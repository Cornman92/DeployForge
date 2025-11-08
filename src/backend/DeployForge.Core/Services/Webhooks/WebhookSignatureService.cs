using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Logging;

namespace DeployForge.Core.Services.Webhooks;

/// <summary>
/// Service for generating and verifying HMAC-SHA256 webhook signatures
/// with timestamp-based replay attack protection
/// </summary>
public interface IWebhookSignatureService
{
    /// <summary>
    /// Generates a secure HMAC-SHA256 signature for a webhook payload
    /// </summary>
    /// <param name="payload">The payload to sign (will be serialized to JSON)</param>
    /// <param name="secret">The shared secret key</param>
    /// <param name="timestamp">Optional timestamp (UTC). If not provided, current time is used.</param>
    /// <returns>Signature details including signature, timestamp, and version</returns>
    WebhookSignature GenerateSignature(object payload, string secret, DateTimeOffset? timestamp = null);

    /// <summary>
    /// Generates a secure HMAC-SHA256 signature for a JSON string payload
    /// </summary>
    /// <param name="payloadJson">The JSON payload to sign</param>
    /// <param name="secret">The shared secret key</param>
    /// <param name="timestamp">Optional timestamp (UTC). If not provided, current time is used.</param>
    /// <returns>Signature details including signature, timestamp, and version</returns>
    WebhookSignature GenerateSignature(string payloadJson, string secret, DateTimeOffset? timestamp = null);

    /// <summary>
    /// Verifies a webhook signature
    /// </summary>
    /// <param name="payloadJson">The received JSON payload</param>
    /// <param name="signature">The received signature</param>
    /// <param name="timestamp">The received timestamp (Unix seconds)</param>
    /// <param name="secret">The shared secret key</param>
    /// <param name="maxAgeSeconds">Maximum age of the request in seconds (default: 300 = 5 minutes)</param>
    /// <returns>True if signature is valid and timestamp is within acceptable range</returns>
    WebhookVerificationResult VerifySignature(
        string payloadJson,
        string signature,
        long timestamp,
        string secret,
        int maxAgeSeconds = 300);

    /// <summary>
    /// Generates a new cryptographically secure webhook secret
    /// </summary>
    /// <param name="length">Length of the secret in bytes (default: 32)</param>
    /// <returns>Base64-encoded secret</returns>
    string GenerateSecret(int length = 32);
}

/// <summary>
/// Webhook signature details
/// </summary>
public class WebhookSignature
{
    /// <summary>
    /// HMAC-SHA256 signature (Base64-encoded)
    /// </summary>
    public string Signature { get; set; } = string.Empty;

    /// <summary>
    /// Unix timestamp (seconds since epoch)
    /// </summary>
    public long Timestamp { get; set; }

    /// <summary>
    /// Signature scheme version (default: v1)
    /// </summary>
    public string Version { get; set; } = "v1";

    /// <summary>
    /// Full signature string for X-DeployForge-Signature header
    /// Format: v1,{timestamp},{signature}
    /// </summary>
    public string FullSignature => $"{Version},{Timestamp},{Signature}";
}

/// <summary>
/// Webhook verification result
/// </summary>
public class WebhookVerificationResult
{
    /// <summary>
    /// Whether the signature is valid
    /// </summary>
    public bool IsValid { get; set; }

    /// <summary>
    /// Error message if validation failed
    /// </summary>
    public string? ErrorMessage { get; set; }

    /// <summary>
    /// Age of the request in seconds
    /// </summary>
    public double? AgeSeconds { get; set; }

    /// <summary>
    /// Success result
    /// </summary>
    public static WebhookVerificationResult Success(double ageSeconds) => new()
    {
        IsValid = true,
        AgeSeconds = ageSeconds
    };

    /// <summary>
    /// Failure result
    /// </summary>
    public static WebhookVerificationResult Failure(string errorMessage) => new()
    {
        IsValid = false,
        ErrorMessage = errorMessage
    };
}

/// <summary>
/// Implementation of webhook signature service
/// </summary>
public class WebhookSignatureService : IWebhookSignatureService
{
    private readonly ILogger<WebhookSignatureService> _logger;

    public WebhookSignatureService(ILogger<WebhookSignatureService> logger)
    {
        _logger = logger;
    }

