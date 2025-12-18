function New-ImageBuild {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$true)]
        [string]$ImagePath,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Config
    )

    Process {
        Write-Progress -Activity "Building Image" -Status "Starting..." -PercentComplete 0
        
        # 1. Mount
        $Context = Mount-DeployImage -ImagePath $ImagePath
        $MountDir = $Context.MountDir
        
        try {
            # 2. Privacy
            if ($Config.Privacy) {
                Write-Progress -Activity "Building Image" -Status "Applying Privacy Settings..." -PercentComplete 20
                Enable-PrivacyHardening -MountDir $MountDir -Config $Config.Privacy
            }

            # 3. Gaming
            if ($Config.Gaming) {
                Write-Progress -Activity "Building Image" -Status "Applying Gaming Optimizations..." -PercentComplete 40
                Enable-GamingOptimizations -MountDir $MountDir -Profile $Config.Gaming.Profile
            }

            # 4. Devenv
            if ($Config.Devenv) {
                Write-Progress -Activity "Building Image" -Status "Installing Dev Environment..." -PercentComplete 60
                Install-DevEnvironment -MountDir $MountDir -Profile $Config.Devenv.Profile
            }

            # 5. Apps
            if ($Config.Apps) {
                Write-Progress -Activity "Building Image" -Status "Installing Applications..." -PercentComplete 80
                Install-Applications -MountDir $MountDir -AppList $Config.Apps
            }

            # 6. UI
            if ($Config.UI) {
                Write-Progress -Activity "Building Image" -Status "Customizing UI..." -PercentComplete 90
                Set-WindowsUI -MountDir $MountDir -Profile $Config.UI.Profile
            }

        }
        catch {
            Write-Error "Build failed: $_"
            Dismount-DeployImage -MountDir $MountDir -SaveChanges:$false
            throw
        }
        
        # 7. Dismount
        Write-Progress -Activity "Building Image" -Status "Saving Changes..." -PercentComplete 100
        Dismount-DeployImage -MountDir $MountDir -SaveChanges:$true
    }
}
