# Option B Backend Features - Complete Documentation

## Overview

Option B provides four enterprise-grade backend features that extend DeployForge's core capabilities:

1. **Scheduled Operations** - Automated batch operation execution
2. **Notification System** - Multi-channel notifications (Email, Webhooks, Slack, Teams)
3. **Report Generation** - Professional reports in multiple formats (HTML, JSON, Markdown, PDF)
4. **Health Monitoring** - Real-time system metrics and alerting

---

## 1. Scheduled Operations

### Features
- Cron-based scheduling for batch operations
- Maintenance windows to prevent execution during specific times
- Execution history tracking
- Manual trigger capability
- Integration with notification system
- Retry policies

### Configuration

```json
{
  "id": "schedule-001",
  "name": "Nightly Image Optimization",
  "description": "Optimize all images every night at 2 AM",
  "enabled": true,
  "cronExpression": "0 2 * * *",
  "batchOperationId": "batch-optimize-all",
  "maintenanceWindows": [
    {
      "name": "Weekend Maintenance",
      "startDay": "Saturday",
      "startHour": 0,
      "endDay": "Sunday",
      "endHour": 23
    }
  ],
  "policy": {
    "maxConcurrentExecutions": 1,
    "retryOnFailure": true,
    "maxRetryAttempts": 3,
    "notifyOnCompletion": true,
    "notifyOnFailure": true
  }
}
```

### API Endpoints

```http
# Create schedule
POST /api/schedules
Content-Type: application/json

# Update schedule
PUT /api/schedules/{scheduleId}

# Delete schedule
DELETE /api/schedules/{scheduleId}

# Get schedule
GET /api/schedules/{scheduleId}

# List all schedules
GET /api/schedules?enabledOnly=true

# Manually execute schedule
POST /api/schedules/{scheduleId}/execute

# Get execution history
GET /api/schedules/{scheduleId}/history?startDate=2025-01-01&endDate=2025-01-31
```

### Cron Expression Examples

| Schedule | Cron Expression |
|----------|----------------|
| Every hour | `0 * * * *` |
| Daily at 2 AM | `0 2 * * *` |
| Every Monday at 8 AM | `0 8 * * 1` |
| First day of month at midnight | `0 0 1 * *` |
| Every 15 minutes | `*/15 * * * *` |

---

## 2. Notification System

### Supported Channels
1. **Email** (SMTP with SSL/TLS)
2. **Webhooks** (HTTP POST with JSON payload)
3. **Slack** (Incoming webhooks)
4. **Microsoft Teams** (Incoming webhooks with Adaptive Cards)

### Email Configuration

```json
{
  "enableEmail": true,
  "email": {
    "smtpHost": "smtp.gmail.com",
    "smtpPort": 587,
    "useSsl": true,
    "username": "deployforge@company.com",
    "password": "your-app-password",
    "fromEmail": "deployforge@company.com",
    "fromName": "DeployForge Automation",
    "defaultRecipients": [
      "admin@company.com",
      "ops-team@company.com"
    ]
  }
}
```

### Slack Configuration

```json
{
  "slack": {
    "enabled": true,
    "webhookUrl": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    "defaultChannel": "#deployforge-alerts",
    "botUsername": "DeployForge Bot",
    "iconEmoji": ":robot_face:"
  }
}
```

### Microsoft Teams Configuration

```json
{
  "teams": {
    "enabled": true,
    "webhookUrl": "https://outlook.office.com/webhook/YOUR-WEBHOOK-URL",
    "themeColor": "0076D7"
  }
}
```

### Notification Rules

```json
{
  "rules": [
    {
      "id": "rule-001",
      "name": "Critical Failures",
      "enabled": true,
      "eventType": "OperationFailed",
      "channels": ["Email", "Slack", "Teams"],
      "recipients": [
        "admin@company.com",
        "oncall@company.com"
      ]
    },
    {
      "id": "rule-002",
      "name": "Completion Notifications",
      "enabled": true,
      "eventType": "BatchOperationCompleted",
      "channels": ["Slack"],
      "recipients": []
    }
  ]
}
```

### API Endpoints

