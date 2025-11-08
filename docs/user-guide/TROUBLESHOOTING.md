# Troubleshooting Guide

Common issues and solutions for DeployForge Desktop.

## Table of Contents

1. [Connection Issues](#connection-issues)
2. [Notification Problems](#notification-problems)
3. [Schedule Execution Failures](#schedule-execution-failures)
4. [Report Generation Errors](#report-generation-errors)
5. [Monitoring Issues](#monitoring-issues)
6. [Performance Problems](#performance-problems)
7. [Application Crashes](#application-crashes)
8. [Log Analysis](#log-analysis)

---

## Connection Issues

### "Cannot Connect to API"

**Symptoms:**
- Red connection indicator in status bar
- Error message: "Failed to connect to API"
- Timeout errors

**Diagnosis:**
```bash
# Test API connectivity
curl http://localhost:5000/health

# Check if API is running
netstat -an | findstr "5000"

# Test from Desktop machine
Test-NetConnection -ComputerName localhost -Port 5000
```

**Solutions:**

#### 1. Verify API is Running

```bash
# Windows
tasklist | findstr "DeployForge.Api"

# If not running:
cd C:\Program Files\DeployForge\Api
.\DeployForge.Api.exe
```

#### 2. Check Firewall

```powershell
# Windows Firewall
New-NetFirewallRule -DisplayName "DeployForge API" `
  -Direction Inbound `
  -LocalPort 5000 `
  -Protocol TCP `
  -Action Allow
```

#### 3. Verify URL in Settings

```
Settings > General > API Connection
API Base URL: http://localhost:5000 (check spelling, port)
☐ Use HTTPS (unless SSL configured)
```

#### 4. Increase Timeout

```
Settings > General > API Connection
Timeout (seconds): 60 (increase from default 30)
```

#### 5. Check Antivirus

Some antivirus software blocks localhost connections:
- Add exception for DeployForge.Desktop.exe
- Add exception for ports 5000/5001

### "SSL Certificate Error"

**Symptoms:**
- "The SSL connection could not be established"
- "Certificate validation failed"

**Solutions:**

#### 1. Use HTTP in Development

```
Settings > General > API Connection
API Base URL: http://localhost:5000
☐ Use HTTPS
```

#### 2. Trust Self-Signed Certificate

```powershell
# Export certificate from API
$cert = (Get-ChildItem Cert:\LocalMachine\My | Where Subject -like "*localhost*")[0]
Export-Certificate -Cert $cert -FilePath C:\Temp\localhost.cer

# Import to Trusted Root
Import-Certificate -FilePath C:\Temp\localhost.cer -CertStoreLocation Cert:\LocalMachine\Root
```

#### 3. Install Valid Certificate (Production)

```
Use Let's Encrypt, commercial CA, or enterprise PKI
Configure IIS/Kestrel with valid certificate
```

### "Unauthorized (401)"

**Symptoms:**
- Connected but operations fail with 401
- Authentication errors

**Solutions:**

#### 1. Check API Authentication Settings

```json
// appsettings.json
{
  "Authentication": {
    "Enabled": false  // Disable for testing
  }
}
```

#### 2. Provide API Key (if required)

```
Settings > Advanced > Security
API Key: [your-api-key]
```

---

## Notification Problems

### Email Not Sending

**Symptoms:**
- Test email fails
- No emails received
- Timeout errors

**Diagnosis:**
```
Notifications > Email > Send Test Email
Check: Notification History for error details
```

**Solutions:**

#### 1. Verify SMTP Settings

```
SMTP Server: smtp.gmail.com (check exact hostname)
Port: 587 (not 465 or 25)
☑ Use SSL/TLS
Username: your-email@gmail.com (full email address)
Password: [16-char app password, not regular password]
```

#### 2. Test SMTP Connection

```powershell
# PowerShell SMTP test
$smtp = New-Object Net.Mail.SmtpClient("smtp.gmail.com", 587)
$smtp.EnableSsl = $true
$smtp.Credentials = New-Object Net.NetworkCredential("user@gmail.com", "app-password")
$smtp.Send("user@gmail.com", "recipient@gmail.com", "Test", "Body")
```

#### 3. Check Firewall

```
Allow outbound connections:
  - Port 587 (TLS)
  - Port 465 (SSL)
  - To SMTP server IP
```

#### 4. Gmail-Specific Issues

**"Username and password not accepted":**
1. Enable 2-Factor Authentication
2. Generate App Password (https://myaccount.google.com/apppasswords)
3. Use app password in DeployForge, not regular password

**"Less secure app access":**
- No longer supported by Gmail
- Must use 2FA + App Password

#### 5. Check Notification History

```
Notifications > History
Filter: Failed
View: Error message details
```

Common errors:
- `535 Authentication failed`: Wrong password
- `450 Daily sending quota exceeded`: Too many emails
- `554 Transaction failed`: Blocked recipient

### Slack Messages Not Appearing

**Symptoms:**
- Test message fails
- No messages in Slack channel
- Webhook error 404

**Diagnosis:**
```
Check:
1. Webhook URL is complete and correct
2. Channel exists
3. Webhook is active in Slack
```

**Solutions:**

#### 1. Verify Webhook URL

```
Correct format:
https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX

Common errors:
❌ Missing https://
❌ Truncated URL
❌ Extra spaces
```

#### 2. Re-create Webhook

1. Go to Slack workspace settings
2. Find "Incoming Webhooks" app
3. Remove old webhook
4. Create new webhook for same channel
5. Copy new URL to DeployForge

#### 3. Check Channel Name

```
Channel: #deployforge (must include #)
Or leave blank to use webhook's default channel
```

#### 4. Test with curl

```bash
curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test from curl"}'
```

If curl works but DeployForge doesn't:
- Check proxy settings
- Verify firewall allows HTTPS to hooks.slack.com

### Teams Messages Not Appearing

**Symptoms:**
- Test message fails
- Error: "400 Bad Request"
- Error: "404 Not Found"

**Solutions:**

#### 1. Verify Webhook URL

```
Correct format:
https://outlook.office.com/webhook/[long-guid]@[tenant-guid]/IncomingWebhook/[channel-guid]/[connector-guid]

Common errors:
❌ URL expired (recreate connector)
❌ Connector removed from channel
❌ Invalid characters in URL
```

#### 2. Re-create Connector

1. Teams > Channel > ... > Connectors
2. Search "Incoming Webhook"
3. Remove old webhook
4. Add new webhook
5. Configure and save
6. Copy new URL to DeployForge

#### 3. Test Adaptive Card

```powershell
# PowerShell test
$body = @{
    type = "message"
    attachments = @(
        @{
            contentType = "application/vnd.microsoft.card.adaptive"
            content = @{
                type = "AdaptiveCard"
                version = "1.4"
                body = @(
                    @{
                        type = "TextBlock"
                        text = "Test from PowerShell"
                    }
                )
            }
        }
    )
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "YOUR-WEBHOOK-URL" -Method Post -Body $body -ContentType "application/json"
```

### Webhook Delivery Failures

**Symptoms:**
- Webhook timeout
- HTTP 500/502/503 errors
- Connection refused

**Solutions:**

#### 1. Verify Endpoint Accessibility

```bash
# Test endpoint
curl https://api.yourservice.com/webhooks/deployforge

# Check DNS
nslookup api.yourservice.com

# Check connectivity
Test-NetConnection -ComputerName api.yourservice.com -Port 443
```

#### 2. Check Webhook Server Logs

```
Look for:
  - Request received?
  - Authentication failures?
  - Processing errors?
  - Rate limiting?
```

#### 3. Verify Payload Format

```
Enable webhook logging in DeployForge:
Settings > Advanced > Logging > Webhook Debug Mode

Check payload matches expected format
```

#### 4. Test with Webhook.site

```
1. Go to https://webhook.site
2. Copy unique URL
3. Use as webhook URL in DeployForge
4. Send test
5. Inspect payload format
```

---

## Schedule Execution Failures

### "Schedule Not Executing"

**Symptoms:**
- Next run time passes but schedule doesn't execute
- Execution history empty
- No error messages

**Diagnosis:**
```
Check:
1. Schedule is enabled (toggle in list view)
2. Maintenance window not blocking execution
3. Schedule service is running
4. Cron expression is valid
```

**Solutions:**

#### 1. Verify Schedule is Enabled

```
Schedules > [Your Schedule]
☑ Enabled

If disabled:
  - Click toggle to enable
  - Save changes
```

#### 2. Validate Cron Expression

```
Schedules > Edit Schedule > Cron Expression
Click: "Validate Expression"

Check: Next 5 execution times
Verify: Times match your expectations

Common mistakes:
  "0 2 * * *"    ✓ Daily at 2 AM
  "2 * * * *"    ✗ Every hour at minute 2
  "0 14 * * 1"   ✓ Every Monday at 2 PM
  "0 14 * * 7"   ✗ 7 is invalid (use 0 for Sunday)
```

#### 3. Check Maintenance Windows

```
Schedules > Edit Schedule > Maintenance Windows

If maintenance window active:
  - Schedule won't run during window
  - Remove or adjust window timing
```

#### 4. Manually Execute

```
Schedules > [Your Schedule] > Execute button
Result: Immediate execution (bypasses cron)

If manual execution works:
  - Cron expression may be wrong
  - Check timezone settings
  - Verify system clock
```

#### 5. Restart Schedule Service

```
API Server:
- Restart DeployForge.Api.exe
- Schedules reload on startup
```

### "Schedule Execution Fails"

**Symptoms:**
- Schedule executes but fails
- Error in execution history
- Incomplete operations

**Diagnosis:**
```
Schedules > [Schedule] > View History
Click: Failed execution
View: Error message
```

**Common Errors:**

#### "Batch operation not found"

```
Solution:
1. Verify batch operation exists
2. Check batch operation ID in schedule matches reality
3. Re-select batch operation in schedule editor
4. Save schedule
```

#### "Insufficient permissions"

```
Solution:
1. Run API as administrator (for system operations)
2. Grant permissions to image paths
3. Check file/folder access rights
```

#### "Concurrent execution limit reached"

```
Schedule Policy:
Max Concurrent Executions: 1

If previous execution still running:
  - Increase limit
  - Or wait for previous execution to complete
  - Or reduce operation duration
```

#### "Operation timeout"

```
Solution:
1. Increase operation timeout
2. Optimize batch operation
3. Reduce batch size
```

---

## Report Generation Errors

### "PDF Generation Failed"

**Symptoms:**
- Report generation fails
- Error: "QuestPDF license error"
- Error: "Cannot create PDF"

**Solutions:**

#### 1. QuestPDF License

```
Error: "Community license required"

Solution:
1. Add to appsettings.json:
{
  "QuestPDF": {
    "License": "Community"
  }
}

2. Or in code startup:
QuestPDF.Settings.License = LicenseType.Community;

3. Restart API
```

#### 2. Verify Write Permissions

```powershell
# Check directory permissions
Get-Acl "C:\DeployForge\Reports" | Format-List

# Grant full control
$acl = Get-Acl "C:\DeployForge\Reports"
$permission = "BUILTIN\Users","FullControl","Allow"
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule $permission
$acl.SetAccessRule($accessRule)
Set-Acl "C:\DeployForge\Reports" $acl
```

#### 3. Check Disk Space

```powershell
Get-PSDrive C | Select-Object Used,Free
```

Solution: Free up disk space or change report output directory

#### 4. Font Issues (PDF Charts)

```
Error: "Font not found"

Solution:
1. Install required fonts (Arial, Calibri)
2. Or specify fallback font in settings
3. Use system fonts only
```

### "Report Empty or Missing Data"

**Symptoms:**
- Report generates but contains no data
- Charts missing
- Tables empty

**Solutions:**

#### 1. Check Date Range

```
Reports > Generate > Date Range
Start Date: [not in future]
End Date: [after start date]

Verify data exists in this range
```

#### 2. Verify Data Source

```
For Audit Report:
  - Check audit logs exist
  - Verify logging is enabled

For Statistics Report:
  - Check metrics collection is active
  - Verify monitoring is enabled
```

#### 3. Include Options

```
☑ Include Summary Section
☑ Include Detailed Logs
☑ Include Charts

At least one must be checked
```

---

## Monitoring Issues

### "Metrics Show 0% or Incorrect Values"

**Symptoms:**
- CPU/Memory/Disk always 0%
- Metrics don't update
- Incorrect uptime

**Solutions:**

#### 1. Restart Monitoring Service

```
API Server restart:
- Close DeployForge.Api.exe
- Start DeployForge.Api.exe
- Monitoring service starts automatically
```

#### 2. Check Permissions

```
Windows Performance Counters require:
  - Read access to performance counter registry keys
  - Run API as administrator for full metrics access
```

#### 3. Verify Performance Counters

```powershell
# List available counters
Get-Counter -ListSet "Processor"
Get-Counter -ListSet "Memory"

# Test counter
Get-Counter "\Processor(_Total)\% Processor Time"
```

If errors: Rebuild performance counters
```cmd
lodctr /R
```

#### 4. Check Metrics Collection Interval

```
API appsettings.json:

{
  "Monitoring": {
    "MetricsIntervalSeconds": 5
  }
}

Default: 5 seconds
Increase if system load high
```

### "Real-Time Updates Not Working"

**Symptoms:**
- Dashboard doesn't auto-refresh
- Must click Refresh button
- SignalR connection failed

**Solutions:**

#### 1. Check SignalR Connection

```
Desktop app:
Status bar should show: "🟢 Connected (SignalR)"

If not:
  "🟡 Connected (Polling)" = SignalR failed, using fallback
```

#### 2. Verify SignalR Hub

```
Test URL: http://localhost:5000/hubs/progress
Expected: 404 or connection upgrade attempt
```

#### 3. Check Firewall/Proxy

```
SignalR uses WebSockets
Requires: ws:// or wss:// protocol
Firewall: Must allow WebSocket upgrade
Proxy: Must support WebSocket pass-through
```

#### 4. Fallback to Polling

```
Settings > Advanced > Monitoring
☑ Use polling if SignalR fails
Poll Interval (seconds): 10
```

### "Alerts Not Triggering"

**Symptoms:**
- Metrics exceed threshold but no alert
- Alert history empty
- Notifications not sent

**Solutions:**

#### 1. Verify Alerts Enabled

```
Settings > Monitoring
☑ Enable Alert Monitoring

Click: "Apply Alert Thresholds"
```

#### 2. Check Cooldown Period

```
Alert Cooldown: 15 minutes

If alert triggered recently:
  - Won't trigger again for 15 minutes
  - Check alert history for previous trigger
```

#### 3. Verify Thresholds

```
CPU Threshold: 80%
Current CPU: 75%

If current < threshold: No alert

Temporarily lower threshold to test
```

#### 4. Check Notification Configuration

```
Settings > Notifications
At least one channel must be enabled and configured

Test notification delivery separately
```

---

## Performance Problems

### "Application Slow or Laggy"

**Symptoms:**
- UI freezes
- Slow response to clicks
- High CPU usage by Desktop app

**Solutions:**

#### 1. Disable Hardware Acceleration

```
Settings > General > Performance
☐ Enable hardware acceleration

Restart application
```

#### 2. Reduce Cache Size

```
Cache Size (MB): 500 → 200
Click: "Clear Cache"
Restart application
```

#### 3. Close Unused Tabs

```
Close monitoring dashboard when not needed (SignalR connection active)
Close large reports (memory usage)
```

#### 4. Update Graphics Drivers

```
Device Manager > Display adapters
Right-click > Update driver
Or download from manufacturer website
```

### "High Memory Usage"

**Symptoms:**
- Application uses excessive RAM
- System becomes slow
- Out of memory errors

**Solutions:**

#### 1. Check Cache Settings

```
Settings > General > Performance
Cache Size: [————200————] 200 MB (reduce from 500+)
```

#### 2. Limit Concurrent Operations

```
Maximum Concurrent Operations: [——1——] 1 operation
(Reduce from 4+ to 1-2)
```

#### 3. Clear Application Data

```
Close DeployForge Desktop
Delete: %LOCALAPPDATA%\DeployForge\cache\*
Restart application
```

#### 4. Monitor Resource Usage

```
Task Manager > Details > DeployForge.Desktop.exe
Track: Memory, CPU over time
Look for: Memory leaks (gradually increasing memory)
```

### "Slow API Responses"

**Symptoms:**
- Operations take long time
- Timeout errors
- Loading spinners stuck

**Solutions:**

#### 1. Check API Server Resources

```
API Server:
Task Manager > DeployForge.Api.exe
CPU usage: Should be < 50% idle
Memory usage: Should have 1+ GB free
```

#### 2. Reduce Concurrent Operations

```
Settings > General > Performance
Max Concurrent Operations: 2 → 1

Schedules > Edit > Policy
Max Concurrent Executions: 1
```

#### 3. Optimize Database

```
API Server:
Compact database (if using SQLite):

sqlite3 deployforge.db
VACUUM;
ANALYZE;
```

#### 4. Network Latency

```
Test latency:
ping localhost (should be <1ms local)
ping api-server (should be <100ms network)

If high latency:
  - Use wired connection instead of WiFi
  - Check network equipment
  - Reduce network traffic
```

---

## Application Crashes

### "Application Won't Start"

**Symptoms:**
- Double-click does nothing
- Splash screen appears then closes
- Error dialog on startup

**Solutions:**

#### 1. Check Event Viewer

```
Event Viewer > Windows Logs > Application
Look for: "DeployForge.Desktop" errors
Note: Error message and stack trace
```

#### 2. Verify .NET Runtime

```
Required: .NET 8.0 Desktop Runtime

Check installed:
dotnet --list-runtimes

Should show: Microsoft.WindowsDesktop.App 8.0.x

If missing:
Download from: https://dotnet.microsoft.com/download/dotnet/8.0
Install: Desktop Runtime (not SDK)
```

#### 3. Reset Settings

```
Rename settings file:
%LOCALAPPDATA%\DeployForge\settings.json
→ settings.json.bak

Restart application (will use defaults)
```

#### 4. Reinstall Application

```
1. Uninstall DeployForge Desktop
2. Delete: C:\Program Files\DeployForge
3. Delete: %LOCALAPPDATA%\DeployForge
4. Reinstall from setup.exe
```

### "Unexpected Crashes During Use"

**Symptoms:**
- Application closes suddenly
- No error message
- Happens during specific operation

**Solutions:**

#### 1. Enable Crash Dumps

```
Settings > Advanced > Diagnostics
☑ Enable crash dumps
Dump location: C:\DeployForge\CrashDumps\

Reproduce crash
Send dump file to support
```

#### 2. Check for Corrupt Data

```
Close application
Delete cache:
  %LOCALAPPDATA%\DeployForge\cache\
Delete temp files:
  %TEMP%\DeployForge\
Restart application
```

#### 3. Disable Add-ins (future feature)

```
Settings > Add-ins
Disable all add-ins
Test if crash still occurs
Enable one at a time to identify culprit
```

#### 4. Run as Administrator

```
Right-click DeployForge.Desktop.exe
"Run as administrator"

Some operations require elevated privileges
```

---

## Log Analysis

### Accessing Logs

**Desktop Application Logs:**
```
Settings > General > Logging > "Open Log Directory"

Location: C:\DeployForge\Logs\
Files:
  - deployforge-desktop-YYYYMMDD.log
  - deployforge-desktop-YYYYMMDD.001.log (if rotated)
```

**API Server Logs:**
```
Location: C:\DeployForge\Api\logs\
Files:
  - deployforge-api-YYYYMMDD.log
```

### Log Levels

```
Verbose: All messages (very detailed)
Debug: Debugging information
Information: Normal operation messages
Warning: Potential issues
Error: Operation failures
Critical: Application-wide failures
```

**Change Log Level:**
```
Settings > General > Logging
Log Level: Information (default)

For troubleshooting: Debug or Verbose
For production: Information or Warning
```

### Common Log Patterns

#### Connection Issues

```
[Error] Failed to connect to API at http://localhost:5000
```
→ See [Connection Issues](#connection-issues)

#### API Errors

```
[Error] API returned 500: Internal Server Error
[Error] Response: {"message":"NullReferenceException at..."}
```
→ Check API logs for details

#### Notification Failures

```
[Error] Failed to send email: SmtpException: 535 Authentication failed
```
→ See [Email Not Sending](#email-not-sending)

#### Schedule Errors

```
[Error] Schedule 'daily-backup' failed: Batch operation not found
```
→ See [Schedule Execution Failures](#schedule-execution-failures)

### Sharing Logs with Support

**Collect Diagnostic Information:**
```
File > Generate Diagnostic Report

Includes:
  - Last 24h of logs
  - Current settings (sanitized)
  - System information
  - Error details

Saved to: Downloads\deployforge-diagnostics-YYYYMMDD.zip
```

**Sanitize Sensitive Data:**
```
Before sharing, remove:
  - Passwords
  - API keys
  - Webhook URLs
  - Email addresses (if needed)
  - IP addresses (if needed)
```

---

## Getting Help

### Self-Service Resources

1. **Documentation**
   - [User Guide](./USER_GUIDE.md)
   - [Configuration Guide](./CONFIGURATION_GUIDE.md)
   - [API Documentation](../OPTION_B_FEATURES.md)

2. **FAQ**
   - https://github.com/Cornman92/DeployForge/wiki/FAQ

3. **Video Tutorials**
   - https://github.com/Cornman92/DeployForge/wiki/Tutorials

### Community Support

1. **GitHub Discussions**
   - https://github.com/Cornman92/DeployForge/discussions
   - Ask questions, share solutions

2. **GitHub Issues**
   - https://github.com/Cornman92/DeployForge/issues
   - Report bugs, request features

### Reporting Bugs

**Include:**
1. DeployForge version (Help > About)
2. Operating System version
3. Steps to reproduce
4. Expected vs actual behavior
5. Error messages/screenshots
6. Relevant log excerpts
7. Diagnostic report (if applicable)

**Template:**
```markdown
## Bug Description
[Clear description of the issue]

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- DeployForge Version: 1.0.0
- OS: Windows 11 Pro 22H2
- .NET Runtime: 8.0.1

## Logs
```
[Paste relevant log excerpt here]
```

## Screenshots
[Attach screenshots if applicable]
```

---

*Last Updated: 2025-01-08*
