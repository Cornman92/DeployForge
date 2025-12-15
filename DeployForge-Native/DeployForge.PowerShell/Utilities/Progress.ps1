#Requires -Version 5.1

<#
.SYNOPSIS
    Progress tracking utilities for DeployForge.

.DESCRIPTION
    Provides progress bar and status tracking for long-running operations.
#>

# Progress state class
class DFProgressState {
    [string]$Activity
    [string]$Status
    [int]$PercentComplete
    [int]$CurrentStep
    [int]$TotalSteps
    [datetime]$StartTime
    [datetime]$LastUpdate
    [timespan]$Elapsed
    [timespan]$EstimatedRemaining
    [bool]$IsComplete

    DFProgressState([string]$activity, [int]$totalSteps) {
        $this.Activity = $activity
        $this.TotalSteps = $totalSteps
        $this.CurrentStep = 0
        $this.PercentComplete = 0
        $this.StartTime = Get-Date
        $this.LastUpdate = Get-Date
        $this.IsComplete = $false
    }

    [void] Update([string]$status, [int]$step) {
        $this.Status = $status
        $this.CurrentStep = $step
        $this.PercentComplete = [math]::Min(100, [math]::Floor(($step / $this.TotalSteps) * 100))
        $this.LastUpdate = Get-Date
        $this.Elapsed = $this.LastUpdate - $this.StartTime

        if ($step -gt 0) {
            $avgTimePerStep = $this.Elapsed.TotalSeconds / $step
            $remainingSteps = $this.TotalSteps - $step
            $this.EstimatedRemaining = [timespan]::FromSeconds($avgTimePerStep * $remainingSteps)
        }
    }

    [void] Complete() {
        $this.PercentComplete = 100
        $this.IsComplete = $true
        $this.LastUpdate = Get-Date
        $this.Elapsed = $this.LastUpdate - $this.StartTime
    }

    [hashtable] ToHashtable() {
        return @{
            Activity = $this.Activity
            Status = $this.Status
            PercentComplete = $this.PercentComplete
            CurrentStep = $this.CurrentStep
            TotalSteps = $this.TotalSteps
            Elapsed = $this.Elapsed.ToString("hh\:mm\:ss")
            EstimatedRemaining = $this.EstimatedRemaining.ToString("hh\:mm\:ss")
            IsComplete = $this.IsComplete
        }
    }
}

# Active progress tracking
$script:DFActiveProgress = @{}
$script:DFProgressId = 0

function Show-DFProgress {
    <#
    .SYNOPSIS
        Shows or updates a progress bar.

    .PARAMETER Activity
        The activity name.

    .PARAMETER Status
        Current status message.

    .PARAMETER PercentComplete
        Completion percentage (0-100).

    .PARAMETER Id
        Progress bar ID for tracking.

    .PARAMETER ParentId
        Parent progress bar ID.

    .PARAMETER Complete
        Mark as complete and remove.

    .EXAMPLE
        Show-DFProgress -Activity "Installing" -Status "Step 1" -PercentComplete 25

    .EXAMPLE
        Show-DFProgress -Activity "Installing" -Complete
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Activity,

        [string]$Status = "Processing...",

        [ValidateRange(0, 100)]
        [int]$PercentComplete = -1,

        [int]$Id = 0,

        [int]$ParentId = -1,

        [switch]$Complete
    )

    if ($Complete) {
        Write-Progress -Activity $Activity -Completed -Id $Id
        $script:DFActiveProgress.Remove($Id)
        return
    }

    $params = @{
        Activity = $Activity
        Status = $Status
        Id = $Id
    }

    if ($PercentComplete -ge 0) {
        $params['PercentComplete'] = $PercentComplete
    }

    if ($ParentId -ge 0) {
        $params['ParentId'] = $ParentId
    }

    Write-Progress @params

    # Track active progress
    if (-not $script:DFActiveProgress.ContainsKey($Id)) {
        $script:DFActiveProgress[$Id] = @{
            Activity = $Activity
            StartTime = Get-Date
        }
    }
    $script:DFActiveProgress[$Id]['Status'] = $Status
    $script:DFActiveProgress[$Id]['PercentComplete'] = $PercentComplete
    $script:DFActiveProgress[$Id]['LastUpdate'] = Get-Date
}

