# Webhook Signature Verification Guide

## Overview

DeployForge uses HMAC-SHA256 signatures with timestamp-based replay protection to secure webhook payloads. This ensures that webhook requests are authentic and haven't been tampered with or replayed by attackers.

## Security Features

✅ **HMAC-SHA256 Signatures** - Industry-standard cryptographic signing
✅ **Timestamp-Based Replay Protection** - Prevents replay attacks
✅ **Constant-Time Comparison** - Prevents timing attacks
✅ **Secret Rotation Support** - Automatic secret rotation with grace period
✅ **Configurable Expiration** - Customizable webhook age limits

## Webhook Headers

DeployForge sends the following headers with each webhook request:

| Header | Description | Example |
|--------|-------------|---------|
| `X-DeployForge-Signature` | Full signature string (v1,timestamp,signature) | `v1,1704729600,dGVzdA==` |
| `X-DeployForge-Timestamp` | Unix timestamp (seconds since epoch) | `1704729600` |
| `Content-Type` | Always `application/json` | `application/json` |

## Signature Format

The `X-DeployForge-Signature` header contains three components separated by commas:

```
v1,{timestamp},{signature}
```

- **v1**: Signature scheme version
- **{timestamp}**: Unix timestamp (seconds since epoch)
- **{signature}**: Base64-encoded HMAC-SHA256 signature

**Example**:
```
X-DeployForge-Signature: v1,1704729600,dGVzdA==
X-DeployForge-Timestamp: 1704729600
```

## Signature Generation Algorithm

To verify a webhook signature, you need to:

1. **Extract components** from the `X-DeployForge-Signature` header
2. **Construct the signed string**: `{timestamp}.{raw_json_payload}`
3. **Compute HMAC-SHA256** using your webhook secret
4. **Compare signatures** using constant-time comparison
5. **Verify timestamp** is within acceptable range (default: 5 minutes)

## Verification Examples

### Node.js / JavaScript

```javascript
const crypto = require('crypto');

function verifyWebhookSignature(payload, signature, timestamp, secret, maxAgeSeconds = 300) {
    // Parse signature components
    const [version, ts, sig] = signature.split(',');

    if (version !== 'v1') {
        throw new Error('Unsupported signature version');
    }

    // Check timestamp age (replay protection)
    const now = Math.floor(Date.now() / 1000);
    const age = now - parseInt(timestamp);

    if (age < 0) {
        throw new Error('Request timestamp is in the future');
    }

    if (age > maxAgeSeconds) {
        throw new Error(`Request is too old (${age} seconds, max: ${maxAgeSeconds})`);
    }

    // Construct the string to sign
    const stringToSign = `${timestamp}.${payload}`;

    // Compute expected signature
    const expectedSignature = crypto
        .createHmac('sha256', secret)
        .update(stringToSign)
        .digest('base64');

    // Constant-time comparison
    if (sig !== expectedSignature) {
        throw new Error('Invalid signature');
    }

    return true;
}

// Usage
app.post('/webhook', (req, res) => {
    const signature = req.headers['x-deployforge-signature'];
    const timestamp = req.headers['x-deployforge-timestamp'];
    const payload = JSON.stringify(req.body);
    const secret = process.env.WEBHOOK_SECRET;

    try {
        verifyWebhookSignature(payload, signature, timestamp, secret);
        console.log('Webhook verified successfully');

        // Process webhook...

        res.status(200).send('OK');
    } catch (error) {
        console.error('Webhook verification failed:', error.message);
        res.status(401).send('Unauthorized');
    }
});
```

### Python

```python
import hmac
import hashlib
import time
import base64
import json

def verify_webhook_signature(payload, signature, timestamp, secret, max_age_seconds=300):
    """Verify DeployForge webhook signature"""

    # Parse signature components
    parts = signature.split(',')
    if len(parts) != 3:
        raise ValueError('Invalid signature format')

    version, ts, sig = parts

    if version != 'v1':
        raise ValueError('Unsupported signature version')

    # Check timestamp age (replay protection)
    now = int(time.time())
    age = now - int(timestamp)

    if age < 0:
        raise ValueError('Request timestamp is in the future')

    if age > max_age_seconds:
        raise ValueError(f'Request is too old ({age} seconds, max: {max_age_seconds})')

    # Construct the string to sign
    string_to_sign = f"{timestamp}.{payload}"

    # Compute expected signature
    expected_signature = base64.b64encode(
        hmac.new(
            secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')

    # Constant-time comparison
    if not hmac.compare_digest(sig, expected_signature):
        raise ValueError('Invalid signature')

    return True

# Usage with Flask
@app.route('/webhook', methods=['POST'])
def webhook():
    signature = request.headers.get('X-DeployForge-Signature')
    timestamp = request.headers.get('X-DeployForge-Timestamp')
    payload = request.get_data(as_text=True)
    secret = os.environ['WEBHOOK_SECRET']

    try:
        verify_webhook_signature(payload, signature, timestamp, secret)
        print('Webhook verified successfully')

        # Process webhook...
        data = json.loads(payload)

        return 'OK', 200
    except Exception as e:
        print(f'Webhook verification failed: {e}')
        return 'Unauthorized', 401
```

