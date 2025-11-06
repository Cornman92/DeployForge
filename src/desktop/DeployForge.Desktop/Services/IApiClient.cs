namespace DeployForge.Desktop.Services;

/// <summary>
/// Interface for API communication
/// </summary>
public interface IApiClient
{
    /// <summary>
    /// Base API URL
    /// </summary>
    string BaseUrl { get; set; }

    /// <summary>
    /// GET request
    /// </summary>
    Task<T?> GetAsync<T>(string endpoint, CancellationToken cancellationToken = default);

    /// <summary>
    /// POST request
    /// </summary>
    Task<TResponse?> PostAsync<TRequest, TResponse>(string endpoint, TRequest data, CancellationToken cancellationToken = default);

    /// <summary>
    /// DELETE request
    /// </summary>
    Task<bool> DeleteAsync(string endpoint, CancellationToken cancellationToken = default);

    /// <summary>
    /// Test API connectivity
    /// </summary>
    Task<bool> TestConnectionAsync();
}
