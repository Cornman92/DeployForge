namespace DeployForge.Common.Models;

/// <summary>
/// Represents a workflow definition
/// </summary>
public class WorkflowDefinition
{
    /// <summary>
    /// Unique workflow identifier
    /// </summary>
    public string Id { get; set; } = string.Empty;

    /// <summary>
    /// Workflow name
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Workflow description
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// Workflow version
    /// </summary>
    public string Version { get; set; } = "1.0.0";

    /// <summary>
    /// Author/creator
    /// </summary>
    public string Author { get; set; } = string.Empty;

    /// <summary>
    /// Creation date
    /// </summary>
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Last modified date
    /// </summary>
    public DateTime? ModifiedAt { get; set; }

    /// <summary>
    /// Workflow steps
    /// </summary>
    public List<WorkflowStep> Steps { get; set; } = new();

    /// <summary>
    /// Variables that can be used throughout the workflow
    /// </summary>
    public Dictionary<string, string> Variables { get; set; } = new();

    /// <summary>
    /// Tags for categorization
    /// </summary>
    public List<string> Tags { get; set; } = new();
}

/// <summary>
/// Individual step in a workflow
/// </summary>
public class WorkflowStep
{
    /// <summary>
    /// Step identifier (unique within workflow)
    /// </summary>
    public string Id { get; set; } = string.Empty;

    /// <summary>
    /// Step name
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Step description
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// Type of operation
    /// </summary>
    public WorkflowStepType Type { get; set; }

    /// <summary>
    /// Step configuration (JSON serialized)
    /// </summary>
    public Dictionary<string, object> Configuration { get; set; } = new();

    /// <summary>
    /// Continue workflow even if this step fails
    /// </summary>
    public bool ContinueOnError { get; set; }

    /// <summary>
    /// Timeout in seconds (0 = no timeout)
    /// </summary>
    public int TimeoutSeconds { get; set; }

    /// <summary>
    /// Conditions that must be met to execute this step
    /// </summary>
    public List<WorkflowCondition> Conditions { get; set; } = new();

    /// <summary>
    /// Steps that depend on this one (executed after)
    /// </summary>
    public List<string> DependsOn { get; set; } = new();
}

/// <summary>
/// Types of workflow steps
/// </summary>
public enum WorkflowStepType
{
    /// <summary>
    /// Mount an image
    /// </summary>
    MountImage,

    /// <summary>
    /// Unmount an image
    /// </summary>
    UnmountImage,

    /// <summary>
    /// Remove components
    /// </summary>
    RemoveComponents,

    /// <summary>
    /// Add components
    /// </summary>
    AddComponents,

    /// <summary>
    /// Install updates
    /// </summary>
    InstallUpdates,

    /// <summary>
    /// Add drivers
    /// </summary>
    AddDrivers,

    /// <summary>
    /// Apply registry tweaks
    /// </summary>
    ApplyRegistryTweaks,

    /// <summary>
    /// Apply debloat preset
    /// </summary>
    ApplyDebloat,

    /// <summary>
    /// Cleanup superseded components
    /// </summary>
    Cleanup,

    /// <summary>
    /// Create ISO
    /// </summary>
    CreateISO,

    /// <summary>
    /// Create bootable USB
    /// </summary>
    CreateBootableUSB,

    /// <summary>
    /// Generate autounattend.xml
    /// </summary>
    GenerateAutounattend,

    /// <summary>
    /// Custom PowerShell script
    /// </summary>
    CustomScript
}

/// <summary>
/// Condition for step execution
/// </summary>
public class WorkflowCondition
{
    /// <summary>
    /// Condition type
    /// </summary>
    public ConditionType Type { get; set; }

    /// <summary>
    /// Variable or property to check
    /// </summary>
    public string Variable { get; set; } = string.Empty;

    /// <summary>
    /// Comparison operator
    /// </summary>
    public ConditionOperator Operator { get; set; }

