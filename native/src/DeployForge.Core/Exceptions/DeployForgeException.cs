namespace DeployForge.Core.Exceptions;

/// <summary>
/// Base exception for all DeployForge operations.
/// </summary>
public class DeployForgeException : Exception
{
    /// <summary>
    /// The operation that caused the exception.
    /// </summary>
    public string Operation { get; }
    
    /// <summary>
    /// Additional details about the error.
    /// </summary>
    public string Details { get; }

    public DeployForgeException(string message) 
        : base(message)
    {
        Operation = "Unknown";
        Details = string.Empty;
    }

    public DeployForgeException(string message, string operation) 
        : base(message)
    {
        Operation = operation;
        Details = string.Empty;
    }

    public DeployForgeException(string message, string operation, string details) 
        : base(message)
    {
        Operation = operation;
        Details = details;
    }

    public DeployForgeException(string message, Exception innerException) 
        : base(message, innerException)
    {
        Operation = "Unknown";
        Details = string.Empty;
    }

    public DeployForgeException(string message, string operation, Exception innerException) 
        : base(message, innerException)
    {
        Operation = operation;
        Details = string.Empty;
    }
}

/// <summary>
/// Thrown when an image file cannot be found.
/// </summary>
public class ImageNotFoundException : DeployForgeException
{
    /// <summary>
    /// Path to the image that was not found.
    /// </summary>
    public string ImagePath { get; }

    public ImageNotFoundException(string imagePath)
        : base($"Image not found: {imagePath}", "ImageLoad")
    {
        ImagePath = imagePath;
    }

    public ImageNotFoundException(string imagePath, Exception innerException)
        : base($"Image not found: {imagePath}", "ImageLoad", innerException)
    {
        ImagePath = imagePath;
    }
}

/// <summary>
/// Thrown when mounting or unmounting an image fails.
/// </summary>
public class MountException : DeployForgeException
{
    /// <summary>
    /// The mount path that failed.
    /// </summary>
    public string MountPath { get; }

    public MountException(string message, string mountPath)
        : base(message, "Mount")
    {
        MountPath = mountPath;
    }

    public MountException(string message, string mountPath, Exception innerException)
        : base(message, "Mount", innerException)
    {
        MountPath = mountPath;
    }
}

/// <summary>
/// Thrown when a registry operation fails.
/// </summary>
public class RegistryException : DeployForgeException
{
    /// <summary>
    /// The registry hive.
    /// </summary>
    public string Hive { get; }
    
    /// <summary>
    /// The registry path.
    /// </summary>
    public string Path { get; }

    public RegistryException(string message, string hive, string path)
        : base(message, "Registry")
    {
        Hive = hive;
        Path = path;
    }

    public RegistryException(string message, string hive, string path, Exception innerException)
        : base(message, "Registry", innerException)
    {
        Hive = hive;
        Path = path;
    }
}

/// <summary>
/// Thrown when input validation fails.
/// </summary>
public class ValidationException : DeployForgeException
{
    /// <summary>
    /// The parameter that failed validation.
    /// </summary>
    public string ParameterName { get; }
    
    /// <summary>
    /// The invalid value.
    /// </summary>
    public object? InvalidValue { get; }

    public ValidationException(string message, string parameterName)
        : base(message, "Validation")
    {
        ParameterName = parameterName;
        InvalidValue = null;
    }

    public ValidationException(string message, string parameterName, object? invalidValue)
        : base(message, "Validation")
    {
        ParameterName = parameterName;
        InvalidValue = invalidValue;
    }
}

/// <summary>
/// Thrown when a DISM operation fails.
/// </summary>
public class DismException : DeployForgeException
{
    /// <summary>
    /// The DISM exit code.
    /// </summary>
    public int ExitCode { get; }
    
    /// <summary>
    /// The DISM output.
    /// </summary>
    public string DismOutput { get; }

    public DismException(string message, int exitCode, string dismOutput)
        : base(message, "DISM")
    {
        ExitCode = exitCode;
        DismOutput = dismOutput;
    }
}

/// <summary>
/// Thrown when a PowerShell script execution fails.
/// </summary>
public class PowerShellException : DeployForgeException
{
    /// <summary>
    /// The script that failed.
    /// </summary>
    public string Script { get; }
    
    /// <summary>
    /// PowerShell error output.
    /// </summary>
    public string ErrorOutput { get; }

    public PowerShellException(string message, string script, string errorOutput)
        : base(message, "PowerShell")
    {
        Script = script;
        ErrorOutput = errorOutput;
    }

    public PowerShellException(string message, string script, Exception innerException)
        : base(message, "PowerShell", innerException)
    {
        Script = script;
        ErrorOutput = innerException.Message;
    }
}

/// <summary>
/// Thrown when an unsupported image format is encountered.
/// </summary>
public class UnsupportedFormatException : DeployForgeException
{
    /// <summary>
    /// The unsupported format.
    /// </summary>
    public string Format { get; }

    public UnsupportedFormatException(string format)
        : base($"Unsupported image format: {format}", "ImageLoad")
    {
        Format = format;
    }
}