### C# / .NET

```csharp
using System;
using System.Security.Cryptography;
using System.Text;

public class WebhookVerifier
{
    public static bool VerifyWebhookSignature(
        string payload,
        string signature,
        long timestamp,
        string secret,
        int maxAgeSeconds = 300)
    {
        // Parse signature components
        var parts = signature.Split(',');
        if (parts.Length != 3)
        {
            throw new ArgumentException("Invalid signature format");
        }

        var version = parts[0];
        var ts = long.Parse(parts[1]);
        var sig = parts[2];

        if (version != "v1")
        {
            throw new ArgumentException("Unsupported signature version");
        }

        // Check timestamp age (replay protection)
        var now = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
        var age = now - timestamp;

        if (age < 0)
        {
            throw new ArgumentException("Request timestamp is in the future");
        }

        if (age > maxAgeSeconds)
        {
            throw new ArgumentException(
                $"Request is too old ({age} seconds, max: {maxAgeSeconds})");
        }

        // Construct the string to sign
        var stringToSign = $"{timestamp}.{payload}";

        // Compute expected signature
        using (var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(secret)))
        {
            var hash = hmac.ComputeHash(Encoding.UTF8.GetBytes(stringToSign));
            var expectedSignature = Convert.ToBase64String(hash);

            // Constant-time comparison
            if (!ConstantTimeEquals(sig, expectedSignature))
            {
                throw new ArgumentException("Invalid signature");
            }
        }

        return true;
    }

    private static bool ConstantTimeEquals(string a, string b)
    {
        if (a.Length != b.Length) return false;

        var result = 0;
        for (int i = 0; i < a.Length; i++)
        {
            result |= a[i] ^ b[i];
        }

        return result == 0;
    }
}

// Usage in ASP.NET Core
[HttpPost("webhook")]
public IActionResult Webhook([FromBody] object payload)
{
    var signature = Request.Headers["X-DeployForge-Signature"].ToString();
    var timestamp = long.Parse(Request.Headers["X-DeployForge-Timestamp"].ToString());
    var payloadJson = JsonSerializer.Serialize(payload);
    var secret = Configuration["Webhook:Secret"];

    try
    {
        WebhookVerifier.VerifyWebhookSignature(payloadJson, signature, timestamp, secret);
        _logger.LogInformation("Webhook verified successfully");

        // Process webhook...

        return Ok();
    }
    catch (Exception ex)
    {
        _logger.LogWarning($"Webhook verification failed: {ex.Message}");
        return Unauthorized();
    }
}
```

### Go

```go
package main

import (
    "crypto/hmac"
    "crypto/sha256"
    "crypto/subtle"
    "encoding/base64"
    "errors"
    "fmt"
    "strconv"
    "strings"
    "time"
)

func VerifyWebhookSignature(payload, signature string, timestamp int64, secret string, maxAgeSeconds int) error {
    // Parse signature components
    parts := strings.Split(signature, ",")
    if len(parts) != 3 {
        return errors.New("invalid signature format")
    }

    version, ts, sig := parts[0], parts[1], parts[2]

    if version != "v1" {
        return errors.New("unsupported signature version")
    }

    // Check timestamp age (replay protection)
    now := time.Now().Unix()
    age := now - timestamp

    if age < 0 {
        return errors.New("request timestamp is in the future")
    }

    if age > int64(maxAgeSeconds) {
        return fmt.Errorf("request is too old (%d seconds, max: %d)", age, maxAgeSeconds)
    }

    // Construct the string to sign
    stringToSign := fmt.Sprintf("%d.%s", timestamp, payload)

    // Compute expected signature
    h := hmac.New(sha256.New, []byte(secret))
    h.Write([]byte(stringToSign))
    expectedSignature := base64.StdEncoding.EncodeToString(h.Sum(nil))

    // Constant-time comparison
    if subtle.ConstantTimeCompare([]byte(sig), []byte(expectedSignature)) != 1 {
        return errors.New("invalid signature")
    }

    return nil
}

// Usage
func webhookHandler(w http.ResponseWriter, r *http.Request) {
    signature := r.Header.Get("X-DeployForge-Signature")
    timestampStr := r.Header.Get("X-DeployForge-Timestamp")
    timestamp, _ := strconv.ParseInt(timestampStr, 10, 64)

    body, _ := ioutil.ReadAll(r.Body)
    payload := string(body)
    secret := os.Getenv("WEBHOOK_SECRET")

    if err := VerifyWebhookSignature(payload, signature, timestamp, secret, 300); err != nil {
        log.Printf("Webhook verification failed: %v", err)
        http.Error(w, "Unauthorized", http.StatusUnauthorized)
        return
    }

    log.Println("Webhook verified successfully")

    // Process webhook...

    w.WriteHeader(http.StatusOK)
}
```

