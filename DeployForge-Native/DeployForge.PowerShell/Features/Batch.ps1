#Requires -Version 5.1
# Batch operations module for DeployForge

function Start-DFBatchOperation {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string[]]$ImagePaths,
        [Parameter(Mandatory)][scriptblock]$Operation,
        [string]$Description = "Processing images",
        [int]$MaxParallel = 4
    )
    
    Write-DFLog "Starting batch operation: $Description ($($ImagePaths.Count) images)" -Level Info
    
    $results = @()
    $tracker = New-DFProgressTracker -Activity $Description -TotalSteps $ImagePaths.Count
    
    foreach ($imagePath in $ImagePaths) {
        $step = $ImagePaths.IndexOf($imagePath) + 1
        Update-DFProgress -Tracker $tracker -Status "Processing $(Split-Path $imagePath -Leaf)..." -Step $step
        
        try {
            $result = & $Operation $imagePath
            $results += @{ Image = $imagePath; Status = "Success"; Result = $result }
            Write-DFLog "Completed: $imagePath" -Level Verbose
        }
        catch {
            $results += @{ Image = $imagePath; Status = "Failed"; Error = $_.Exception.Message }
            Write-DFLog "Failed: $imagePath - $($_.Exception.Message)" -Level Error
        }
    }
    
    Complete-DFProgress -Tracker $tracker
    
    $successful = ($results | Where-Object { $_.Status -eq "Success" }).Count
    $failed = ($results | Where-Object { $_.Status -eq "Failed" }).Count
    
    Write-DFLog "Batch complete: $successful successful, $failed failed" -Level Info
    return $results
}

function Get-DFBatchResult {
    [CmdletBinding()]
    param([Parameter(Mandatory)][hashtable[]]$Results)
    
    return @{
        Total = $Results.Count
        Successful = ($Results | Where-Object { $_.Status -eq "Success" }).Count
        Failed = ($Results | Where-Object { $_.Status -eq "Failed" }).Count
        Details = $Results
    }
}

function Export-DFBatchReport {
    [CmdletBinding()]
    param([Parameter(Mandatory)][hashtable[]]$Results, [Parameter(Mandatory)][string]$OutputPath, [ValidateSet('json','csv','text')][string]$Format = 'json')
    
    switch ($Format) {
        'json' { $Results | ConvertTo-Json -Depth 5 | Set-Content $OutputPath -Encoding UTF8 }
        'csv' { $Results | ForEach-Object { [PSCustomObject]$_ } | Export-Csv $OutputPath -NoTypeInformation }
        'text' { $Results | ForEach-Object { "Image: $($_.Image)`nStatus: $($_.Status)`n$('-'*40)" } | Set-Content $OutputPath }
    }
    Write-DFLog "Batch report exported to $OutputPath" -Level Info
}

Write-Verbose "Loaded DeployForge Batch module"