    /// <summary>
    /// Generates a secure HMAC-SHA256 signature for a webhook payload
    /// </summary>
    public WebhookSignature GenerateSignature(object payload, string secret, DateTimeOffset? timestamp = null)
    {
        var payloadJson = JsonSerializer.Serialize(payload);
        return GenerateSignature(payloadJson, secret, timestamp);
    }

    /// <summary>
    /// Generates a secure HMAC-SHA256 signature for a JSON string payload
    /// </summary>
    public WebhookSignature GenerateSignature(string payloadJson, string secret, DateTimeOffset? timestamp = null)
    {
        if (string.IsNullOrEmpty(secret))
        {
            throw new ArgumentException("Secret cannot be null or empty", nameof(secret));
        }

        var ts = timestamp ?? DateTimeOffset.UtcNow;
        var unixTimestamp = ts.ToUnixTimeSeconds();

        // Construct the string to sign: timestamp.payload
        var stringToSign = $"{unixTimestamp}.{payloadJson}";

        // Compute HMAC-SHA256
        using var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(secret));
        var hash = hmac.ComputeHash(Encoding.UTF8.GetBytes(stringToSign));
        var signature = Convert.ToBase64String(hash);

        _logger.LogDebug("Generated webhook signature for timestamp {Timestamp}", unixTimestamp);

        return new WebhookSignature
        {
            Signature = signature,
            Timestamp = unixTimestamp,
            Version = "v1"
        };
    }

    /// <summary>
    /// Verifies a webhook signature
    /// </summary>
    public WebhookVerificationResult VerifySignature(
        string payloadJson,
        string signature,
        long timestamp,
        string secret,
        int maxAgeSeconds = 300)
    {
        try
        {
            if (string.IsNullOrEmpty(payloadJson))
            {
                return WebhookVerificationResult.Failure("Payload cannot be null or empty");
            }

            if (string.IsNullOrEmpty(signature))
            {
                return WebhookVerificationResult.Failure("Signature cannot be null or empty");
            }

            if (string.IsNullOrEmpty(secret))
            {
                return WebhookVerificationResult.Failure("Secret cannot be null or empty");
            }

            // Check timestamp age (replay attack protection)
            var requestTime = DateTimeOffset.FromUnixTimeSeconds(timestamp);
            var now = DateTimeOffset.UtcNow;
            var age = (now - requestTime).TotalSeconds;

            if (age < 0)
            {
                _logger.LogWarning("Webhook timestamp is in the future by {Seconds} seconds", Math.Abs(age));
                return WebhookVerificationResult.Failure("Request timestamp is in the future");
            }

            if (age > maxAgeSeconds)
            {
                _logger.LogWarning("Webhook timestamp is too old: {Age} seconds (max: {Max})", age, maxAgeSeconds);
                return WebhookVerificationResult.Failure($"Request is too old ({age:F0} seconds, max: {maxAgeSeconds})");
            }

            // Reconstruct the expected signature
            var stringToSign = $"{timestamp}.{payloadJson}";
            using var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(secret));
            var hash = hmac.ComputeHash(Encoding.UTF8.GetBytes(stringToSign));
            var expectedSignature = Convert.ToBase64String(hash);

            // Constant-time comparison to prevent timing attacks
            if (!ConstantTimeEquals(signature, expectedSignature))
            {
                _logger.LogWarning("Webhook signature verification failed");
                return WebhookVerificationResult.Failure("Invalid signature");
            }

            _logger.LogDebug("Webhook signature verified successfully (age: {Age} seconds)", age);
            return WebhookVerificationResult.Success(age);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error verifying webhook signature");
            return WebhookVerificationResult.Failure($"Verification error: {ex.Message}");
        }
    }

    /// <summary>
    /// Generates a new cryptographically secure webhook secret
    /// </summary>
    public string GenerateSecret(int length = 32)
    {
        if (length < 16)
        {
            throw new ArgumentException("Secret length must be at least 16 bytes", nameof(length));
        }

        var randomBytes = new byte[length];
        using var rng = RandomNumberGenerator.Create();
        rng.GetBytes(randomBytes);
        return Convert.ToBase64String(randomBytes);
    }

    /// <summary>
    /// Constant-time string comparison to prevent timing attacks
    /// </summary>
    private static bool ConstantTimeEquals(string a, string b)
    {
        if (a.Length != b.Length)
        {
            return false;
        }

        var result = 0;
        for (int i = 0; i < a.Length; i++)
        {
            result |= a[i] ^ b[i];
        }

        return result == 0;
    }
}
