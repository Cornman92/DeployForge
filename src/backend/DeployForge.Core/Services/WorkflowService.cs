using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using System.Runtime.Versioning;

namespace DeployForge.Core.Services;

/// <summary>
/// Service for managing and executing workflows
/// </summary>
[SupportedOSPlatform("windows")]
public class WorkflowService : IWorkflowService
{
    private readonly IComponentService _componentService;
    private readonly IDriverService _driverService;
    private readonly IUpdateService _updateService;
    private readonly IRegistryService _registryService;
    private readonly IDebloatService _debloatService;
    private readonly ILogger<WorkflowService> _logger;
    private readonly Dictionary<string, WorkflowDefinition> _templates;

    public WorkflowService(
        IComponentService componentService,
        IDriverService driverService,
        IUpdateService updateService,
        IRegistryService registryService,
        IDebloatService debloatService,
        ILogger<WorkflowService> logger)
    {
        _componentService = componentService;
        _driverService = driverService;
        _updateService = updateService;
        _registryService = registryService;
        _debloatService = debloatService;
        _logger = logger;
        _templates = InitializeTemplates();
    }

    public async Task<OperationResult<List<string>>> ValidateWorkflowAsync(
        WorkflowDefinition workflow,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            var errors = new List<string>();

            try
            {
                // Basic validation
                if (string.IsNullOrWhiteSpace(workflow.Name))
                {
                    errors.Add("Workflow name is required");
                }

                if (workflow.Steps == null || workflow.Steps.Count == 0)
                {
                    errors.Add("Workflow must have at least one step");
                }

                // Validate step IDs are unique
                var stepIds = workflow.Steps.Select(s => s.Id).ToList();
                var duplicates = stepIds.GroupBy(id => id)
                    .Where(g => g.Count() > 1)
                    .Select(g => g.Key)
                    .ToList();

                if (duplicates.Any())
                {
                    errors.Add($"Duplicate step IDs found: {string.Join(", ", duplicates)}");
                }

                // Validate dependencies
                foreach (var step in workflow.Steps)
                {
                    foreach (var dependency in step.DependsOn)
                    {
                        if (!stepIds.Contains(dependency))
                        {
                            errors.Add($"Step '{step.Id}' depends on unknown step '{dependency}'");
                        }
                    }
                }

                // Check for circular dependencies (simplified)
                var visited = new HashSet<string>();
                var recursionStack = new HashSet<string>();

                foreach (var step in workflow.Steps)
                {
                    if (HasCircularDependency(step.Id, workflow.Steps, visited, recursionStack))
                    {
                        errors.Add($"Circular dependency detected involving step '{step.Id}'");
                    }
                }

                _logger.LogInformation("Workflow validation completed. Errors: {ErrorCount}", errors.Count);

                return OperationResult<List<string>>.SuccessResult(errors);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to validate workflow");
                return OperationResult<List<string>>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<WorkflowExecutionResult>> ExecuteWorkflowAsync(
        ExecuteWorkflowRequest request,
        CancellationToken cancellationToken = default)
    {
        var result = new WorkflowExecutionResult
        {
            WorkflowId = request.Workflow.Id,
            StartTime = DateTime.UtcNow
        };

        try
        {
            _logger.LogInformation("Starting workflow execution: {WorkflowName}", request.Workflow.Name);

            // Validate workflow
            var validationResult = await ValidateWorkflowAsync(request.Workflow, cancellationToken);
            if (validationResult.Success && validationResult.Data != null && validationResult.Data.Any())
            {
                result.Success = false;
                result.Errors = validationResult.Data;
                result.Message = "Workflow validation failed";
                result.EndTime = DateTime.UtcNow;
                return OperationResult<WorkflowExecutionResult>.SuccessResult(result);
            }

            // Merge variables
            var variables = new Dictionary<string, string>(request.Workflow.Variables);
            foreach (var kvp in request.Variables)
            {
                variables[kvp.Key] = kvp.Value;
            }

            // Add built-in variables
            variables["ImagePath"] = request.ImagePath;
            variables["MountPath"] = request.MountPath;

            if (request.DryRun)
            {
                result.Success = true;
                result.Message = "Dry run completed - workflow is valid";
                result.EndTime = DateTime.UtcNow;
                return OperationResult<WorkflowExecutionResult>.SuccessResult(result);
            }

            // Execute steps in dependency order
            var executedSteps = new HashSet<string>();
            var stepQueue = new Queue<WorkflowStep>();

            // Find steps with no dependencies
            foreach (var step in request.Workflow.Steps.Where(s => !s.DependsOn.Any()))
            {
                stepQueue.Enqueue(step);
            }

            while (stepQueue.Count > 0)
            {
                if (cancellationToken.IsCancellationRequested)
                {
                    result.Message = "Workflow execution cancelled";
                    break;
                }

                var step = stepQueue.Dequeue();

                // Check if dependencies are met
                if (step.DependsOn.Any(dep => !executedSteps.Contains(dep)))
                {
                    // Re-queue if dependencies not met
                    stepQueue.Enqueue(step);
                    continue;
                }

                // Execute step
                var stepResult = await ExecuteStepAsync(step, request.MountPath, variables, cancellationToken);
                result.StepResults.Add(stepResult);
                executedSteps.Add(step.Id);

                // Handle step failure
                if (stepResult.Status == StepStatus.Failed && !step.ContinueOnError)
                {
                    result.Success = false;
                    result.Errors.Add($"Step '{step.Name}' failed: {stepResult.ErrorMessage}");
                    result.Message = "Workflow execution failed";
                    break;
                }

                // Queue dependent steps
                foreach (var dependentStep in request.Workflow.Steps.Where(s => s.DependsOn.Contains(step.Id)))
                {
                    if (!executedSteps.Contains(dependentStep.Id) && !stepQueue.Contains(dependentStep))
                    {
                        stepQueue.Enqueue(dependentStep);
                    }
                }
            }

            result.EndTime = DateTime.UtcNow;
            result.Success = result.StepResults.All(r => r.Status != StepStatus.Failed);
            result.Message = result.Success
                ? $"Workflow completed successfully. Executed {result.StepResults.Count} steps in {result.Duration.TotalSeconds:F1} seconds"
                : "Workflow completed with errors";

            _logger.LogInformation("Workflow execution completed. Success: {Success}, Steps: {StepCount}, Duration: {Duration}s",
                result.Success, result.StepResults.Count, result.Duration.TotalSeconds);

            return OperationResult<WorkflowExecutionResult>.SuccessResult(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Workflow execution failed");
            result.EndTime = DateTime.UtcNow;
            result.Success = false;
            result.Errors.Add(ex.Message);
            return OperationResult<WorkflowExecutionResult>.ExceptionResult(ex);
        }
    }

    public async Task<OperationResult<List<WorkflowDefinition>>> GetTemplatesAsync(
        string? tag = null,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var templates = _templates.Values.ToList();

                if (!string.IsNullOrEmpty(tag))
                {
                    templates = templates.Where(t =>
                        t.Tags.Any(tg => tg.Equals(tag, StringComparison.OrdinalIgnoreCase))).ToList();
                }

                return OperationResult<List<WorkflowDefinition>>.SuccessResult(templates);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get workflow templates");
                return OperationResult<List<WorkflowDefinition>>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<WorkflowDefinition>> GetTemplateAsync(
        string templateId,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                if (!_templates.TryGetValue(templateId, out var template))
                {
                    return OperationResult<WorkflowDefinition>.FailureResult($"Template not found: {templateId}");
                }

                return OperationResult<WorkflowDefinition>.SuccessResult(template);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get workflow template");
                return OperationResult<WorkflowDefinition>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    #region Private Helper Methods

    private async Task<WorkflowStepResult> ExecuteStepAsync(
        WorkflowStep step,
        string mountPath,
        Dictionary<string, string> variables,
        CancellationToken cancellationToken)
    {
        var stepResult = new WorkflowStepResult
        {
            StepId = step.Id,
            StepName = step.Name,
            StartTime = DateTime.UtcNow,
            Status = StepStatus.Running
        };

        try
        {
            _logger.LogInformation("Executing step: {StepName} ({StepType})", step.Name, step.Type);

            // Check conditions
            if (!EvaluateConditions(step.Conditions, variables))
            {
                stepResult.Status = StepStatus.Skipped;
                stepResult.Message = "Step skipped due to conditions";
                stepResult.EndTime = DateTime.UtcNow;
                return stepResult;
            }

            // Execute based on type
            var success = step.Type switch
            {
                WorkflowStepType.RemoveComponents => await ExecuteRemoveComponentsAsync(step, mountPath, cancellationToken),
                WorkflowStepType.InstallUpdates => await ExecuteInstallUpdatesAsync(step, mountPath, cancellationToken),
                WorkflowStepType.AddDrivers => await ExecuteAddDriversAsync(step, mountPath, cancellationToken),
                WorkflowStepType.ApplyRegistryTweaks => await ExecuteApplyRegistryTweaksAsync(step, mountPath, cancellationToken),
                WorkflowStepType.ApplyDebloat => await ExecuteApplyDebloatAsync(step, mountPath, cancellationToken),
                WorkflowStepType.Cleanup => await ExecuteCleanupAsync(step, mountPath, cancellationToken),
                _ => throw new NotImplementedException($"Step type {step.Type} not implemented")
            };

            stepResult.Status = success ? StepStatus.Completed : StepStatus.Failed;
            stepResult.Message = success ? "Step completed successfully" : "Step failed";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Step execution failed: {StepName}", step.Name);
            stepResult.Status = StepStatus.Failed;
            stepResult.ErrorMessage = ex.Message;
        }

        stepResult.EndTime = DateTime.UtcNow;
        return stepResult;
    }

    private async Task<bool> ExecuteRemoveComponentsAsync(WorkflowStep step, string mountPath, CancellationToken cancellationToken)
    {
        if (!step.Configuration.TryGetValue("componentIds", out var componentIdsObj))
            return false;

        var componentIds = (componentIdsObj as List<object>)?.Select(o => o.ToString() ?? string.Empty).ToList() ?? new List<string>();

        var result = await _componentService.RemoveComponentsAsync(new ComponentOperationRequest
        {
            MountPath = mountPath,
            ComponentIds = componentIds
        }, cancellationToken);

        return result.Success;
    }

    private async Task<bool> ExecuteInstallUpdatesAsync(WorkflowStep step, string mountPath, CancellationToken cancellationToken)
    {
        if (!step.Configuration.TryGetValue("updatePaths", out var updatePathsObj))
            return false;

        var updatePaths = (updatePathsObj as List<object>)?.Select(o => o.ToString() ?? string.Empty).ToList() ?? new List<string>();

        var result = await _updateService.InstallUpdatesAsync(new UpdateOperationRequest
        {
            MountPath = mountPath,
            UpdatePaths = updatePaths
        }, cancellationToken);

        return result.Success;
    }

    private async Task<bool> ExecuteAddDriversAsync(WorkflowStep step, string mountPath, CancellationToken cancellationToken)
    {
        if (!step.Configuration.TryGetValue("driverPaths", out var driverPathsObj))
            return false;

        var driverPaths = (driverPathsObj as List<object>)?.Select(o => o.ToString() ?? string.Empty).ToList() ?? new List<string>();

        var result = await _driverService.AddDriversAsync(new DriverOperationRequest
        {
            MountPath = mountPath,
            Drivers = driverPaths
        }, cancellationToken);

        return result.Success;
    }

    private async Task<bool> ExecuteApplyRegistryTweaksAsync(WorkflowStep step, string mountPath, CancellationToken cancellationToken)
    {
        if (!step.Configuration.TryGetValue("presetName", out var presetNameObj))
            return false;

        var presetName = presetNameObj.ToString() ?? string.Empty;
        var presetsResult = await _registryService.GetTweakPresetsAsync(null, cancellationToken);

        if (!presetsResult.Success || presetsResult.Data == null)
            return false;

        var preset = presetsResult.Data.FirstOrDefault(p => p.Name.Equals(presetName, StringComparison.OrdinalIgnoreCase));
        if (preset == null)
            return false;

        var result = await _registryService.ApplyTweakPresetAsync(mountPath, preset, cancellationToken);
        return result.Success;
    }

    private async Task<bool> ExecuteApplyDebloatAsync(WorkflowStep step, string mountPath, CancellationToken cancellationToken)
    {
        if (!step.Configuration.TryGetValue("presetId", out var presetIdObj))
            return false;

        var presetId = presetIdObj.ToString() ?? string.Empty;

        var result = await _debloatService.ApplyPresetAsync(new ApplyDebloatRequest
        {
            MountPath = mountPath,
            PresetId = presetId,
            DryRun = false
        }, cancellationToken);

        return result.Success;
    }

    private async Task<bool> ExecuteCleanupAsync(WorkflowStep step, string mountPath, CancellationToken cancellationToken)
    {
        var result = await _updateService.CleanupSupersededAsync(mountPath, cancellationToken);
        return result.Success;
    }

    private bool EvaluateConditions(List<WorkflowCondition> conditions, Dictionary<string, string> variables)
    {
        if (conditions == null || conditions.Count == 0)
            return true;

        return conditions.All(condition =>
        {
            if (condition.Type == ConditionType.Always)
                return true;

            if (condition.Type == ConditionType.Variable)
            {
                if (!variables.TryGetValue(condition.Variable, out var value))
                    return false;

                return condition.Operator switch
                {
                    ConditionOperator.Equals => value.Equals(condition.Value, StringComparison.OrdinalIgnoreCase),
                    ConditionOperator.NotEquals => !value.Equals(condition.Value, StringComparison.OrdinalIgnoreCase),
                    ConditionOperator.Contains => value.Contains(condition.Value, StringComparison.OrdinalIgnoreCase),
                    _ => false
                };
            }

            return false;
        });
    }

    private bool HasCircularDependency(
        string stepId,
        List<WorkflowStep> steps,
        HashSet<string> visited,
        HashSet<string> recursionStack)
    {
        if (recursionStack.Contains(stepId))
            return true;

        if (visited.Contains(stepId))
            return false;

        visited.Add(stepId);
        recursionStack.Add(stepId);

        var step = steps.FirstOrDefault(s => s.Id == stepId);
        if (step != null)
        {
            foreach (var dependency in step.DependsOn)
            {
                if (HasCircularDependency(dependency, steps, visited, recursionStack))
                    return true;
            }
        }

        recursionStack.Remove(stepId);
        return false;
    }

    private Dictionary<string, WorkflowDefinition> InitializeTemplates()
    {
        return new Dictionary<string, WorkflowDefinition>
        {
            ["gaming-optimized"] = new WorkflowDefinition
            {
                Id = "gaming-optimized",
                Name = "Gaming Optimized Windows",
                Description = "Create a gaming-optimized Windows image with bloat removed and performance tweaks applied",
                Author = "DeployForge Team",
                Tags = new List<string> { "gaming", "performance", "debloat" },
                Steps = new List<WorkflowStep>
                {
                    new()
                    {
                        Id = "debloat",
                        Name = "Remove Bloatware",
                        Description = "Apply moderate debloat preset",
                        Type = WorkflowStepType.ApplyDebloat,
                        Configuration = new Dictionary<string, object>
                        {
                            ["presetId"] = "moderate"
                        }
                    },
                    new()
                    {
                        Id = "registry-tweaks",
                        Name = "Apply Gaming Tweaks",
                        Description = "Apply gaming performance registry tweaks",
                        Type = WorkflowStepType.ApplyRegistryTweaks,
                        Configuration = new Dictionary<string, object>
                        {
                            ["presetName"] = "Gaming Performance"
                        },
                        DependsOn = new List<string> { "debloat" }
                    },
                    new()
                    {
                        Id = "cleanup",
                        Name = "Cleanup Image",
                        Description = "Remove superseded components",
                        Type = WorkflowStepType.Cleanup,
                        DependsOn = new List<string> { "registry-tweaks" }
                    }
                }
            },

            ["minimal-install"] = new WorkflowDefinition
            {
                Id = "minimal-install",
                Name = "Minimal Windows Installation",
                Description = "Create a minimal Windows image with maximum bloat removal",
                Author = "DeployForge Team",
                Tags = new List<string> { "minimal", "debloat", "privacy" },
                Steps = new List<WorkflowStep>
                {
                    new()
                    {
                        Id = "aggressive-debloat",
                        Name = "Aggressive Debloat",
                        Description = "Apply aggressive debloat preset",
                        Type = WorkflowStepType.ApplyDebloat,
                        Configuration = new Dictionary<string, object>
                        {
                            ["presetId"] = "aggressive"
                        }
                    },
                    new()
                    {
                        Id = "privacy-tweaks",
                        Name = "Privacy Tweaks",
                        Description = "Apply privacy registry tweaks",
                        Type = WorkflowStepType.ApplyRegistryTweaks,
                        Configuration = new Dictionary<string, object>
                        {
                            ["presetName"] = "Disable Telemetry"
                        },
                        DependsOn = new List<string> { "aggressive-debloat" }
                    },
                    new()
                    {
                        Id = "cleanup",
                        Name = "Cleanup Image",
                        Description = "Remove superseded components",
                        Type = WorkflowStepType.Cleanup,
                        DependsOn = new List<string> { "privacy-tweaks" }
                    }
                }
            },

            ["enterprise-deployment"] = new WorkflowDefinition
            {
                Id = "enterprise-deployment",
                Name = "Enterprise Deployment Image",
                Description = "Create an enterprise-ready Windows image with updates and drivers",
                Author = "DeployForge Team",
                Tags = new List<string> { "enterprise", "deployment", "drivers" },
                Steps = new List<WorkflowStep>
                {
                    new()
                    {
                        Id = "conservative-debloat",
                        Name = "Remove Obvious Bloat",
                        Description = "Apply conservative debloat preset",
                        Type = WorkflowStepType.ApplyDebloat,
                        Configuration = new Dictionary<string, object>
                        {
                            ["presetId"] = "conservative"
                        }
                    },
                    new()
                    {
                        Id = "cleanup",
                        Name = "Cleanup Image",
                        Description = "Remove superseded components",
                        Type = WorkflowStepType.Cleanup,
                        DependsOn = new List<string> { "conservative-debloat" }
                    }
                }
            }
        };
    }

    #endregion
}
