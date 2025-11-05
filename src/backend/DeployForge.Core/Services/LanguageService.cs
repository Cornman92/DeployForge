using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using DeployForge.DismEngine;
using System.Runtime.Versioning;
using System.Xml.Linq;

namespace DeployForge.Core.Services;

/// <summary>
/// Service for managing language packs
/// </summary>
[SupportedOSPlatform("windows")]
public class LanguageService : ILanguageService
{
    private readonly DismManager _dismManager;
    private readonly ILogger<LanguageService> _logger;

    public LanguageService(DismManager dismManager, ILogger<LanguageService> logger)
    {
        _dismManager = dismManager;
        _logger = logger;
    }

    public async Task<OperationResult<List<LanguagePackInfo>>> GetLanguagePacksAsync(
        string mountPath,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                _logger.LogInformation("Getting language packs from {MountPath}", mountPath);

                // Get packages that are language packs
                var packagesResult = _dismManager.GetPackages(mountPath);

                if (!packagesResult.Success || packagesResult.Data == null)
                {
                    return OperationResult<List<LanguagePackInfo>>.FailureResult(
                        packagesResult.ErrorMessage ?? "Failed to get packages");
                }

                var languagePacks = new List<LanguagePackInfo>();

                foreach (var package in packagesResult.Data)
                {
                    // Language packs typically have "Language-Pack" or "LanguageFeatures" in the name
                    if (package.PackageName.Contains("LanguagePack", StringComparison.OrdinalIgnoreCase) ||
                        package.PackageName.Contains("LanguageFeatures", StringComparison.OrdinalIgnoreCase))
                    {
                        var languageTag = ExtractLanguageTag(package.PackageName);

                        languagePacks.Add(new LanguagePackInfo
                        {
                            LanguageTag = languageTag,
                            DisplayName = GetLanguageDisplayName(languageTag),
                            NativeName = GetLanguageNativeName(languageTag),
                            PackageName = package.PackageName,
                            State = MapPackageStateToLanguageState(package.PackageState),
                            InstallDate = package.InstallTime == DateTime.MinValue ? null : package.InstallTime
                        });
                    }
                }

                _logger.LogInformation("Found {Count} language packs", languagePacks.Count);

                return OperationResult<List<LanguagePackInfo>>.SuccessResult(languagePacks);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get language packs");
                return OperationResult<List<LanguagePackInfo>>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<LanguageOperationResult>> AddLanguagePacksAsync(
        AddLanguagePackRequest request,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            var result = new LanguageOperationResult();
            var successful = new List<string>();
            var failed = new List<LanguageOperationError>();

            try
            {
                _logger.LogInformation("Adding {Count} language packs to {MountPath}",
                    request.LanguagePackPaths.Count, request.MountPath);

                foreach (var packPath in request.LanguagePackPaths)
                {
                    if (cancellationToken.IsCancellationRequested)
                        break;

                    if (!File.Exists(packPath))
                    {
                        failed.Add(new LanguageOperationError
                        {
                            LanguageTag = Path.GetFileName(packPath),
                            ErrorMessage = "File not found"
                        });
                        continue;
                    }

                    var addResult = _dismManager.AddPackage(request.MountPath, packPath, false);

                    if (addResult.Success)
                    {
                        var languageTag = ExtractLanguageTag(Path.GetFileName(packPath));
                        successful.Add(languageTag);
                        _logger.LogInformation("Successfully added language pack: {LanguageTag}", languageTag);
                    }
                    else
                    {
                        failed.Add(new LanguageOperationError
                        {
                            LanguageTag = Path.GetFileName(packPath),
                            ErrorMessage = addResult.ErrorMessage ?? "Unknown error"
                        });
                        _logger.LogWarning("Failed to add language pack {Path}: {Error}",
                            packPath, addResult.ErrorMessage);
                    }
                }

                // Install FOD packages if requested
                if (request.InstallFOD && request.FODPaths.Any())
                {
                    _logger.LogInformation("Installing {Count} FOD packages", request.FODPaths.Count);

                    foreach (var fodPath in request.FODPaths)
                    {
                        if (cancellationToken.IsCancellationRequested)
                            break;

                        if (File.Exists(fodPath))
                        {
                            _dismManager.AddPackage(request.MountPath, fodPath, false);
                        }
                    }
                }

                result.SuccessfulLanguages = successful;
                result.FailedLanguages = failed;
                result.TotalProcessed = successful.Count + failed.Count;
                result.Success = successful.Count > 0;
                result.Message = $"Added {successful.Count} of {result.TotalProcessed} language packs";

                return OperationResult<LanguageOperationResult>.SuccessResult(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to add language packs");
                return OperationResult<LanguageOperationResult>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<LanguageOperationResult>> RemoveLanguagePacksAsync(
        RemoveLanguagePackRequest request,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            var result = new LanguageOperationResult();
            var successful = new List<string>();
            var failed = new List<LanguageOperationError>();

            try
            {
                _logger.LogInformation("Removing {Count} language packs from {MountPath}",
                    request.LanguageTags.Count, request.MountPath);

                // Get all packages
                var packagesResult = _dismManager.GetPackages(request.MountPath);

                if (!packagesResult.Success || packagesResult.Data == null)
                {
                    return OperationResult<LanguageOperationResult>.FailureResult(
                        "Failed to get packages");
                }

                foreach (var languageTag in request.LanguageTags)
                {
                    if (cancellationToken.IsCancellationRequested)
                        break;

                    // Find packages matching this language tag
                    var matchingPackages = packagesResult.Data
                        .Where(p => p.PackageName.Contains(languageTag, StringComparison.OrdinalIgnoreCase))
                        .ToList();

                    bool anySuccess = false;

                    foreach (var package in matchingPackages)
                    {
                        var removeResult = _dismManager.RemovePackage(request.MountPath, package.PackageName);

                        if (removeResult.Success)
                        {
                            anySuccess = true;
                            _logger.LogInformation("Successfully removed package: {PackageName}", package.PackageName);
                        }
                        else
                        {
                            _logger.LogWarning("Failed to remove package {PackageName}: {Error}",
                                package.PackageName, removeResult.ErrorMessage);
                        }
                    }

                    if (anySuccess)
                    {
                        successful.Add(languageTag);
                    }
                    else
                    {
                        failed.Add(new LanguageOperationError
                        {
                            LanguageTag = languageTag,
                            ErrorMessage = "No packages found or removal failed"
                        });
                    }
                }

                result.SuccessfulLanguages = successful;
                result.FailedLanguages = failed;
                result.TotalProcessed = successful.Count + failed.Count;
                result.Success = successful.Count > 0;
                result.Message = $"Removed {successful.Count} of {result.TotalProcessed} language packs";

                return OperationResult<LanguageOperationResult>.SuccessResult(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to remove language packs");
                return OperationResult<LanguageOperationResult>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult> SetDefaultLanguagesAsync(
        SetDefaultLanguagesRequest request,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                _logger.LogInformation("Setting default languages for {MountPath}", request.MountPath);

                // Setting default languages requires modifying registry hives
                // This is a simplified implementation
                // In production, you would:
                // 1. Load SYSTEM hive
                // 2. Modify Control Panel\International settings
                // 3. Set UILanguage, SystemLocale, UserLocale, InputLocale
                // 4. Unload hive

                _logger.LogInformation("Default UI Language: {UILanguage}", request.UILanguage);
                _logger.LogInformation("System Locale: {SystemLocale}", request.SystemLocale);
                _logger.LogInformation("User Locale: {UserLocale}", request.UserLocale);
                _logger.LogInformation("Input Locale: {InputLocale}", request.InputLocale);

                // Placeholder - actual implementation would modify registry
                return OperationResult.SuccessResult();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set default languages");
                return OperationResult.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<SetDefaultLanguagesRequest>> GetDefaultLanguagesAsync(
        string mountPath,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                _logger.LogInformation("Getting default languages from {MountPath}", mountPath);

                // This would read from registry hives
                // Placeholder implementation
                var defaults = new SetDefaultLanguagesRequest
                {
                    MountPath = mountPath,
                    UILanguage = "en-US",
                    SystemLocale = "en-US",
                    UserLocale = "en-US",
                    InputLocale = "0409:00000409"
                };

                return OperationResult<SetDefaultLanguagesRequest>.SuccessResult(defaults);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get default languages");
                return OperationResult<SetDefaultLanguagesRequest>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    #region Private Helper Methods

    private string ExtractLanguageTag(string packageName)
    {
        // Language packs typically have format: Microsoft-Windows-LanguagePack-en-US-...
        // Or: LanguageFeatures-Basic-en-us-Package

        var parts = packageName.Split('-', '_');

        foreach (var part in parts)
        {
            // Look for xx-XX pattern (e.g., en-US, es-ES)
            if (part.Length == 5 && part[2] == '-')
            {
                return part;
            }
            // Look for xx_XX pattern
            if (part.Length == 5 && part[2] == '_')
            {
                return part.Replace('_', '-');
            }
        }

        return "Unknown";
    }

    private string GetLanguageDisplayName(string languageTag)
    {
        // Simple mapping - in production, use CultureInfo
        return languageTag.ToLowerInvariant() switch
        {
            "en-us" => "English (United States)",
            "en-gb" => "English (United Kingdom)",
            "es-es" => "Spanish (Spain)",
            "es-mx" => "Spanish (Mexico)",
            "fr-fr" => "French (France)",
            "de-de" => "German (Germany)",
            "it-it" => "Italian (Italy)",
            "pt-br" => "Portuguese (Brazil)",
            "pt-pt" => "Portuguese (Portugal)",
            "ja-jp" => "Japanese (Japan)",
            "ko-kr" => "Korean (Korea)",
            "zh-cn" => "Chinese (Simplified)",
            "zh-tw" => "Chinese (Traditional)",
            "ru-ru" => "Russian (Russia)",
            "ar-sa" => "Arabic (Saudi Arabia)",
            _ => languageTag
        };
    }

    private string GetLanguageNativeName(string languageTag)
    {
        // Simple mapping - in production, use CultureInfo
        return languageTag.ToLowerInvariant() switch
        {
            "en-us" => "English",
            "es-es" => "Español",
            "fr-fr" => "Français",
            "de-de" => "Deutsch",
            "it-it" => "Italiano",
            "pt-br" => "Português",
            "ja-jp" => "日本語",
            "ko-kr" => "한국어",
            "zh-cn" => "中文（简体）",
            "zh-tw" => "中文（繁體）",
            "ru-ru" => "Русский",
            "ar-sa" => "العربية",
            _ => languageTag
        };
    }

    private LanguagePackState MapPackageStateToLanguageState(Microsoft.Dism.DismPackageFeatureState state)
    {
        return state switch
        {
            Microsoft.Dism.DismPackageFeatureState.Installed => LanguagePackState.Installed,
            Microsoft.Dism.DismPackageFeatureState.Staged => LanguagePackState.PartiallyInstalled,
            Microsoft.Dism.DismPackageFeatureState.InstallPending => LanguagePackState.InstallPending,
            _ => LanguagePackState.NotInstalled
        };
    }

    #endregion
}