```http
# Send notification
POST /api/notifications
Content-Type: application/json
{
  "eventType": "OperationCompleted",
  "title": "Image Processing Complete",
  "message": "Successfully processed 10 images",
  "severity": "Success",
  "data": {
    "TotalImages": 10,
    "Duration": "5 minutes"
  }
}

# Send email
POST /api/notifications/email
{
  "subject": "Test Email",
  "body": "<h1>Test</h1><p>This is a test email.</p>",
  "recipients": ["user@company.com"]
}

# Send test notification
POST /api/notifications/test?channel=Slack

# Configure settings
POST /api/notifications/configure

# Get settings
GET /api/notifications/settings

# Register webhook
POST /api/notifications/webhook

# Unregister webhook
DELETE /api/notifications/webhook/{webhookId}

# Get notification history
GET /api/notifications/history?startDate=2025-01-01&eventType=OperationCompleted
```

---

## 3. Report Generation

### Supported Formats
1. **HTML** - Professional styled reports with tables
2. **JSON** - Machine-readable format
3. **Markdown** - Documentation-friendly format
4. **PDF** - Publication-quality documents with charts

### Report Types
- **Validation Reports** - Image validation results
- **Audit Reports** - Operation audit logs
- **Statistics Reports** - Performance metrics and analytics
- **Batch Operation Reports** - Batch execution summaries
- **System Health Reports** - Current system status

### Chart Types (PDF only)
- **Bar Charts** - Compare values across categories
- **Pie Charts** - Show proportions
- **Line Charts** - Time-series data
- **Progress Bars** - Visual progress indicators

### API Endpoints

```http
# Generate validation report
POST /api/reports/validation?format=Pdf
Content-Type: application/json
{
  "imagePath": "C:\\images\\install.wim",
  "status": "Completed",
  "totalChecks": 10,
  "passedChecks": 8,
  "failedChecks": 2
}

# Generate audit report
POST /api/reports/audit?startDate=2025-01-01&endDate=2025-01-31&format=Html

# Generate statistics report
POST /api/reports/statistics?startDate=2025-01-01&endDate=2025-01-31&format=Pdf

# Generate batch operation report
POST /api/reports/batchoperation?batchOperationId=batch-001&format=Html

# Get report
GET /api/reports/{reportId}

# List reports
GET /api/reports?type=Validation&startDate=2025-01-01

# Delete report
DELETE /api/reports/{reportId}

# Export report to different format
POST /api/reports/{reportId}/export?targetFormat=Pdf
```

### Example: Creating Report with Charts

```csharp
var report = new Report
{
    Type = ReportType.Statistics,
    Format = ReportFormat.Pdf,
    Title = "Monthly Performance Report",
    Description = "System performance for January 2025"
};

// Add bar chart section
report.Sections.Add(new ReportSection
{
    Title = "Operations by Type",
    Order = 1,
    Type = SectionType.Chart,
    Data = new Dictionary<string, object>
    {
        ["type"] = "bar",
        ["title"] = "Operations per Day",
        ["data"] = new Dictionary<string, double>
        {
            ["Monday"] = 45,
            ["Tuesday"] = 52,
            ["Wednesday"] = 48,
            ["Thursday"] = 50,
            ["Friday"] = 38
        }
    }
});

// Add progress bar
report.Sections.Add(new ReportSection
{
    Title = "System Utilization",
    Order = 2,
    Type = SectionType.Chart,
    Data = new Dictionary<string, object>
    {
        ["type"] = "progress",
        ["label"] = "CPU Usage",
        ["percentage"] = 75.5,
        ["color"] = "green"
    }
});
```

---

## 4. Health Monitoring

### Metrics Collected
- **CPU Usage** (0-100%)
- **Memory Usage** (0-100%)
- **Disk Usage** (0-100%)
- **Active Operations** Count
- **Uptime** Duration

### Alert Thresholds

```json
{
  "cpuThreshold": 90,
  "memoryThreshold": 85,
  "diskThreshold": 90,
  "maxConcurrentOperations": 10,
  "operationDurationThresholdMs": 300000,
  "enableCpuAlerts": true,
  "enableMemoryAlerts": true,
  "enableDiskAlerts": true,
  "enableOperationAlerts": true,
  "alertCooldownMinutes": 15
}
```

### API Endpoints

