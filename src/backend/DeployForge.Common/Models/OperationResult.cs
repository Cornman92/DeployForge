namespace DeployForge.Common.Models;

/// <summary>
/// Represents the result of an operation
/// </summary>
/// <typeparam name="T">The type of data returned</typeparam>
public class OperationResult<T>
{
    /// <summary>
    /// Indicates whether the operation was successful
    /// </summary>
    public bool Success { get; set; }

    /// <summary>
    /// The data returned by the operation
    /// </summary>
    public T? Data { get; set; }

    /// <summary>
    /// Error message if the operation failed
    /// </summary>
    public string? ErrorMessage { get; set; }

    /// <summary>
    /// Exception details if an exception occurred
    /// </summary>
    public string? ExceptionDetails { get; set; }

    /// <summary>
    /// Additional error codes or status
    /// </summary>
    public string? ErrorCode { get; set; }

    /// <summary>
    /// Timestamp of the operation
    /// </summary>
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Creates a successful result
    /// </summary>
    public static OperationResult<T> SuccessResult(T data)
    {
        return new OperationResult<T>
        {
            Success = true,
            Data = data
        };
    }

    /// <summary>
    /// Creates a failed result
    /// </summary>
    public static OperationResult<T> FailureResult(string errorMessage, string? errorCode = null)
    {
        return new OperationResult<T>
        {
            Success = false,
            ErrorMessage = errorMessage,
            ErrorCode = errorCode
        };
    }

    /// <summary>
    /// Creates a failed result from an exception
    /// </summary>
    public static OperationResult<T> ExceptionResult(Exception ex)
    {
        return new OperationResult<T>
        {
            Success = false,
            ErrorMessage = ex.Message,
            ExceptionDetails = ex.ToString()
        };
    }
}

/// <summary>
/// Represents the result of an operation without data
/// </summary>
public class OperationResult : OperationResult<object>
{
    /// <summary>
    /// Creates a successful result
    /// </summary>
    public new static OperationResult SuccessResult()
    {
        return new OperationResult
        {
            Success = true
        };
    }

    /// <summary>
    /// Creates a failed result
    /// </summary>
    public new static OperationResult FailureResult(string errorMessage, string? errorCode = null)
    {
        return new OperationResult
        {
            Success = false,
            ErrorMessage = errorMessage,
            ErrorCode = errorCode
        };
    }

    /// <summary>
    /// Creates a failed result from an exception
    /// </summary>
    public new static OperationResult ExceptionResult(Exception ex)
    {
        return new OperationResult
        {
            Success = false,
            ErrorMessage = ex.Message,
            ExceptionDetails = ex.ToString()
        };
    }
}
