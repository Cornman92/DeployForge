using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using Microsoft.Extensions.Logging;

namespace DeployForge.Desktop.Services;

/// <summary>
/// API client implementation
/// </summary>
public class ApiClient : IApiClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<ApiClient> _logger;
    private readonly JsonSerializerOptions _jsonOptions;

    public string BaseUrl
    {
        get => _httpClient.BaseAddress?.ToString() ?? string.Empty;
        set => _httpClient.BaseAddress = new Uri(value);
    }

    public ApiClient(ILogger<ApiClient> logger)
    {
        _httpClient = new HttpClient
        {
            BaseAddress = new Uri("http://localhost:5000/api/"),
            Timeout = TimeSpan.FromMinutes(10)
        };

        _logger = logger;

        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true,
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        };
    }

    public async Task<T?> GetAsync<T>(string endpoint, CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogDebug("GET {Endpoint}", endpoint);

            var response = await _httpClient.GetAsync(endpoint, cancellationToken);
            response.EnsureSuccessStatusCode();

            var result = await response.Content.ReadFromJsonAsync<T>(_jsonOptions, cancellationToken);
            return result;
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "HTTP error during GET {Endpoint}", endpoint);
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during GET {Endpoint}", endpoint);
            throw;
        }
    }

    public async Task<TResponse?> PostAsync<TRequest, TResponse>(
        string endpoint,
        TRequest data,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogDebug("POST {Endpoint}", endpoint);

            var response = await _httpClient.PostAsJsonAsync(endpoint, data, _jsonOptions, cancellationToken);
            response.EnsureSuccessStatusCode();

            var result = await response.Content.ReadFromJsonAsync<TResponse>(_jsonOptions, cancellationToken);
            return result;
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "HTTP error during POST {Endpoint}", endpoint);
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during POST {Endpoint}", endpoint);
            throw;
        }
    }

    public async Task<bool> DeleteAsync(string endpoint, CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogDebug("DELETE {Endpoint}", endpoint);

            var response = await _httpClient.DeleteAsync(endpoint, cancellationToken);
            response.EnsureSuccessStatusCode();

            return true;
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "HTTP error during DELETE {Endpoint}", endpoint);
            return false;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during DELETE {Endpoint}", endpoint);
            return false;
        }
    }

    public async Task<bool> TestConnectionAsync()
    {
        try
        {
            var response = await _httpClient.GetAsync("health");
            return response.IsSuccessStatusCode;
        }
        catch
        {
            return false;
        }
    }
}
