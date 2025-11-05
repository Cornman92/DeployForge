BeforeAll {
    # Import module
    Import-Module "$PSScriptRoot/../../src/powershell/DeployForge.psd1" -Force
}

Describe 'Mount-DFImage' {
    It 'Should have proper parameter validation' {
        { Mount-DFImage -Path 'NonExistent.wim' -Index 1 } | Should -Throw
    }

    It 'Should require administrator privileges' {
        Mock Test-Administrator { return $false }
        { Mount-DFImage -Path 'TestDrive:\test.wim' -Index 1 } | Should -Throw "*administrative privileges*"
    }
}

Describe 'Dismount-DFImage' {
    It 'Should have proper parameter validation' {
        { Dismount-DFImage -MountPath 'NonExistent' } | Should -Throw
    }

    It 'Should not allow both Save and Discard' {
        { Dismount-DFImage -MountPath 'C:\Mount' -Save -Discard } | Should -Throw "*both*"
    }
}

Describe 'Get-DFImageInfo' {
    It 'Should have proper parameter validation' {
        { Get-DFImageInfo -Path 'NonExistent.wim' } | Should -Throw
    }

    It 'Should accept pipeline input' {
        $cmd = Get-Command Get-DFImageInfo
        $pathParam = $cmd.Parameters['Path']
        $pathParam.Attributes.ValueFromPipeline | Should -Be $true
    }
}

Describe 'Get-DFComponent' {
    It 'Should require administrator privileges' {
        Mock Test-Administrator { return $false }
        { Get-DFComponent -MountPath 'C:\Mount' } | Should -Throw "*administrative privileges*"
    }

    It 'Should accept valid Type values' {
        $cmd = Get-Command Get-DFComponent
        $typeParam = $cmd.Parameters['Type']
        $validValues = $typeParam.Attributes | Where-Object { $_ -is [System.Management.Automation.ValidateSetAttribute] }
        $validValues.ValidValues | Should -Contain 'Package'
        $validValues.ValidValues | Should -Contain 'Feature'
        $validValues.ValidValues | Should -Contain 'Capability'
        $validValues.ValidValues | Should -Contain 'All'
    }
}

Describe 'Remove-DFComponent' {
    It 'Should support WhatIf' {
        $cmd = Get-Command Remove-DFComponent
        $cmd.Parameters.ContainsKey('WhatIf') | Should -Be $true
    }

    It 'Should require administrator privileges' {
        Mock Test-Administrator { return $false }
        { Remove-DFComponent -MountPath 'C:\Mount' -Name 'Test' -Type 'Package' } | Should -Throw "*administrative privileges*"
    }
}
