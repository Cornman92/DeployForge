#Requires -Version 5.1

<#
.SYNOPSIS
    DeployForge Exception Handling Module
    
.DESCRIPTION
    Provides custom exception types and error handling utilities for DeployForge operations.
#>

# Custom exception classes
class DeployForgeException : System.Exception {
    [string]$Operation
    [string]$Details
    
    DeployForgeException([string]$message) : base($message) {
        $this.Operation = "Unknown"
        $this.Details = ""
    }
    
    DeployForgeException([string]$message, [string]$operation) : base($message) {
        $this.Operation = $operation
        $this.Details = ""
    }
    
    DeployForgeException([string]$message, [string]$operation, [string]$details) : base($message) {
        $this.Operation = $operation
        $this.Details = $details
    }
}

class ImageNotFoundException : DeployForgeException {
    [string]$ImagePath
    
    ImageNotFoundException([string]$imagePath) : base("Image not found: $imagePath", "ImageLoad") {
        $this.ImagePath = $imagePath
    }
}

class MountException : DeployForgeException {
    [string]$MountPath
    
    MountException([string]$message, [string]$mountPath) : base($message, "Mount") {
        $this.MountPath = $mountPath
    }
}

class RegistryException : DeployForgeException {
    [string]$Hive
    [string]$Path
    
    RegistryException([string]$message, [string]$hive, [string]$path) : base($message, "Registry") {
        $this.Hive = $hive
        $this.Path = $path
    }
}

class ValidationException : DeployForgeException {
    [string]$Parameter
    [object]$Value
    
    ValidationException([string]$message, [string]$parameter, [object]$value) : base($message, "Validation") {
        $this.Parameter = $parameter
        $this.Value = $value
    }
}

class DismException : DeployForgeException {
    [int]$ExitCode
    [string]$DismOutput
    
    DismException([string]$message, [int]$exitCode, [string]$output) : base($message, "DISM") {
        $this.ExitCode = $exitCode
        $this.DismOutput = $output
    }
}

# Error handling functions
function New-DeployForgeError {
    <#
    .SYNOPSIS
        Creates a standardized DeployForge error object.
        
    .PARAMETER Message
        Error message.
        
    .PARAMETER Operation
        The operation that failed.
        
    .PARAMETER Details
        Additional details about the error.
        
    .PARAMETER Exception
        The underlying exception if available.
    #>
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,
        
        [Parameter(Mandatory = $false)]
        [string]$Operation = "Unknown",
        
        [Parameter(Mandatory = $false)]
        [string]$Details = "",
        
        [Parameter(Mandatory = $false)]
        [System.Exception]$Exception
    )
    
    $error = [PSCustomObject]@{
        Timestamp = Get-Date
        Operation = $Operation
        Message = $Message
        Details = $Details
        Success = $false
    }
    
    if ($Exception) {
        $error | Add-Member -NotePropertyName "ExceptionType" -NotePropertyValue $Exception.GetType().Name
        $error | Add-Member -NotePropertyName "ExceptionMessage" -NotePropertyValue $Exception.Message
        $error | Add-Member -NotePropertyName "StackTrace" -NotePropertyValue $Exception.StackTrace
    }
    
    return $error
}

function Write-DeployForgeError {
    <#
    .SYNOPSIS
        Writes a DeployForge error with consistent formatting.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,
        
        [Parameter(Mandatory = $false)]
        [string]$Operation = "Unknown",
        
        [Parameter(Mandatory = $false)]
        [System.Exception]$Exception,
        
        [Parameter(Mandatory = $false)]
        [switch]$ThrowError
    )
    
    $errorObj = New-DeployForgeError -Message $Message -Operation $Operation -Exception $Exception
    
    Write-Host "✗ ERROR: $Message" -ForegroundColor Red
    if ($Operation -ne "Unknown") {
        Write-Host "  Operation: $Operation" -ForegroundColor DarkRed
    }
    if ($Exception) {
        Write-Host "  Exception: $($Exception.Message)" -ForegroundColor DarkRed
    }
    
    if ($ThrowError) {
        throw [DeployForgeException]::new($Message, $Operation)
    }
    
    return $errorObj
}

function Test-DeployForgeResult {
    <#
    .SYNOPSIS
        Tests if a DeployForge operation result indicates success.
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param(
        [Parameter(Mandatory = $true, ValueFromPipeline = $true)]
        [PSCustomObject]$Result
    )
    
    process {
        if ($Result.PSObject.Properties.Name -contains 'Success') {
            return $Result.Success -eq $true
        }
        return $true
    }
}

# DISM error code mappings
$script:DismErrorCodes = @{
    0 = "Success"
    2 = "The system cannot find the file specified"
    5 = "Access denied"
    50 = "The request is not supported"
    87 = "The parameter is incorrect"
    1168 = "Element not found"
    14098 = "The resource loader cache doesn't have loaded MUI entry"
}

function Get-DismErrorMessage {
    <#
    .SYNOPSIS
        Gets a human-readable message for a DISM error code.
    #>
    [CmdletBinding()]
    [OutputType([string])]
    param(
        [Parameter(Mandatory = $true)]
        [int]$ErrorCode
    )
    
    if ($script:DismErrorCodes.ContainsKey($ErrorCode)) {
        return $script:DismErrorCodes[$ErrorCode]
    }
    
    return "Unknown DISM error (code: $ErrorCode)"
}

# Export functions and classes
Export-ModuleMember -Function @(
    'New-DeployForgeError',
    'Write-DeployForgeError',
    'Test-DeployForgeResult',
    'Get-DismErrorMessage'
)
