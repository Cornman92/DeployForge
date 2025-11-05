namespace DeployForge.Common.Models;

/// <summary>
/// Language pack information
/// </summary>
public class LanguagePackInfo
{
    /// <summary>
    /// Language tag (e.g., en-US, es-ES)
    /// </summary>
    public string LanguageTag { get; set; } = string.Empty;

    /// <summary>
    /// Display name
    /// </summary>
    public string DisplayName { get; set; } = string.Empty;

    /// <summary>
    /// Native name
    /// </summary>
    public string NativeName { get; set; } = string.Empty;

    /// <summary>
    /// Package name
    /// </summary>
    public string PackageName { get; set; } = string.Empty;

    /// <summary>
    /// Installation state
    /// </summary>
    public LanguagePackState State { get; set; }

    /// <summary>
    /// Package size in bytes
    /// </summary>
    public long SizeBytes { get; set; }

    /// <summary>
    /// Is this the default system language
    /// </summary>
    public bool IsDefault { get; set; }

    /// <summary>
    /// Install date
    /// </summary>
    public DateTime? InstallDate { get; set; }

    /// <summary>
    /// Features included (FOD - Features on Demand)
    /// </summary>
    public List<string> Features { get; set; } = new();
}

/// <summary>
/// Language pack installation states
/// </summary>
public enum LanguagePackState
{
    /// <summary>
    /// Not installed
    /// </summary>
    NotInstalled,

    /// <summary>
    /// Partially installed
    /// </summary>
    PartiallyInstalled,

    /// <summary>
    /// Fully installed
    /// </summary>
    Installed,

    /// <summary>
    /// Installation pending
    /// </summary>
    InstallPending
}

/// <summary>
/// Request to add language packs
/// </summary>
public class AddLanguagePackRequest
{
    /// <summary>
    /// Path to mounted image
    /// </summary>
    public string MountPath { get; set; } = string.Empty;

    /// <summary>
    /// Paths to language pack cab files
    /// </summary>
    public List<string> LanguagePackPaths { get; set; } = new();

    /// <summary>
    /// Install language Features on Demand (FOD)
    /// </summary>
    public bool InstallFOD { get; set; } = true;

    /// <summary>
    /// FOD package paths
    /// </summary>
    public List<string> FODPaths { get; set; } = new();
}

/// <summary>
/// Request to remove language packs
/// </summary>
public class RemoveLanguagePackRequest
{
    /// <summary>
    /// Path to mounted image
    /// </summary>
    public string MountPath { get; set; } = string.Empty;

    /// <summary>
    /// Language tags to remove
    /// </summary>
    public List<string> LanguageTags { get; set; } = new();
}

/// <summary>
/// Request to set default languages
/// </summary>
public class SetDefaultLanguagesRequest
{
    /// <summary>
    /// Path to mounted image
    /// </summary>
    public string MountPath { get; set; } = string.Empty;

    /// <summary>
    /// Default UI language
    /// </summary>
    public string UILanguage { get; set; } = "en-US";

    /// <summary>
    /// Default system locale
    /// </summary>
    public string SystemLocale { get; set; } = "en-US";

    /// <summary>
    /// Default user locale
    /// </summary>
    public string UserLocale { get; set; } = "en-US";

    /// <summary>
    /// Default input locale (keyboard)
    /// </summary>
    public string InputLocale { get; set; } = "0409:00000409"; // en-US keyboard

    /// <summary>
    /// Fallback languages
    /// </summary>
    public List<string> FallbackLanguages { get; set; } = new();
}

/// <summary>
/// Language operation result
/// </summary>
public class LanguageOperationResult
{
    /// <summary>
    /// Whether operation succeeded
    /// </summary>
    public bool Success { get; set; }

    /// <summary>
    /// Languages successfully processed
    /// </summary>
    public List<string> SuccessfulLanguages { get; set; } = new();

    /// <summary>
    /// Languages that failed
    /// </summary>
    public List<LanguageOperationError> FailedLanguages { get; set; } = new();

    /// <summary>
    /// Total processed
    /// </summary>
    public int TotalProcessed { get; set; }

    /// <summary>
    /// Message
    /// </summary>
    public string Message { get; set; } = string.Empty;
}

/// <summary>
/// Language operation error
/// </summary>
public class LanguageOperationError
{
    public string LanguageTag { get; set; } = string.Empty;
    public string ErrorMessage { get; set; } = string.Empty;
}

/// <summary>
/// Language Features on Demand types
/// </summary>
public enum LanguageFODType
{
    /// <summary>
    /// Basic typing (fonts)
    /// </summary>
    BasicTyping,

    /// <summary>
    /// Handwriting recognition
    /// </summary>
    Handwriting,

    /// <summary>
    /// Optical character recognition
    /// </summary>
    OCR,

    /// <summary>
    /// Speech recognition
    /// </summary>
    Speech,

    /// <summary>
    /// Text-to-speech
    /// </summary>
    TextToSpeech,

    /// <summary>
    /// Local experience packs
    /// </summary>
    LocalExperiencePack
}
