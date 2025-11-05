using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using Microsoft.Win32;
using System.Runtime.Versioning;
using System.Text;

namespace DeployForge.Core.Services;

/// <summary>
/// Service for managing offline registry hives
/// </summary>
[SupportedOSPlatform("windows")]
public class RegistryService : IRegistryService
{
    private readonly ILogger<RegistryService> _logger;
    private readonly Dictionary<string, RegistryTweakPreset> _presets;

    public RegistryService(ILogger<RegistryService> logger)
    {
        _logger = logger;
        _presets = InitializePresets();
    }

    public async Task<OperationResult> LoadHiveAsync(
        LoadHiveRequest request,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                // Determine hive file path
                string hivePath = request.HiveType switch
                {
                    RegistryHiveType.Software => Path.Combine(request.MountPath, "Windows", "System32", "config", "SOFTWARE"),
                    RegistryHiveType.System => Path.Combine(request.MountPath, "Windows", "System32", "config", "SYSTEM"),
                    RegistryHiveType.DefaultUser => Path.Combine(request.MountPath, "Windows", "System32", "config", "DEFAULT"),
                    RegistryHiveType.User => Path.Combine(request.MountPath, "Users", "Default", "NTUSER.DAT"),
                    RegistryHiveType.Custom => request.CustomHivePath ?? throw new ArgumentException("Custom hive path required"),
                    _ => throw new ArgumentException($"Unknown hive type: {request.HiveType}")
                };

                if (!File.Exists(hivePath))
                {
                    return OperationResult.FailureResult($"Hive file not found: {hivePath}");
                }

                _logger.LogInformation("Loading registry hive {HivePath} to {MountPoint}", hivePath, request.MountPoint);

                // Use reg.exe to load the hive
                var processStartInfo = new System.Diagnostics.ProcessStartInfo
                {
                    FileName = "reg.exe",
                    Arguments = $"load \"{request.MountPoint}\" \"{hivePath}\"",
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };

                using var process = System.Diagnostics.Process.Start(processStartInfo);
                if (process == null)
                {
                    return OperationResult.FailureResult("Failed to start reg.exe process");
                }

                process.WaitForExit();

                if (process.ExitCode == 0)
                {
                    _logger.LogInformation("Successfully loaded hive to {MountPoint}", request.MountPoint);
                    return OperationResult.SuccessResult();
                }
                else
                {
                    var error = process.StandardError.ReadToEnd();
                    return OperationResult.FailureResult($"Failed to load hive: {error}");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to load registry hive");
                return OperationResult.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult> UnloadHiveAsync(
        string mountPoint,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                _logger.LogInformation("Unloading registry hive from {MountPoint}", mountPoint);

                var processStartInfo = new System.Diagnostics.ProcessStartInfo
                {
                    FileName = "reg.exe",
                    Arguments = $"unload \"{mountPoint}\"",
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };

                using var process = System.Diagnostics.Process.Start(processStartInfo);
                if (process == null)
                {
                    return OperationResult.FailureResult("Failed to start reg.exe process");
                }

                process.WaitForExit();

                if (process.ExitCode == 0)
                {
                    _logger.LogInformation("Successfully unloaded hive from {MountPoint}", mountPoint);
                    return OperationResult.SuccessResult();
                }
                else
                {
                    var error = process.StandardError.ReadToEnd();
                    return OperationResult.FailureResult($"Failed to unload hive: {error}");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to unload registry hive");
                return OperationResult.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<RegistryKeyInfo>> GetKeyInfoAsync(
        string keyPath,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                using var key = OpenRegistryKey(keyPath, false);
                if (key == null)
                {
                    return OperationResult<RegistryKeyInfo>.FailureResult($"Key not found: {keyPath}");
                }

                var info = new RegistryKeyInfo
                {
                    Path = keyPath,
                    Name = key.Name.Split('\\').Last(),
                    ParentPath = string.Join("\\", keyPath.Split('\\').SkipLast(1)),
                    SubKeyCount = key.GetSubKeyNames().Length,
                    ValueCount = key.GetValueNames().Length
                };

                return OperationResult<RegistryKeyInfo>.SuccessResult(info);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get key info for {KeyPath}", keyPath);
                return OperationResult<RegistryKeyInfo>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<List<RegistryValueInfo>>> GetValuesAsync(
        string keyPath,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                using var key = OpenRegistryKey(keyPath, false);
                if (key == null)
                {
                    return OperationResult<List<RegistryValueInfo>>.FailureResult($"Key not found: {keyPath}");
                }

                var values = new List<RegistryValueInfo>();
                foreach (var valueName in key.GetValueNames())
                {
                    var kind = key.GetValueKind(valueName);
                    var data = key.GetValue(valueName);

                    values.Add(new RegistryValueInfo
                    {
                        Name = valueName,
                        Type = MapRegistryKind(kind),
                        Data = data,
                        DataString = FormatRegistryData(data, kind),
                        KeyPath = keyPath
                    });
                }

                return OperationResult<List<RegistryValueInfo>>.SuccessResult(values);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get values for {KeyPath}", keyPath);
                return OperationResult<List<RegistryValueInfo>>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<List<string>>> GetSubKeysAsync(
        string keyPath,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                using var key = OpenRegistryKey(keyPath, false);
                if (key == null)
                {
                    return OperationResult<List<string>>.FailureResult($"Key not found: {keyPath}");
                }

                var subKeys = key.GetSubKeyNames().ToList();
                return OperationResult<List<string>>.SuccessResult(subKeys);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get subkeys for {KeyPath}", keyPath);
                return OperationResult<List<string>>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult> SetValueAsync(
        SetRegistryValueRequest request,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var fullPath = request.KeyPath.StartsWith(request.MountPoint)
                    ? request.KeyPath
                    : Path.Combine(request.MountPoint, request.KeyPath);

                using var key = OpenRegistryKey(fullPath, true);
                if (key == null)
                {
                    return OperationResult.FailureResult($"Failed to open key: {fullPath}");
                }

                var kind = MapToRegistryValueKind(request.ValueType);
                key.SetValue(request.ValueName, request.Data ?? string.Empty, kind);

                _logger.LogInformation("Set registry value {KeyPath}\\{ValueName} = {Data}",
                    fullPath, request.ValueName, request.Data);

                return OperationResult.SuccessResult();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set registry value");
                return OperationResult.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult> DeleteAsync(
        DeleteRegistryRequest request,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var fullPath = request.KeyPath.StartsWith(request.MountPoint)
                    ? request.KeyPath
                    : Path.Combine(request.MountPoint, request.KeyPath);

                if (string.IsNullOrEmpty(request.ValueName))
                {
                    // Delete entire key
                    var parentPath = string.Join("\\", fullPath.Split('\\').SkipLast(1));
                    var keyName = fullPath.Split('\\').Last();

                    using var parentKey = OpenRegistryKey(parentPath, true);
                    if (parentKey == null)
                    {
                        return OperationResult.FailureResult($"Parent key not found: {parentPath}");
                    }

                    if (request.Recursive)
                    {
                        parentKey.DeleteSubKeyTree(keyName);
                    }
                    else
                    {
                        parentKey.DeleteSubKey(keyName);
                    }

                    _logger.LogInformation("Deleted registry key {KeyPath}", fullPath);
                }
                else
                {
                    // Delete value
                    using var key = OpenRegistryKey(fullPath, true);
                    if (key == null)
                    {
                        return OperationResult.FailureResult($"Key not found: {fullPath}");
                    }

                    key.DeleteValue(request.ValueName);
                    _logger.LogInformation("Deleted registry value {KeyPath}\\{ValueName}",
                        fullPath, request.ValueName);
                }

                return OperationResult.SuccessResult();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to delete registry key/value");
                return OperationResult.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult> ImportRegFileAsync(
        ImportRegFileRequest request,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                if (!File.Exists(request.RegFilePath))
                {
                    return OperationResult.FailureResult($"Reg file not found: {request.RegFilePath}");
                }

                _logger.LogInformation("Importing .reg file {RegFilePath}", request.RegFilePath);

                // This is a simplified implementation
                // In production, you would parse the .reg file and apply changes
                var processStartInfo = new System.Diagnostics.ProcessStartInfo
                {
                    FileName = "reg.exe",
                    Arguments = $"import \"{request.RegFilePath}\"",
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };

                using var process = System.Diagnostics.Process.Start(processStartInfo);
                if (process == null)
                {
                    return OperationResult.FailureResult("Failed to start reg.exe process");
                }

                process.WaitForExit();

                if (process.ExitCode == 0)
                {
                    return OperationResult.SuccessResult();
                }
                else
                {
                    var error = process.StandardError.ReadToEnd();
                    return OperationResult.FailureResult($"Failed to import .reg file: {error}");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to import .reg file");
                return OperationResult.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult> ExportRegFileAsync(
        ExportRegFileRequest request,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                _logger.LogInformation("Exporting registry keys to {OutputPath}", request.OutputPath);

                var sb = new StringBuilder();
                sb.AppendLine("Windows Registry Editor Version 5.00");
                sb.AppendLine();

                foreach (var keyPath in request.KeyPaths)
                {
                    ExportKey(keyPath, sb);
                }

                File.WriteAllText(request.OutputPath, sb.ToString());
                return OperationResult.SuccessResult();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to export .reg file");
                return OperationResult.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult> ApplyTweakPresetAsync(
        string mountPath,
        RegistryTweakPreset preset,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(async () =>
        {
            try
            {
                _logger.LogInformation("Applying registry tweak preset: {PresetName}", preset.Name);

                var loadedHives = new Dictionary<RegistryHiveType, string>();

                // Load required hives
                var requiredHives = preset.Tweaks.Select(t => t.HiveType).Distinct();
                foreach (var hiveType in requiredHives)
                {
                    var mountPoint = $"HKLM\\DeployForge_{hiveType}_{Guid.NewGuid():N}";
                    var loadResult = await LoadHiveAsync(new LoadHiveRequest
                    {
                        MountPath = mountPath,
                        HiveType = hiveType,
                        MountPoint = mountPoint
                    }, cancellationToken);

                    if (loadResult.Success)
                    {
                        loadedHives[hiveType] = mountPoint;
                    }
                }

                // Apply tweaks
                foreach (var tweak in preset.Tweaks)
                {
                    if (!loadedHives.TryGetValue(tweak.HiveType, out var mountPoint))
                    {
                        _logger.LogWarning("Hive not loaded for tweak: {Description}", tweak.Description);
                        continue;
                    }

                    await SetValueAsync(new SetRegistryValueRequest
                    {
                        MountPoint = mountPoint,
                        KeyPath = tweak.KeyPath,
                        ValueName = tweak.ValueName,
                        ValueType = tweak.ValueType,
                        Data = tweak.Data
                    }, cancellationToken);
                }

                // Unload hives
                foreach (var mountPoint in loadedHives.Values)
                {
                    await UnloadHiveAsync(mountPoint, cancellationToken);
                }

                _logger.LogInformation("Successfully applied preset: {PresetName}", preset.Name);
                return OperationResult.SuccessResult();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to apply tweak preset");
                return OperationResult.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<List<RegistryTweakPreset>>> GetTweakPresetsAsync(
        string? category = null,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var presets = _presets.Values.ToList();

                if (!string.IsNullOrEmpty(category))
                {
                    presets = presets.Where(p =>
                        p.Category.Equals(category, StringComparison.OrdinalIgnoreCase)).ToList();
                }

                return OperationResult<List<RegistryTweakPreset>>.SuccessResult(presets);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get tweak presets");
                return OperationResult<List<RegistryTweakPreset>>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    #region Private Helper Methods

    private RegistryKey? OpenRegistryKey(string path, bool writable)
    {
        // Parse the path to get the hive and subkey
        var parts = path.Split('\\', 2);
        if (parts.Length < 2) return null;

        var hive = parts[0].ToUpperInvariant() switch
        {
            "HKEY_LOCAL_MACHINE" or "HKLM" => Registry.LocalMachine,
            "HKEY_CURRENT_USER" or "HKCU" => Registry.CurrentUser,
            "HKEY_CLASSES_ROOT" or "HKCR" => Registry.ClassesRoot,
            "HKEY_USERS" or "HKU" => Registry.Users,
            _ => null
        };

        if (hive == null) return null;

        try
        {
            if (writable)
            {
                return hive.CreateSubKey(parts[1], true);
            }
            else
            {
                return hive.OpenSubKey(parts[1], false);
            }
        }
        catch
        {
            return null;
        }
    }

    private void ExportKey(string keyPath, StringBuilder sb)
    {
        using var key = OpenRegistryKey(keyPath, false);
        if (key == null) return;

        sb.AppendLine($"[{keyPath}]");

        foreach (var valueName in key.GetValueNames())
        {
            var kind = key.GetValueKind(valueName);
            var data = key.GetValue(valueName);
            sb.AppendLine($"\"{valueName}\"={FormatRegistryDataForExport(data, kind)}");
        }

        sb.AppendLine();
    }

    private string FormatRegistryData(object? data, RegistryValueKind kind)
    {
        if (data == null) return string.Empty;

        return kind switch
        {
            RegistryValueKind.DWord => ((int)data).ToString(),
            RegistryValueKind.QWord => ((long)data).ToString(),
            RegistryValueKind.MultiString => string.Join(", ", (string[])data),
            RegistryValueKind.Binary => BitConverter.ToString((byte[])data).Replace("-", " "),
            _ => data.ToString() ?? string.Empty
        };
    }

    private string FormatRegistryDataForExport(object? data, RegistryValueKind kind)
    {
        if (data == null) return "\"\"";

        return kind switch
        {
            RegistryValueKind.DWord => $"dword:{(int)data:x8}",
            RegistryValueKind.String => $"\"{data}\"",
            _ => $"\"{data}\""
        };
    }

    private RegistryValueType MapRegistryKind(RegistryValueKind kind)
    {
        return kind switch
        {
            RegistryValueKind.String => RegistryValueType.String,
            RegistryValueKind.ExpandString => RegistryValueType.ExpandString,
            RegistryValueKind.Binary => RegistryValueType.Binary,
            RegistryValueKind.DWord => RegistryValueType.DWord,
            RegistryValueKind.QWord => RegistryValueType.QWord,
            RegistryValueKind.MultiString => RegistryValueType.MultiString,
            _ => RegistryValueType.Unknown
        };
    }

    private RegistryValueKind MapToRegistryValueKind(RegistryValueType type)
    {
        return type switch
        {
            RegistryValueType.String => RegistryValueKind.String,
            RegistryValueType.ExpandString => RegistryValueKind.ExpandString,
            RegistryValueType.Binary => RegistryValueKind.Binary,
            RegistryValueType.DWord => RegistryValueKind.DWord,
            RegistryValueType.QWord => RegistryValueKind.QWord,
            RegistryValueType.MultiString => RegistryValueKind.MultiString,
            _ => RegistryValueKind.String
        };
    }

    private Dictionary<string, RegistryTweakPreset> InitializePresets()
    {
        return new Dictionary<string, RegistryTweakPreset>
        {
            ["disable-telemetry"] = new RegistryTweakPreset
            {
                Name = "Disable Telemetry",
                Description = "Disable Windows telemetry and data collection",
                Category = "Privacy",
                Tweaks = new List<RegistryTweak>
                {
                    new() { HiveType = RegistryHiveType.Software, KeyPath = "Policies\\Microsoft\\Windows\\DataCollection",
                        ValueName = "AllowTelemetry", ValueType = RegistryValueType.DWord, Data = 0,
                        Description = "Disable telemetry completely" },
                    new() { HiveType = RegistryHiveType.Software, KeyPath = "Policies\\Microsoft\\Windows\\DataCollection",
                        ValueName = "DoNotShowFeedbackNotifications", ValueType = RegistryValueType.DWord, Data = 1,
                        Description = "Disable feedback notifications" }
                }
            },
            ["gaming-performance"] = new RegistryTweakPreset
            {
                Name = "Gaming Performance",
                Description = "Optimize Windows for gaming performance",
                Category = "Gaming",
                Tweaks = new List<RegistryTweak>
                {
                    new() { HiveType = RegistryHiveType.System, KeyPath = "CurrentControlSet\\Control\\PriorityControl",
                        ValueName = "Win32PrioritySeparation", ValueType = RegistryValueType.DWord, Data = 38,
                        Description = "Optimize CPU scheduling for games" },
                    new() { HiveType = RegistryHiveType.Software, KeyPath = "Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile",
                        ValueName = "SystemResponsiveness", ValueType = RegistryValueType.DWord, Data = 0,
                        Description = "Minimize background tasks during gaming" }
                }
            }
        };
    }

    #endregion
}
