# Getting Started with DeployForge Desktop

Welcome to DeployForge Desktop! This guide will help you get up and running with the WPF desktop application.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [First Launch](#first-launch)
4. [Connecting to the API](#connecting-to-the-api)
5. [Basic Workflow](#basic-workflow)
6. [Next Steps](#next-steps)

---

## Prerequisites

### System Requirements

- **Operating System**: Windows 10/11 (64-bit)
- **RAM**: 4 GB minimum, 8 GB recommended
- **Disk Space**: 500 MB for application, additional space for images
- **.NET Runtime**: .NET 8.0 Runtime (Desktop) - automatically installed

### Backend Requirements

- **DeployForge API**: Running instance of DeployForge.Api
- **Network Access**: HTTP/HTTPS access to the API server
- **Port**: Default 5000 (HTTP) or 5001 (HTTPS)

---

## Installation

### Option 1: Installer (Recommended)

1. Download `DeployForgeSetup.exe` from the releases page
2. Run the installer with administrator privileges
3. Follow the installation wizard
4. Launch DeployForge from the Start menu

### Option 2: Portable Version

1. Download `DeployForge-Portable.zip`
2. Extract to your preferred location
3. Run `DeployForge.Desktop.exe`

### Option 3: Build from Source

```bash
git clone https://github.com/Cornman92/DeployForge.git
cd DeployForge/src/desktop/DeployForge.Desktop
dotnet build -c Release
dotnet run --project DeployForge.Desktop.csproj
```

---

## First Launch

### Initial Configuration Wizard

When you first launch DeployForge Desktop, you'll see the initial configuration wizard:

#### Step 1: API Connection

1. Enter your API Base URL (e.g., `http://localhost:5000` or `https://api.deployforge.local`)
2. Choose HTTP or HTTPS
3. Set timeout (default: 30 seconds)
4. Click **Test Connection** to verify
5. Click **Next**

#### Step 2: Application Preferences

1. Select your preferred theme (Light, Dark, or System)
2. Choose language (English, Spanish, French, German)
3. Configure update preferences
4. Click **Next**

#### Step 3: Feature Configuration

1. Enable desired features:
   - ✓ Image Management (always enabled)
   - ✓ Real-time Monitoring
   - ✓ Scheduled Operations
   - ✓ Report Generation
   - ✓ Notifications
2. Click **Finish**

### Main Window

After configuration, you'll see the main DeployForge window with:

- **Left Navigation Bar**: Access all features
- **Content Area**: Main workspace
- **Status Bar**: Connection status and notifications

---

## Connecting to the API

### Manual Configuration

If you need to change API settings later:

1. Click **Settings** in the navigation bar
2. Select the **General** tab
3. Update **API Connection** settings:
   - API Base URL
   - Timeout
   - HTTPS toggle
4. Click **Test Connection**
5. Click **Save Settings**

### Connection Status

The status bar shows your connection status:

- 🟢 **Connected**: API is reachable
- 🟡 **Connecting**: Attempting to connect
- 🔴 **Disconnected**: Cannot reach API

### Troubleshooting Connection Issues

#### "Connection Refused"

- Verify the API is running: `curl http://localhost:5000/health`
- Check firewall settings
- Verify the URL and port are correct

#### "Timeout"

- Increase timeout in Settings > General > API Connection
- Check network connectivity
- Verify API server performance

#### "SSL Certificate Error"

- For development: Disable HTTPS or use HTTP
- For production: Install valid SSL certificate
- Trust self-signed certificate in Windows

---

## Basic Workflow

### 1. Dashboard Overview

The Dashboard shows:
- System health status
- Active operations count
- Recent activity
- Quick actions

### 2. Image Management

Navigate to **Images** to:
- Mount/unmount images
- View image details
- Perform operations (optimize, cleanup, etc.)
- Create image templates

### 3. Monitoring (Option B Feature)

Navigate to **Monitoring** to:
- View real-time CPU, Memory, Disk usage
- See active operations
- Review alert history
- Configure alert thresholds

### 4. Scheduled Operations (Option B Feature)

Navigate to **Schedules** to:
- Create new schedules
- View execution history
- Enable/disable schedules
- Manually trigger execution

### 5. Reports (Option B Feature)

Navigate to **Reports** to:
- Generate validation reports
- Export audit logs
- Create performance statistics
- Download reports in PDF/HTML/JSON

### 6. Notifications (Option B Feature)

Navigate to **Notifications** to:
- View notification history
- Configure channels (Email, Slack, Teams)
- Test notification delivery
- Manage notification rules

---

## Next Steps

### Configure Features

1. **Set Up Monitoring Alerts**
   - Go to Settings > Monitoring
   - Adjust CPU/Memory/Disk thresholds
   - Click "Apply Alert Thresholds"

2. **Configure Notifications**
   - Go to Settings > Notifications
   - Enable desired channels (Email, Slack, Teams, Webhooks)
   - Enter credentials/webhook URLs
   - Test each channel
   - Save settings

3. **Create Your First Schedule**
   - Navigate to Schedules
   - Click "Create Schedule"
   - Enter name and description
   - Set cron expression (e.g., `0 2 * * *` for daily at 2 AM)
   - Select batch operation
   - Enable notifications
   - Save schedule

4. **Generate Your First Report**
   - Navigate to Reports
   - Click "Generate Report"
   - Select type (Validation, Audit, Statistics)
   - Choose format (PDF, HTML, JSON)
   - Configure options
   - Generate and download

### Learn More

- [**User Guide**](./USER_GUIDE.md) - Complete feature documentation
- [**Configuration Guide**](./CONFIGURATION_GUIDE.md) - Advanced settings
- [**Troubleshooting**](./TROUBLESHOOTING.md) - Common issues and solutions
- [**API Documentation**](../OPTION_B_FEATURES.md) - Backend API reference

### Get Help

- **GitHub Issues**: https://github.com/Cornman92/DeployForge/issues
- **Discussions**: https://github.com/Cornman92/DeployForge/discussions
- **Wiki**: https://github.com/Cornman92/DeployForge/wiki

---

## Tips for Success

1. **Start with Monitoring**: Enable monitoring first to understand your system baseline
2. **Test Notifications**: Always test notification channels before relying on them
3. **Validate Cron**: Use the cron validator in the Schedules view
4. **Check Logs**: View application logs via Settings > Logging > Open Log Directory
5. **Regular Backups**: Use the backup feature before major operations

---

**Next**: [Complete User Guide](./USER_GUIDE.md) →

---

*Last Updated: 2025-01-08*
