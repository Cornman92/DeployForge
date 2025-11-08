# DeployForge Desktop - User Guide

Complete guide for using DeployForge Desktop's advanced features.

## Table of Contents

1. [Monitoring Dashboard](#monitoring-dashboard)
2. [Scheduled Operations](#scheduled-operations)
3. [Report Generation](#report-generation)
4. [Notifications Center](#notifications-center)
5. [Settings Configuration](#settings-configuration)

---

## Monitoring Dashboard

The Monitoring Dashboard provides real-time system health metrics and alerts.

### Overview

Navigate to **Monitoring** to access the dashboard, which displays:

- **Current Metrics**
  - CPU Usage (%)
  - Memory Usage (%)
  - Disk Usage (%)
  - Active Operations
  - System Uptime

- **Historical Charts**
  - CPU Usage History (last 50 data points)
  - Memory Usage History (last 50 data points)
  - Auto-refreshing every 5 seconds via SignalR

- **Recent Alerts**
  - Last 10 alert events
  - Timestamp, metric type, threshold exceeded
  - Alert message details

### Features

#### Real-Time Updates

The dashboard uses SignalR for live updates:
- Metrics refresh automatically every 5 seconds
- No manual refresh needed
- Fallback to polling if SignalR disconnects

#### Performance Statistics

View aggregate statistics:
- **Average CPU/Memory Usage**: Over the monitoring period
- **Peak CPU/Memory Usage**: Maximum values recorded
- **Total Metrics Collected**: Data point count

### Actions

#### Refresh Data

```
Click: Refresh Button (top right)
Result: Manually refresh all metrics and charts
```

#### Configure Alerts

```
Click: Configure Alerts Button
Opens: Alert Configuration Dialog
Configure: CPU, Memory, Disk thresholds
Save: Apply new thresholds to monitoring service
```

#### View Metrics History

```
Click: View History Button
Action: Load last 1 hour of metrics
Display: Populate charts with historical data (last 50 points)
```

### Alert Thresholds

Default thresholds:
- **CPU**: 80%
- **Memory**: 85%
- **Disk**: 90%

When a metric exceeds its threshold:
1. Alert is generated
2. Notification sent (if configured)
3. Alert appears in Recent Alerts list
4. Alert stored in history

### Troubleshooting

**Dashboard not updating:**
- Check API connection status
- Verify SignalR hub is running
- Check browser console for WebSocket errors

**Metrics show 0%:**
- API may not be collecting metrics
- Check monitoring service is started
- Verify permissions for system metrics

---

## Scheduled Operations

Automate batch operations with cron-based scheduling.

### Overview

Navigate to **Schedules** to manage automated operations.

### Creating a Schedule

#### Step 1: Basic Information

```
1. Click "Create Schedule"
2. Enter schedule details:
   - Name: e.g., "Daily Image Optimization"
   - Description: What the schedule does
   - Enable/Disable toggle
```

#### Step 2: Timing Configuration

```
3. Set cron expression:
   - Use cron builder or enter manually
   - Examples:
     * "0 2 * * *" = Daily at 2:00 AM
     * "0 */4 * * *" = Every 4 hours
     * "0 9 * * 1" = Every Monday at 9:00 AM
   - Validate cron: Click "Validate Expression"
```

#### Step 3: Operation Selection

```
4. Select batch operation:
   - Choose from dropdown of available operations
   - Operation details shown below
```

#### Step 4: Policy Configuration

```
5. Configure execution policy:
   ☑ Retry on Failure
   - Max Retry Attempts: 3

   ☑ Notify on Completion
   ☑ Notify on Failure

   - Max Concurrent Executions: 1
```

#### Step 5: Maintenance Windows (Optional)

```
6. Add maintenance windows:
   - Click "Add Window"
   - Set start/end day and hours
   - Schedule won't run during these times
   - Example: Skip weekends for maintenance
```

#### Step 6: Save

```
7. Click "Create Schedule"
   - Schedule is created
   - Enabled schedules start automatically
   - View in schedule list
```

### Managing Schedules

#### Schedule List View

Displays all schedules with:
- Name and description
- Next run time (calculated from cron)
- Last run status (Success/Failed/Never)
- Enabled/Disabled status
- Actions (Edit, Delete, Execute, History)

#### Schedule Actions

**Edit Schedule**
```
Click: Edit icon
Action: Open schedule in edit mode
Modify: Any schedule properties
Save: Update schedule
```

**Delete Schedule**
```
Click: Delete icon
Confirm: Deletion dialog
Result: Schedule permanently removed
```

**Manual Execution**
```
Click: Execute icon
Action: Immediately run schedule (ignores cron)
Result: Operation executes, history recorded
Use Case: Test schedule before enabling
```

**View History**
```
Click: History icon
Display: Execution history table
Columns: Start Time, End Time, Status, Duration, Error (if any)
Filter: By date range
```

### Execution History

Each execution record contains:
- **Schedule Name**: Which schedule ran
- **Start Time**: When execution began
- **End Time**: When execution completed
- **Status**: Success, Failed, Cancelled
- **Duration**: Total execution time
- **Error Message**: If failed, the error details

### Cron Expression Guide

| Pattern | Description | Example |
|---------|-------------|---------|
| `* * * * *` | Every minute | Tests |
| `0 * * * *` | Every hour | Hourly checks |
| `0 2 * * *` | Daily at 2 AM | Nightly jobs |
| `0 9 * * 1` | Every Monday at 9 AM | Weekly reports |
| `0 0 1 * *` | 1st of month at midnight | Monthly tasks |
| `*/15 * * * *` | Every 15 minutes | Frequent polling |
| `0 2 * * 1-5` | Weekdays at 2 AM | Business days only |

**Cron Format**: `minute hour day month day-of-week`
- minute: 0-59
- hour: 0-23
- day: 1-31
- month: 1-12
- day-of-week: 0-6 (0 = Sunday)

### Best Practices

1. **Test First**: Use "Execute" to test before enabling
2. **Avoid Overlaps**: Don't schedule heavy operations simultaneously
3. **Set Maintenance Windows**: Prevent execution during backups/updates
4. **Enable Notifications**: Get alerts when schedules fail
5. **Monitor History**: Check for patterns in failures
6. **Use Retry Logic**: Enable retry for transient failures

---

## Report Generation

Generate professional reports in multiple formats.

### Overview

Navigate to **Reports** to generate and manage reports.

### Report Types

#### 1. Validation Reports

```
Purpose: Document image validation results
Contains:
  - Image path and details
  - Validation checks performed
  - Pass/Fail status
  - Detailed findings
  - Recommendations
```

#### 2. Audit Reports

```
Purpose: Operation audit trail
Contains:
  - Date range of operations
  - User actions
  - Operation types
  - Success/failure rates
  - Timeline of events
```

#### 3. Statistics Reports

```
Purpose: Performance metrics analysis
Contains:
  - Operation counts by type
  - Success/failure ratios
  - Performance trends
  - Resource utilization
  - Charts and graphs (PDF only)
```

#### 4. Batch Operation Reports

```
Purpose: Summary of batch execution
Contains:
  - Batch operation details
  - Individual operation results
  - Total/success/failure counts
  - Duration statistics
  - Error summary
```

### Generating Reports

#### Step 1: Select Report Type

```
1. Click "Generate Report"
2. Select report type from dropdown:
   - Validation
   - Audit
   - Statistics
   - Batch Operation
```

#### Step 2: Configure Options

```
3. Set report parameters:
   - Title: Custom report title
   - Description: Report purpose
   - Date Range: Start and end dates
   - Format: PDF, HTML, or JSON
```

#### Step 3: Content Options

```
4. Choose content to include:
   ☑ Include Charts (PDF only)
   ☑ Include Summary Section
   ☑ Include Detailed Logs
   ☑ Include Recommendations
```

#### Step 4: Generate

```
5. Click "Generate Report"
   - Progress bar shows generation status
   - Report appears in reports list
   - Automatic download (if configured)
```

### Report Formats

#### PDF (Recommended)

**Features:**
- Professional layout
- Charts and graphs
- Print-ready
- Portable format

**Use Cases:**
- Executive summaries
- Sharing with stakeholders
- Archival

**Charts Available:**
- Bar charts (operation counts)
- Pie charts (distributions)
- Line charts (trends)
- Progress bars (utilization)

#### HTML

**Features:**
- Styled tables
- Responsive design
- Interactive (links, expandable sections)
- Email-friendly

**Use Cases:**
- Email distribution
- Web publishing
- Internal dashboards

#### JSON

**Features:**
- Machine-readable
- API-friendly
- Complete data export
- No formatting overhead

**Use Cases:**
- Data analysis
- System integration
- Custom processing
- Database import

### Managing Reports

#### Report List View

Displays all generated reports:
- Report type and title
- Generation date
- Format (PDF/HTML/JSON)
- File size
- Actions (Download, Delete, Export)

#### Report Actions

**Download Report**
```
Click: Download icon
Action: Save report to local disk
Location: User's Downloads folder or configured directory
```

**Delete Report**
```
Click: Delete icon
Confirm: Deletion dialog
Result: Report removed from server
Warning: Cannot be undone
```

**Export to Different Format**
```
Click: Export icon
Select: Target format
Action: Convert report to new format
Result: New report generated
```

**View Report Details**
```
Click: Report row
Display: Report metadata
Show: Title, description, date, size
Preview: Report content (HTML only)
```

### Report Storage

Reports are stored:
- **Server**: `C:\ProgramData\DeployForge\Reports\`
- **Downloads**: User's configured download directory
- **Retention**: Configurable in Settings (default: 60 days)

### Automated Reports

Configure automatic report generation:

```
Settings > Reports > Automated Reports

☑ Auto-generate daily report
  - Daily Report Time: 09:00
  - Report Type: Statistics
  - Format: PDF
  - Recipients: admin@company.com
```

### Best Practices

1. **Choose Format Wisely**: PDF for presentation, JSON for data
2. **Include Charts**: Visual data is more impactful
3. **Set Date Ranges**: Don't generate reports with too much data
4. **Regular Cleanup**: Delete old reports to save space
5. **Automate Common Reports**: Use scheduled reports for regular needs

---

## Notifications Center

Manage notification channels and view notification history.

### Overview

Navigate to **Notifications** to configure and monitor notifications.

### Notification Channels

DeployForge supports 4 notification channels:

#### 1. Email (SMTP)

**Configuration:**
```
Settings > Notifications > Email Notifications

☑ Enable email notifications
SMTP Server: smtp.gmail.com
Port: 587
☑ Use SSL/TLS
Username: deployforge@company.com
Password: ••••••••••••••••
From Email: deployforge@company.com
To Email(s): admin@company.com, ops@company.com

[Send Test Email]
```

**Supported Providers:**
- Gmail (port 587, SSL)
- Outlook (port 587, TLS)
- Office 365 (port 587, TLS)
- Custom SMTP servers

**Gmail Setup:**
1. Enable 2-factor authentication
2. Generate app-specific password
3. Use app password in DeployForge

#### 2. Slack

**Configuration:**
```
Settings > Notifications > Slack Notifications

☑ Enable Slack notifications
Webhook URL: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
Channel: #deployforge
Username: DeployForge Bot

[Send Test Message]
```

**Slack Setup:**
1. Go to Slack workspace
2. Add "Incoming Webhooks" app
3. Create webhook for desired channel
4. Copy webhook URL
5. Paste into DeployForge settings

**Message Format:**
- Rich attachments
- Color-coded by severity
- Includes operation details
- Clickable links (if applicable)

#### 3. Microsoft Teams

**Configuration:**
```
Settings > Notifications > Teams Notifications

☑ Enable Teams notifications
Webhook URL: https://outlook.office.com/webhook/YOUR-WEBHOOK-URL

[Send Test Message]
```

**Teams Setup:**
1. Open desired Teams channel
2. Click "..." > Connectors
3. Add "Incoming Webhook"
4. Name webhook and upload icon
5. Copy webhook URL
6. Paste into DeployForge settings

**Message Format:**
- Adaptive Cards
- Formatted tables
- Action buttons
- Branded with DeployForge theme

#### 4. Custom Webhooks

**Configuration:**
```
Settings > Notifications > Custom Webhook

☑ Enable webhook notifications
Webhook URL: https://api.yourservice.com/webhooks
Method: POST
Authorization Header: Bearer your-token-here (optional)

[Send Test Webhook]
```

**Payload Format:**
```json
{
  "timestamp": "2025-01-08T10:30:00Z",
  "eventType": "OperationCompleted",
  "severity": "Success",
  "title": "Image Processing Complete",
  "message": "Successfully processed 10 images",
  "data": {
    "operationId": "op-12345",
    "duration": "5 minutes",
    "itemCount": 10
  }
}
```

### Notification Events

DeployForge sends notifications for these events:

| Event | Severity | When Triggered |
|-------|----------|----------------|
| `OperationStarted` | Info | Operation begins |
| `OperationCompleted` | Success | Operation succeeds |
| `OperationFailed` | Error | Operation fails |
| `ScheduleExecuted` | Info | Scheduled job runs |
| `ScheduleFailed` | Error | Scheduled job fails |
| `AlertTriggered` | Warning/Error | Metric exceeds threshold |
| `ReportGenerated` | Success | Report created |
| `SystemStartup` | Info | DeployForge starts |

### Notification History

View all sent notifications:

**Columns:**
- Timestamp
- Event Type
- Channels (Email/Slack/Teams/Webhook)
- Status (Sent/Failed)
- Message preview
- Details

**Filters:**
- Date range
- Event type
- Channel
- Status

**Actions:**
- View full details
- Resend failed notifications
- Export history

### Testing Notifications

Always test before relying on notifications:

```
1. Configure channel settings
2. Click "Send Test [Channel]"
3. Check destination for test message
4. Verify message format and content
5. If failed, check:
   - Credentials/webhook URL
   - Network connectivity
   - Firewall rules
   - Service status
```

### Notification Rules

Create custom rules for specific events:

```
Notifications > Rules > Create Rule

Name: Critical Failures
Event Type: OperationFailed
Conditions:
  - Severity = Error
  - Operation Type = Batch
Channels:
  ☑ Email
  ☑ Slack
  ☑ Teams
  ☐ Webhook
Recipients:
  - admin@company.com
  - oncall@company.com

[Save Rule]
```

### Best Practices

1. **Test All Channels**: Verify delivery before relying on notifications
2. **Use Multiple Channels**: Redundancy for critical alerts
3. **Configure Rules**: Avoid notification spam with targeted rules
4. **Monitor History**: Check for delivery failures
5. **Secure Credentials**: Use app passwords, rotate webhooks regularly
6. **Set Severity Filters**: Only notify on important events

---

## Settings Configuration

Configure all aspects of DeployForge Desktop.

### Settings Navigation

Access Settings via navigation bar, organized in tabs:
1. **General**: API, Application, Performance, Logging
2. **Monitoring**: Alert thresholds, data retention
3. **Notifications**: Email, Slack, Teams, Webhooks
4. **Reports**: Output directory, formats, automation
5. **Schedules**: Job configuration, time zones

### General Settings

#### API Connection

```
API Base URL: http://localhost:5000
Timeout (seconds): 30
☑ Use HTTPS

[Test Connection]
```

#### Application

```
Theme: Dark
Language: English
☑ Check for updates automatically
☐ Start with Windows
☐ Minimize to system tray

[Check for Updates Now]
```

#### Performance

```
Maximum Concurrent Operations: [——2——] 2 operations
Cache Size (MB): [————500————] 500 MB
☑ Enable hardware acceleration

[Clear Cache]
```

#### Logging

```
Log Level: Information
☑ Enable file logging
☐ Enable debug logging (verbose)
Log Directory: C:\DeployForge\Logs

[Browse...] [Open Log Directory]
```

### Monitoring Settings

#### Alert Thresholds

```
☑ Enable Alert Monitoring

CPU Usage Threshold (%): [————80————] 80%
Memory Usage Threshold (%): [————85————] 85%
Disk Usage Threshold (%): [————90————] 90%

[Apply Alert Thresholds]
```

#### Data Retention

```
Metrics Retention (days): 30
Alert Retention (days): 90
```

### Notification Settings

See [Notifications Center](#notification-channels) for detailed configuration.

**Save All Channels:**
```
[Save All Notification Settings]
```

This button saves:
- Email settings
- Slack configuration
- Teams configuration
- Webhook settings

### Report Settings

#### Report Generation

```
Report Output Directory: C:\DeployForge\Reports
[Browse...] [Open Directory]

Default Report Format: PDF
☑ Include charts in reports
☑ Include summary section
☐ Include detailed logs
```

#### Automated Reports

```
☑ Auto-generate daily report
Daily Report Time (HH:mm): 09:00
```

#### Report Retention

```
Report Retention (days): 60
```

### Schedule Settings

#### Schedule Configuration

```
☑ Enable scheduled jobs

Maximum Concurrent Scheduled Jobs: [——5——] 5 jobs

Default Time Zone: UTC
☑ Send notifications for scheduled job completion
```

#### Schedule Retention

```
Schedule History Retention (days): 180
```

### Saving Settings

**Individual Sections:**
- Some sections have "Apply" buttons (e.g., Alert Thresholds)
- Changes apply immediately to specific feature

**Global Save:**
- Top-right "Save Settings" button
- Saves all changes across all tabs
- Shows confirmation message

**Reset to Defaults:**
- Top-right "Reset to Defaults" button
- Confirms before resetting
- Restores factory settings

### Settings Storage

Settings are stored:
- **Location**: `C:\Users\[User]\AppData\Local\DeployForge\settings.json`
- **Format**: JSON
- **Backup**: Automatic backup on change
- **Sync**: Sync with API server (if enabled)

### Import/Export Settings

**Export Settings:**
```
Settings > Advanced > Export Settings
Format: JSON
Use Case: Backup, share with team, migrate to new machine
```

**Import Settings:**
```
Settings > Advanced > Import Settings
Select: JSON file
Action: Merge or replace existing settings
Confirm: Preview changes before applying
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+R` | Refresh current view |
| `Ctrl+S` | Save (in edit mode) |
| `Ctrl+,` | Open Settings |
| `Ctrl+Q` | Quit application |
| `F5` | Refresh current view |
| `F1` | Open help documentation |
| `Esc` | Close dialog/cancel |

---

## Support and Resources

### Documentation

- [Getting Started Guide](./GETTING_STARTED.md)
- [Configuration Guide](./CONFIGURATION_GUIDE.md)
- [Troubleshooting Guide](./TROUBLESHOOTING.md)
- [API Documentation](../OPTION_B_FEATURES.md)

### Community

- **GitHub**: https://github.com/Cornman92/DeployForge
- **Issues**: https://github.com/Cornman92/DeployForge/issues
- **Discussions**: https://github.com/Cornman92/DeployForge/discussions
- **Wiki**: https://github.com/Cornman92/DeployForge/wiki

### Updates

Check for updates:
1. Settings > General > Application
2. Click "Check for Updates Now"
3. Or enable "Check for updates automatically"

---

*Last Updated: 2025-01-08*