function New-DFProgressTracker {
    <#
    .SYNOPSIS
        Creates a new progress tracker for step-based operations.

    .PARAMETER Activity
        The activity name.

    .PARAMETER TotalSteps
        Total number of steps.

    .EXAMPLE
        $tracker = New-DFProgressTracker -Activity "Building Image" -TotalSteps 10
        $tracker.Update("Step 1", 1)
    #>
    [CmdletBinding()]
    [OutputType([DFProgressState])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Activity,

        [Parameter(Mandatory = $true)]
        [int]$TotalSteps
    )

    return [DFProgressState]::new($Activity, $TotalSteps)
}

function Update-DFProgress {
    <#
    .SYNOPSIS
        Updates progress using a tracker.

    .PARAMETER Tracker
        Progress tracker object.

    .PARAMETER Status
        Current status message.

    .PARAMETER Step
        Current step number.

    .PARAMETER Id
        Progress bar ID.

    .EXAMPLE
        Update-DFProgress -Tracker $tracker -Status "Processing files" -Step 3
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [DFProgressState]$Tracker,

        [Parameter(Mandatory = $true)]
        [string]$Status,

        [Parameter(Mandatory = $true)]
        [int]$Step,

        [int]$Id = 0
    )

    $Tracker.Update($Status, $Step)

    $remainingText = if ($Tracker.EstimatedRemaining.TotalSeconds -gt 0) {
        " (ETA: $($Tracker.EstimatedRemaining.ToString('mm\:ss')))"
    } else { "" }

    Show-DFProgress -Activity $Tracker.Activity `
        -Status "$Status$remainingText" `
        -PercentComplete $Tracker.PercentComplete `
        -Id $Id
}

function Complete-DFProgress {
    <#
    .SYNOPSIS
        Completes and removes a progress tracker.

    .PARAMETER Tracker
        Progress tracker object.

    .PARAMETER Id
        Progress bar ID.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [DFProgressState]$Tracker,

        [int]$Id = 0
    )

    $Tracker.Complete()
    Show-DFProgress -Activity $Tracker.Activity -Complete -Id $Id
}

# Progress callback for external use
function New-DFProgressCallback {
    <#
    .SYNOPSIS
        Creates a scriptblock callback for progress reporting.

    .PARAMETER Activity
        Activity name for the progress bar.

    .EXAMPLE
        $callback = New-DFProgressCallback -Activity "Downloading"
        & $callback 50 "Downloading file..."
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Activity
    )

    $callback = {
        param([int]$Percent, [string]$Status)
        Show-DFProgress -Activity $using:Activity -Status $Status -PercentComplete $Percent
    }.GetNewClosure()

    return $callback
}

# Spinner for indeterminate progress
function Show-DFSpinner {
    <#
    .SYNOPSIS
        Shows an indeterminate spinner.

    .PARAMETER Activity
        Activity name.

    .PARAMETER Status
        Current status.

    .PARAMETER Duration
        Duration to show spinner (seconds).
    #>
    [CmdletBinding()]
    param(
        [string]$Activity = "Processing",
        [string]$Status = "Please wait...",
        [int]$Duration = 0
    )

    $spinChars = @('|', '/', '-', '\')
    $i = 0
    $startTime = Get-Date

    while ($true) {
        $spin = $spinChars[$i % 4]
        Write-Host "`r$spin $Activity - $Status" -NoNewline -ForegroundColor Cyan
        
        Start-Sleep -Milliseconds 100
        $i++

        if ($Duration -gt 0 -and ((Get-Date) - $startTime).TotalSeconds -ge $Duration) {
            break
        }
    }

    Write-Host ""
}

Write-Verbose "Loaded DeployForge progress utilities"