```http
# Get current health status (enhanced)
GET /api/health

Response:
{
  "status": "Healthy",
  "version": "1.0.0",
  "timestamp": "2025-01-08T10:00:00Z",
  "uptime": "2.05:30:15",
  "cpuUsage": 45.2,
  "memoryUsage": 62.5
}

# Get current metrics
GET /api/health/metrics

# Get historical metrics
GET /api/health/metrics/history?startDate=2025-01-08T00:00:00&endDate=2025-01-08T23:59:59

# Get performance statistics
GET /api/health/performance

# Configure alert thresholds
POST /api/health/alerts/configure
{
  "cpuThreshold": 85,
  "memoryThreshold": 80,
  "diskThreshold": 90
}

# Get alert configuration
GET /api/health/alerts

# Get alert history
GET /api/health/alerts/history?startDate=2025-01-01
```

### Performance Metrics Response

```json
{
  "timestamp": "2025-01-08T10:00:00Z",
  "totalOperations": 1523,
  "successfulOperations": 1489,
  "failedOperations": 34,
  "averageOperationDurationMs": 2543.5,
  "minOperationDurationMs": 150.2,
  "maxOperationDurationMs": 45632.1,
  "operationsPerMinute": 12.5,
  "requestsLastHour": 156,
  "requestsLastDay": 1523,
  "averageCpuUsage": 52.3,
  "averageMemoryUsage": 58.7,
  "peakCpuUsage": 89.2,
  "peakMemoryUsage": 78.4
}
```

---

## Data Storage

All Option B features store data in:
```
C:\ProgramData\DeployForge\
├── Reports\
│   ├── report_<uuid>.html
│   ├── report_<uuid>.pdf
│   └── report_<uuid>.json
├── Notifications\
│   └── settings.json
└── Scheduling\
    ├── schedules.json
    └── history.json
```

---

## Security Considerations

### Email
- Use app-specific passwords for Gmail
- Store credentials securely
- Use SSL/TLS for SMTP connections

### Webhooks
- Implement HMAC signature verification
- Use HTTPS endpoints only
- Validate incoming payloads

### Slack/Teams
- Protect webhook URLs (treat as secrets)
- Rotate URLs periodically
- Monitor usage for anomalies

---

## Integration Examples

### Schedule with Notification

```csharp
// Create schedule
var schedule = new Schedule
{
    Name = "Daily Validation",
    CronExpression = "0 2 * * *", // 2 AM daily
    BatchOperationId = "validate-all-images",
    Policy = new SchedulePolicy
    {
        NotifyOnCompletion = true,
        NotifyOnFailure = true
    }
};

await scheduleService.CreateScheduleAsync(schedule);

// Configure notification rule
var rule = new NotificationRule
{
    Name = "Validation Alerts",
    EventType = NotificationEventType.ValidationCompleted,
    Channels = new List<NotificationChannel>
    {
        NotificationChannel.Email,
        NotificationChannel.Slack
    },
    Recipients = new List<string> { "admin@company.com" }
};
```

### Generate Report and Send via Email

```csharp
// Generate PDF report
var report = await reportService.GenerateValidationReportAsync(
    validationResult,
    ReportFormat.Pdf,
    outputPath: "C:\\Reports\\validation.pdf");

// Send email with report
await notificationService.SendEmailAsync(
    subject: "Validation Report Ready",
    body: $"<p>Validation report generated: {report.Data.FilePath}</p>",
    recipients: new List<string> { "team@company.com" });
```

---

## Troubleshooting

### Email Not Sending
1. Check SMTP credentials
2. Verify port and SSL settings
3. Check firewall rules
4. For Gmail: Enable "Less secure app access" or use app-specific password

### Slack Messages Not Appearing
1. Verify webhook URL is correct
2. Check channel permissions
3. Verify JSON payload format
4. Check Slack webhook logs

### Schedule Not Executing
1. Verify cron expression is valid
2. Check if schedule is enabled
3. Verify maintenance windows
4. Check execution history for errors

### PDF Generation Failing
1. Ensure QuestPDF is installed
2. Check write permissions to reports directory
3. Verify sufficient disk space

---

## Performance Tips

1. **Scheduling**: Don't schedule too many operations simultaneously
2. **Notifications**: Use notification rules to avoid spam
3. **Reports**: Generate large reports asynchronously
4. **Monitoring**: Metrics collection runs every 5 seconds - adjust if needed

---

## License Notes

- **QuestPDF**: Community license for open-source projects
- **MailKit**: MIT License
- **Quartz.NET**: Apache License 2.0

---

## Support

For issues, feature requests, or contributions:
- GitHub: https://github.com/Cornman92/DeployForge
- Issues: https://github.com/Cornman92/DeployForge/issues

---

*Last Updated: 2025-01-08*
