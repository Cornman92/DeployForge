#Requires -Version 5.1

<#
.SYNOPSIS
    Logging utilities for DeployForge.

.DESCRIPTION
    Provides structured logging with multiple output targets and severity levels.
#>

# Log level enumeration
enum DFLogLevel {
    Verbose = 0
    Debug = 1
    Info = 2
    Warning = 3
    Error = 4
    Critical = 5
}

# Log configuration
$script:DFLogConfig = @{
    MinLevel = [DFLogLevel]::Info
    LogToFile = $true
    LogToConsole = $true
    LogPath = Join-Path $env:TEMP "DeployForge\Logs"
    MaxLogFiles = 10
    MaxLogSizeMB = 50
    UseTimestamp = $true
    UseColors = $true
}

# Initialize logging
function Initialize-DFLogging {
    <#
    .SYNOPSIS
        Initializes the logging system.
    #>
    [CmdletBinding()]
    param(
        [DFLogLevel]$MinLevel = [DFLogLevel]::Info,
        [string]$LogPath,
        [switch]$NoConsole,
        [switch]$NoFile
    )

    $script:DFLogConfig.MinLevel = $MinLevel
    
    if ($LogPath) {
        $script:DFLogConfig.LogPath = $LogPath
    }
    
    $script:DFLogConfig.LogToConsole = -not $NoConsole.IsPresent
    $script:DFLogConfig.LogToFile = -not $NoFile.IsPresent

    # Ensure log directory exists
    if ($script:DFLogConfig.LogToFile) {
        if (-not (Test-Path $script:DFLogConfig.LogPath)) {
            New-Item -ItemType Directory -Path $script:DFLogConfig.LogPath -Force | Out-Null
        }
    }
}

# Main logging function
function Write-DFLog {
    <#
    .SYNOPSIS
        Writes a log message.

    .PARAMETER Message
        The message to log.

    .PARAMETER Level
        The log level (Verbose, Debug, Info, Warning, Error, Critical).

    .PARAMETER Exception
        Optional exception to log.

    .PARAMETER NoNewLine
        Don't append newline to console output.

    .EXAMPLE
        Write-DFLog -Message "Operation completed" -Level Info

    .EXAMPLE
        Write-DFLog -Message "An error occurred" -Level Error -Exception $_.Exception
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Message,

        [Parameter(Position = 1)]
        [DFLogLevel]$Level = [DFLogLevel]::Info,

        [System.Exception]$Exception,

        [switch]$NoNewLine
    )

    # Check if we should log at this level
    if ([int]$Level -lt [int]$script:DFLogConfig.MinLevel) {
        return
    }

    # Build timestamp
    $timestamp = if ($script:DFLogConfig.UseTimestamp) {
        "[{0:yyyy-MM-dd HH:mm:ss}]" -f (Get-Date)
    } else { "" }

    # Build log entry
    $levelTag = "[$($Level.ToString().ToUpper().PadRight(7))]"
    $logEntry = "$timestamp $levelTag $Message"

    if ($Exception) {
        $logEntry += "`n  Exception: $($Exception.GetType().Name): $($Exception.Message)"
        if ($Exception.StackTrace) {
            $logEntry += "`n  StackTrace: $($Exception.StackTrace)"
        }
    }

    # Console output with colors
    if ($script:DFLogConfig.LogToConsole) {
        $color = switch ($Level) {
            'Verbose' { 'DarkGray' }
            'Debug'   { 'Gray' }
            'Info'    { 'White' }
            'Warning' { 'Yellow' }
            'Error'   { 'Red' }
            'Critical' { 'Magenta' }
            default   { 'White' }
        }

        if ($script:DFLogConfig.UseColors) {
            if ($NoNewLine) {
                Write-Host $logEntry -ForegroundColor $color -NoNewline
            }
            else {
                Write-Host $logEntry -ForegroundColor $color
            }
        }
        else {
            if ($NoNewLine) {
                Write-Host $logEntry -NoNewline
            }
            else {
                Write-Host $logEntry
            }
        }
    }

    # File output
    if ($script:DFLogConfig.LogToFile) {
        $logFile = Join-Path $script:DFLogConfig.LogPath "DeployForge_$(Get-Date -Format 'yyyyMMdd').log"
        Add-Content -Path $logFile -Value $logEntry -ErrorAction SilentlyContinue
    }
}

# Convenience functions
function Write-DFVerbose {
    param([string]$Message)
    Write-DFLog -Message $Message -Level Verbose
}

function Write-DFDebug {
    param([string]$Message)
    Write-DFLog -Message $Message -Level Debug
}

function Write-DFInfo {
    param([string]$Message)
    Write-DFLog -Message $Message -Level Info
}

function Write-DFWarning {
    param([string]$Message)
    Write-DFLog -Message $Message -Level Warning
}

function Write-DFError {
    param([string]$Message, [System.Exception]$Exception)
    Write-DFLog -Message $Message -Level Error -Exception $Exception
}

function Write-DFCritical {
    param([string]$Message, [System.Exception]$Exception)
    Write-DFLog -Message $Message -Level Critical -Exception $Exception
}

# Get current log file
function Get-DFLogFile {
    <#
    .SYNOPSIS
        Gets the current log file path.
    #>
    $logFile = Join-Path $script:DFLogConfig.LogPath "DeployForge_$(Get-Date -Format 'yyyyMMdd').log"
    return $logFile
}

# Clear old log files
function Clear-DFLogs {
    <#
    .SYNOPSIS
        Clears old log files, keeping the most recent ones.

    .PARAMETER KeepCount
        Number of log files to keep.
    #>
    [CmdletBinding()]
    param(
        [int]$KeepCount = 10
    )

    $logFiles = Get-ChildItem -Path $script:DFLogConfig.LogPath -Filter "DeployForge_*.log" |
        Sort-Object LastWriteTime -Descending |
        Select-Object -Skip $KeepCount

    foreach ($file in $logFiles) {
        Remove-Item $file.FullName -Force
        Write-DFLog -Message "Removed old log file: $($file.Name)" -Level Debug
    }
}

# Export log to file
function Export-DFLog {
    <#
    .SYNOPSIS
        Exports logs to a specified file.

    .PARAMETER Path
        Output file path.

    .PARAMETER Days
        Number of days of logs to export.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [int]$Days = 7
    )

    $startDate = (Get-Date).AddDays(-$Days)
    $logFiles = Get-ChildItem -Path $script:DFLogConfig.LogPath -Filter "DeployForge_*.log" |
        Where-Object { $_.LastWriteTime -ge $startDate }

    $allLogs = $logFiles | ForEach-Object { Get-Content $_.FullName }
    $allLogs | Set-Content -Path $Path

    Write-DFLog -Message "Exported $($logFiles.Count) log files to $Path" -Level Info
}

# Initialize on load
Initialize-DFLogging

Write-Verbose "Loaded DeployForge logging utilities"