## Secret Management

### Generating Secrets

Generate a cryptographically secure secret:

```bash
# Linux/Mac
openssl rand -base64 32

# PowerShell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

### Storing Secrets

**Best Practices:**
- ✅ Store secrets in environment variables or secret management systems
- ✅ Never commit secrets to version control
- ✅ Use different secrets for each environment (dev, staging, production)
- ✅ Rotate secrets regularly (recommended: every 90 days)

### Secret Rotation

Deploy Forge supports secret rotation with a grace period:

1. Generate a new secret
2. Update webhook configuration with new secret
3. Old secret remains valid for grace period (default: 7 days)
4. Update your webhook receiver to use new secret
5. Old secret is automatically invalidated after grace period

**Configuration:**
```json
{
  "webhooks": [
    {
      "id": "webhook-123",
      "name": "My Webhook",
      "url": "https://example.com/webhook",
      "secret": "new_secret_here",
      "previousSecret": "old_secret_here",
      "secretRotationDays": 90,
      "secretRotatedAt": "2025-01-08T00:00:00Z"
    }
  ]
}
```

## Webhook Payload Structure

```json
{
  "eventType": "OperationCompleted",
  "title": "Image Validation Complete",
  "message": "Windows 11 Pro image validated successfully",
  "severity": "Info",
  "timestamp": "2025-01-08T12:00:00Z",
  "details": {
    "imageName": "Windows11_Pro_22H2.wim",
    "duration": "45 seconds",
    "success": true
  },
  "source": "DeployForge",
  "environment": "Production"
}
```

## Security Best Practices

### For Webhook Senders (DeployForge)

✅ Include timestamp in signature
✅ Use HTTPS for all webhook URLs
✅ Rotate secrets regularly
✅ Log signature generation for audit
✅ Implement retry logic with backoff

### For Webhook Receivers

✅ **Always verify signatures** - Never process unverified webhooks
✅ **Check timestamp age** - Reject old requests (5-minute window recommended)
✅ **Use constant-time comparison** - Prevents timing attacks
✅ **Validate payload structure** - Ensure expected fields exist
✅ **Handle errors gracefully** - Return appropriate HTTP status codes
✅ **Implement idempotency** - Handle duplicate webhooks safely
✅ **Use HTTPS** - Encrypt webhook traffic
✅ **Store secrets securely** - Use environment variables or secret management

## Troubleshooting

### Common Errors

**"Invalid signature"**
- Check that you're using the correct secret
- Ensure you're comparing the correct components
- Verify you're using the raw JSON payload (no modifications)
- Check for character encoding issues

**"Request is too old"**
- Check system clock synchronization (NTP)
- Increase `maxAgeSeconds` if needed for high-latency networks
- Ensure webhook receiver processes requests quickly

**"Request timestamp is in the future"**
- Synchronize system clocks using NTP
- Check for timezone issues (timestamps are always UTC)

### Testing

**Generate Test Signature:**

```bash
# Bash
SECRET="your_webhook_secret"
TIMESTAMP=$(date +%s)
PAYLOAD='{"test": "data"}'
SIGNATURE=$(echo -n "${TIMESTAMP}.${PAYLOAD}" | openssl dgst -sha256 -hmac "$SECRET" -binary | base64)
echo "v1,${TIMESTAMP},${SIGNATURE}"
```

**Send Test Webhook:**

```bash
curl -X POST https://your-webhook-receiver.com/webhook \
  -H "Content-Type: application/json" \
  -H "X-DeployForge-Signature: v1,1704729600,dGVzdA==" \
  -H "X-DeployForge-Timestamp: 1704729600" \
  -d '{"test": "data"}'
```

## Support

For questions or issues:
- Check the [Security Audit](./SECURITY_AUDIT_OPTION_B.md) documentation
- Review the [DeployForge documentation](../README.md)
- Open an issue on GitHub

## References

- [HMAC-SHA256 Specification (RFC 2104)](https://tools.ietf.org/html/rfc2104)
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [Webhook Security Best Practices](https://webhooks.fyi/security/overview)

---

**Last Updated**: 2025-01-08
**Version**: 1.0
