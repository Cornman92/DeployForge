# Configuration Guide

Advanced configuration options for DeployForge Desktop.

## Table of Contents

1. [Email Configuration](#email-configuration)
2. [Slack Integration](#slack-integration)
3. [Microsoft Teams Integration](#microsoft-teams-integration)
4. [Custom Webhooks](#custom-webhooks)
5. [Alert Threshold Tuning](#alert-threshold-tuning)
6. [Cron Expression Patterns](#cron-expression-patterns)
7. [Performance Optimization](#performance-optimization)
8. [Security Best Practices](#security-best-practices)

---

## Email Configuration

### Gmail Configuration

**Step 1: Enable 2-Factor Authentication**
1. Go to Google Account settings
2. Security > 2-Step Verification
3. Enable 2FA with phone or authenticator app

**Step 2: Generate App Password**
1. Security > App passwords
2. Select app: Mail
3. Select device: Windows Computer
4. Click Generate
5. Copy 16-character password

**Step 3: Configure DeployForge**
```
SMTP Server: smtp.gmail.com
Port: 587
Use SSL/TLS: Yes
Username: your-email@gmail.com
Password: [16-character app password]
From Email: your-email@gmail.com
To Email(s): recipient1@gmail.com, recipient2@gmail.com
```

**Step 4: Test**
- Click "Send Test Email"
- Check recipient inbox (including spam folder)
- Verify message formatting

### Outlook/Office 365 Configuration

```
SMTP Server: smtp.office365.com
Port: 587
Use SSL/TLS: Yes
Username: your-email@outlook.com
Password: [your account password]
From Email: your-email@outlook.com
To Email(s): recipients...
```

**Notes:**
- Modern authentication supported
- May require app-specific password if MFA enabled
- Check Office 365 admin center for SMTP settings

### Custom SMTP Server

```
SMTP Server: mail.yourcompany.com
Port: 587 (or 465 for SSL, 25 for unencrypted)
Use SSL/TLS: Yes (recommended)
Username: smtp-user@yourcompany.com
Password: [service account password]
From Email: deployforge@yourcompany.com
To Email(s): team@yourcompany.com
```

**Firewall Configuration:**
- Allow outbound connections to SMTP server
- Ports: 25 (SMTP), 587 (TLS), 465 (SSL)
- Whitelist server IP if needed

### Email Formatting

DeployForge sends HTML-formatted emails:

**Template Structure:**
```html
<!DOCTYPE html>
<html>
<head>
  <style>
    /* DeployForge branding */
    body { font-family: Arial, sans-serif; }
    .header { background: #2196F3; color: white; }
    .success { color: #4CAF50; }
    .error { color: #F44336; }
  </style>
</head>
<body>
  <div class="header">
    <h1>[DeployForge] Event Title</h1>
  </div>
  <div class="content">
    <p>Message content...</p>
    <table><!-- Event details --></table>
  </div>
</body>
</html>
```

**Customization:**
- Templates stored in `C:\ProgramData\DeployForge\Templates\`
- Modify HTML files to customize appearance
- Variables: `{{title}}`, `{{message}}`, `{{timestamp}}`, `{{severity}}`

---

## Slack Integration

### Creating Slack Webhook

**Step 1: Add Incoming Webhooks App**
1. Go to https://[your-workspace].slack.com/apps
2. Search for "Incoming Webhooks"
3. Click "Add to Slack"
4. Choose channel (e.g., #deployforge, #operations)
5. Click "Add Incoming Webhooks Integration"

**Step 2: Configure Webhook**
1. **Customize Name**: DeployForge Bot
2. **Customize Icon**: Upload DeployForge logo (optional)
3. **Copy Webhook URL**: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX`

**Step 3: Configure DeployForge**
```
Webhook URL: https://hooks.slack.com/services/T.../B.../XXX...
Channel: #deployforge
Username: DeployForge Bot
```

**Step 4: Test**
- Click "Send Test Message"
- Check Slack channel for test message
- Verify formatting and username

### Message Formatting

DeployForge uses Slack's attachment format:

```json
{
  "username": "DeployForge Bot",
  "channel": "#deployforge",
  "attachments": [
    {
      "color": "#36a64f",
      "title": "Operation Completed",
      "text": "Successfully processed 10 images",
      "fields": [
        { "title": "Operation ID", "value": "op-12345", "short": true },
        { "title": "Duration", "value": "5 minutes", "short": true }
      ],
      "footer": "DeployForge",
      "ts": 1609459200
    }
  ]
}
```

**Color Codes:**
- Success: `#36a64f` (green)
- Warning: `#ffaa00` (orange)
- Error: `#ff0000` (red)
- Info: `#2196F3` (blue)

### Advanced Configuration

**Mentions:**
Add to message text:
- User: `<@U1234567>` (get ID from Slack profile)
- Channel: `<!channel>` (mention everyone)
- Here: `<!here>` (mention active users)

**Links:**
Format: `<https://example.com|Link Text>`

**Threading:**
Enable threaded notifications in settings to keep channel clean.

---

## Microsoft Teams Integration

### Creating Teams Webhook

**Step 1: Open Channel Connectors**
1. Navigate to desired Teams channel
2. Click "..." (More options) next to channel name
3. Select "Connectors"

**Step 2: Configure Incoming Webhook**
1. Search for "Incoming Webhook"
2. Click "Configure"
3. Enter name: "DeployForge Notifications"
4. Upload image (optional)
5. Click "Create"
6. **Copy webhook URL**: `https://outlook.office.com/webhook/...`

**Step 3: Configure DeployForge**
```
Webhook URL: https://outlook.office.com/webhook/...
```

**Step 4: Test**
- Click "Send Test Message"
- Check Teams channel
- Verify Adaptive Card rendering

### Adaptive Card Format

DeployForge sends messages as Adaptive Cards:

```json
{
  "type": "message",
  "attachments": [
    {
      "contentType": "application/vnd.microsoft.card.adaptive",
      "contentUrl": null,
      "content": {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": [
          {
            "type": "TextBlock",
            "size": "Large",
            "weight": "Bolder",
            "text": "Operation Completed"
          },
          {
            "type": "TextBlock",
            "text": "Successfully processed 10 images",
            "wrap": true
          },
          {
            "type": "FactSet",
            "facts": [
              { "title": "Operation ID:", "value": "op-12345" },
              { "title": "Duration:", "value": "5 minutes" }
            ]
          }
        ]
      }
    }
  ]
}
```

### Customization

Modify template at: `C:\ProgramData\DeployForge\Templates\teams-adaptive-card.json`

**Card Elements:**
- **TextBlock**: Headers, paragraphs
- **FactSet**: Key-value pairs
- **Image**: Logos, charts
- **ActionSet**: Buttons (e.g., "View Details")

**Theme Colors:**
```json
{
  "success": "#92C353",
  "warning": "#F7B500",
  "error": "#E81123",
  "info": "#0078D7"
}
```

---

## Custom Webhooks

### Webhook Configuration

```
URL: https://api.yourservice.com/webhooks/deployforge
Method: POST
Authorization Header: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Payload Structure

DeployForge sends JSON payload:

```json
{
  "timestamp": "2025-01-08T10:30:00Z",
  "eventType": "OperationCompleted",
  "severity": "Success",
  "title": "Image Processing Complete",
  "message": "Successfully processed 10 images",
  "source": "DeployForge",
  "version": "1.0.0",
  "data": {
    "operationId": "op-12345",
    "operationType": "ImageProcessing",
    "startTime": "2025-01-08T10:25:00Z",
    "endTime": "2025-01-08T10:30:00Z",
    "duration": "PT5M",
    "itemCount": 10,
    "successCount": 10,
    "failureCount": 0,
    "details": {
      "images": [
        "image1.wim",
        "image2.wim"
      ]
    }
  },
  "metadata": {
    "environment": "production",
    "hostname": "SERVER01",
    "correlationId": "12345-67890-abcde"
  }
}
```

### HTTP Headers

DeployForge sends these headers:

```
Content-Type: application/json
User-Agent: DeployForge/1.0.0
X-DeployForge-Event: OperationCompleted
X-DeployForge-Severity: Success
X-DeployForge-Timestamp: 2025-01-08T10:30:00Z
Authorization: Bearer [your-token] (if configured)
```

### Webhook Security

#### HMAC Signature Verification

**Server-side validation:**
```python
import hmac
import hashlib

def verify_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)

# In request handler:
signature = request.headers.get('X-DeployForge-Signature')
if not verify_signature(request.body, signature, SECRET_KEY):
    return 401
```

**Enable in DeployForge:**
```
Advanced > Webhook Security
☑ Enable HMAC signatures
Secret Key: [shared secret]
Algorithm: SHA-256
```

#### IP Whitelisting

Restrict webhook endpoint to DeployForge server IP:
```
Firewall Rule:
  Allow: 192.168.1.100 (DeployForge server)
  To: Port 443
  Protocol: HTTPS
  Deny: All others
```

---

## Alert Threshold Tuning

### Understanding Metrics

#### CPU Usage
- **Measurement**: Percentage of CPU time used
- **Baseline**: Varies by workload (typically 20-40% idle)
- **Threshold**: 80% (high activity but not critical)
- **Critical**: 95%+ sustained

**Tuning:**
- Increase threshold for compute-intensive workloads
- Decrease for latency-sensitive operations
- Consider peak vs average usage

#### Memory Usage
- **Measurement**: Percentage of physical RAM used
- **Baseline**: 50-70% normal (OS caching)
- **Threshold**: 85% (approaching swapping)
- **Critical**: 95%+ (performance degradation)

**Tuning:**
- Lower threshold if swapping observed
- Higher threshold for memory-intensive operations
- Monitor available vs used

#### Disk Usage
- **Measurement**: Percentage of disk space used
- **Baseline**: <70% (allows temp file growth)
- **Threshold**: 90% (limited free space)
- **Critical**: 95%+ (risk of failures)

**Tuning:**
- Lower threshold for system drives
- Higher threshold for data drives
- Account for log rotation and temp files

### Threshold Recommendations

| Workload Type | CPU | Memory | Disk |
|---------------|-----|--------|------|
| Development | 80% | 85% | 90% |
| Production (24/7) | 70% | 75% | 85% |
| Batch Processing | 90% | 90% | 90% |
| Interactive UI | 60% | 70% | 90% |

### Alert Cooldown

Prevent alert spam with cooldown periods:

```
Settings > Monitoring > Advanced

Alert Cooldown (minutes): 15

Result: Same alert won't trigger again for 15 minutes
```

**Tuning:**
- Short cooldown (5 min): Critical alerts
- Medium cooldown (15 min): Normal alerts
- Long cooldown (60 min): Informational alerts

---

## Cron Expression Patterns

### Common Patterns

#### Daily Schedules

```
At specific time:
0 2 * * *       -> Daily at 2:00 AM
0 18 * * *      -> Daily at 6:00 PM
30 14 * * *     -> Daily at 2:30 PM

Multiple times:
0 8,12,18 * * * -> 8 AM, 12 PM, 6 PM
0 */4 * * *     -> Every 4 hours
0 9-17 * * *    -> Every hour from 9 AM to 5 PM
```

#### Weekly Schedules

```
Specific days:
0 9 * * 1       -> Every Monday at 9 AM
0 9 * * 1-5     -> Weekdays at 9 AM
0 9 * * 0,6     -> Weekends at 9 AM

Multiple times:
0 9,17 * * 1-5  -> Weekdays at 9 AM and 5 PM
```

#### Monthly Schedules

```
Specific dates:
0 0 1 * *       -> 1st of every month at midnight
0 9 15 * *      -> 15th of every month at 9 AM
0 0 1 1 *       -> January 1st at midnight

Last day:
0 0 28-31 * *   -> Last few days (combine with logic)
```

#### Advanced Patterns

```
Complex schedules:
0 0 * * 1#1     -> First Monday (some cron implementations)
0 9 1-7 * 1     -> First Monday of month
*/30 9-17 * * 1-5 -> Every 30 min during business hours

Excluded times:
0 9 * * 1-5     -> Weekdays (use maintenance windows to skip holidays)
```

### Cron Expression Tester

Use online tool: https://crontab.guru

Or in DeployForge:
1. Schedules > Create Schedule
2. Enter cron expression
3. Click "Validate Expression"
4. See next 5 execution times
5. Verify against expectations

---

## Performance Optimization

### Application Settings

#### Cache Size

```
Settings > General > Performance

Cache Size (MB): [————500————] 500 MB

Guidelines:
  - Minimum: 100 MB
  - Recommended: 500 MB
  - High-volume: 1000+ MB
```

**Impact:**
- Larger cache: Faster repeated operations, more memory
- Smaller cache: Less memory, more API calls

#### Concurrent Operations

```
Maximum Concurrent Operations: [——2——] 2 operations

Guidelines:
  - Single-core CPU: 1-2
  - Quad-core CPU: 2-4
  - High-end CPU: 4-8
```

**Impact:**
- More concurrent: Faster batch operations, higher CPU/memory
- Fewer concurrent: Lower resource usage, slower batches

#### Hardware Acceleration

```
☑ Enable hardware acceleration

Requirements:
  - GPU with DirectX 12 support
  - Updated graphics drivers
```

**Impact:**
- Enabled: Smoother UI, better rendering
- Disabled: Lower GPU usage, compatibility mode

### Network Optimization

#### API Timeout

```
Settings > General > API Connection

Timeout (seconds): 30

Guidelines:
  - Fast network: 10-20 seconds
  - Normal network: 30 seconds
  - Slow/remote network: 60+ seconds
```

#### Compression

```
Advanced > Network

☑ Enable HTTP compression

Savings: 60-80% reduction in transfer size
```

### Database Optimization

#### Metrics Retention

```
Settings > Monitoring

Metrics Retention (days): 30

Impact:
  - Shorter retention: Less disk, faster queries
  - Longer retention: More history, trend analysis
```

#### Log Retention

```
Settings > General > Logging

☑ Auto-rotate logs
Max log file size: 10 MB
Max log files: 10

Total space: 100 MB
```

---

## Security Best Practices

### Credential Management

#### Email Passwords

**DO:**
- Use app-specific passwords (Gmail, Outlook)
- Store in Windows Credential Manager
- Rotate passwords regularly

**DON'T:**
- Use main account password with 2FA
- Share passwords across applications
- Store in plaintext files

#### Webhook URLs

**DO:**
- Treat as secrets (like passwords)
- Use HTTPS endpoints only
- Rotate URLs after team member leaves

**DON'T:**
- Commit to source control
- Share in public channels
- Reuse across applications

### Network Security

#### HTTPS Configuration

```
Settings > General > API Connection

☑ Use HTTPS

Certificate requirements:
  - Trusted CA (production)
  - Valid domain name
  - Not expired
```

**Development:**
```
# Trust self-signed certificate
certutil -addstore "Root" localhost.crt

Or disable HTTPS and use HTTP (dev only)
```

#### Firewall Rules

**Outbound (Desktop):**
- Allow: Port 5000/5001 (API)
- Allow: Port 587/465 (SMTP)
- Allow: Port 443 (Slack/Teams/Webhooks)

**Inbound (API Server):**
- Allow: Port 5000/5001 (API)
- Allow: Port 443 (HTTPS)
- Deny: All other ports

### Data Protection

#### Report Storage

```
Settings > Reports

Report Output Directory: D:\SecureStorage\Reports

Permissions:
  - Administrators: Full Control
  - Operators: Read, Write
  - Users: No Access
```

#### Log Files

```
Settings > General > Logging

Log Directory: C:\DeployForge\Logs

☐ Include sensitive data in logs

Protect:
  - Disable debug logging in production
  - Exclude passwords, tokens, keys
  - Regular log review for anomalies
```

### Access Control

#### Windows Integration

```
Run DeployForge as:
  - Standard User (read-only operations)
  - Administrator (system-level operations)

Use Windows User Account Control (UAC) for privilege escalation
```

#### Audit Logging

```
Settings > Advanced > Security

☑ Enable audit logging
☑ Log failed login attempts
☑ Log configuration changes
☑ Log administrative actions

Review: Settings > Logging > Open Log Directory
```

---

## Configuration Backup

### Export Settings

```
Settings > Advanced > Export Settings

[Export Settings]

Saves to: Downloads/deployforge-settings-[date].json
```

### Import Settings

```
Settings > Advanced > Import Settings

[Select File: deployforge-settings.json]

Options:
  ⚫ Merge with existing
  ⚪ Replace all settings

[Import]
```

### Automated Backup

```
PowerShell script:

$source = "$env:LOCALAPPDATA\DeployForge\settings.json"
$dest = "\\backup\deployforge\settings-$(Get-Date -f yyyy-MM-dd).json"
Copy-Item $source $dest

Schedule: Daily via Task Scheduler
```

---

## Advanced Topics

### Custom Themes

**Location**: `C:\Program Files\DeployForge\Themes\`

**Create**: `mytheme.xaml`
```xml
<ResourceDictionary xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation">
    <Color x:Key="PrimaryColor">#1976D2</Color>
    <Color x:Key="AccentColor">#FFC107</Color>
    <!-- More theme colors -->
</ResourceDictionary>
```

**Apply**: Settings > General > Application > Theme > Custom

### Plugin System

(Coming in future release)

---

*Last Updated: 2025-01-08*