    /// <summary>
    /// Value to compare against
    /// </summary>
    public string Value { get; set; } = string.Empty;
}

/// <summary>
/// Condition types
/// </summary>
public enum ConditionType
{
    /// <summary>
    /// Check a variable value
    /// </summary>
    Variable,

    /// <summary>
    /// Check previous step result
    /// </summary>
    StepResult,

    /// <summary>
    /// Check file existence
    /// </summary>
    FileExists,

    /// <summary>
    /// Always execute
    /// </summary>
    Always
}

/// <summary>
/// Comparison operators
/// </summary>
public enum ConditionOperator
{
    Equals,
    NotEquals,
    Contains,
    NotContains,
    GreaterThan,
    LessThan
}

/// <summary>
/// Request to execute a workflow
/// </summary>
public class ExecuteWorkflowRequest
{
    /// <summary>
    /// Workflow definition to execute
    /// </summary>
    public WorkflowDefinition Workflow { get; set; } = new();

    /// <summary>
    /// Base image path
    /// </summary>
    public string ImagePath { get; set; } = string.Empty;

    /// <summary>
    /// Mount path for operations
    /// </summary>
    public string MountPath { get; set; } = string.Empty;

    /// <summary>
    /// Override variables
    /// </summary>
    public Dictionary<string, string> Variables { get; set; } = new();

    /// <summary>
    /// Dry run (validate only, don't execute)
    /// </summary>
    public bool DryRun { get; set; }
}

/// <summary>
/// Result of workflow execution
/// </summary>
public class WorkflowExecutionResult
{
    /// <summary>
    /// Overall success
    /// </summary>
    public bool Success { get; set; }

    /// <summary>
    /// Workflow ID
    /// </summary>
    public string WorkflowId { get; set; } = string.Empty;

    /// <summary>
    /// Execution start time
    /// </summary>
    public DateTime StartTime { get; set; }

    /// <summary>
    /// Execution end time
    /// </summary>
    public DateTime EndTime { get; set; }

    /// <summary>
    /// Total duration
    /// </summary>
    public TimeSpan Duration => EndTime - StartTime;

    /// <summary>
    /// Results for each step
    /// </summary>
    public List<WorkflowStepResult> StepResults { get; set; } = new();

    /// <summary>
    /// Overall message
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Any warnings generated
    /// </summary>
    public List<string> Warnings { get; set; } = new();

    /// <summary>
    /// Errors encountered
    /// </summary>
    public List<string> Errors { get; set; } = new();
}

/// <summary>
/// Result of a single workflow step
/// </summary>
public class WorkflowStepResult
{
    /// <summary>
    /// Step ID
    /// </summary>
    public string StepId { get; set; } = string.Empty;

    /// <summary>
    /// Step name
    /// </summary>
    public string StepName { get; set; } = string.Empty;

    /// <summary>
    /// Step status
    /// </summary>
    public StepStatus Status { get; set; }

    /// <summary>
    /// Start time
    /// </summary>
    public DateTime StartTime { get; set; }

    /// <summary>
    /// End time
    /// </summary>
    public DateTime EndTime { get; set; }

    /// <summary>
    /// Duration
    /// </summary>
    public TimeSpan Duration => EndTime - StartTime;

    /// <summary>
    /// Output message
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Error message if failed
    /// </summary>
    public string? ErrorMessage { get; set; }

    /// <summary>
    /// Additional output data
    /// </summary>
    public Dictionary<string, object> OutputData { get; set; } = new();
}

/// <summary>
/// Step execution status
/// </summary>
public enum StepStatus
{
    /// <summary>
    /// Not yet executed
    /// </summary>
    Pending,

    /// <summary>
    /// Currently executing
    /// </summary>
    Running,

    /// <summary>
    /// Completed successfully
    /// </summary>
    Completed,

    /// <summary>
    /// Failed with error
    /// </summary>
    Failed,

    /// <summary>
    /// Skipped due to conditions
    /// </summary>
    Skipped
}
