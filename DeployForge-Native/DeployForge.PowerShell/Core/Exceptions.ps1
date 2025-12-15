#Requires -Version 5.1

<#
.SYNOPSIS
    Custom exception classes for DeployForge.

.DESCRIPTION
    Defines custom exception types for error handling throughout the module.
#>

# Base exception class for all DeployForge errors
class DFException : System.Exception {
    [string]$Operation
    [datetime]$Timestamp

    DFException() : base() {
        $this.Timestamp = Get-Date
    }

    DFException([string]$message) : base($message) {
        $this.Timestamp = Get-Date
    }

    DFException([string]$message, [System.Exception]$innerException) : base($message, $innerException) {
        $this.Timestamp = Get-Date
    }

    [string] ToString() {
        $result = "[DeployForge Error] $($this.Message)"
        if ($this.Operation) {
            $result += " (Operation: $($this.Operation))"
        }
        return $result
    }
}

# Image not found exception
class DFImageNotFoundException : DFException {
    [string]$ImagePath

    DFImageNotFoundException([string]$path) : base("Image file not found: $path") {
        $this.ImagePath = $path
        $this.Operation = "ImageValidation"
    }
}

# Unsupported format exception
class DFUnsupportedFormatException : DFException {
    [string]$Format
    [string[]]$SupportedFormats

    DFUnsupportedFormatException([string]$message) : base($message) {
        $this.Operation = "FormatDetection"
    }

    DFUnsupportedFormatException([string]$format, [string[]]$supported) : base(
        "Unsupported image format: $format. Supported formats: $($supported -join ', ')"
    ) {
        $this.Format = $format
        $this.SupportedFormats = $supported
        $this.Operation = "FormatDetection"
    }
}

# Mount operation exception
class DFMountException : DFException {
    [string]$ImagePath
    [string]$MountPoint
    [int]$DismErrorCode

    DFMountException([string]$message) : base($message) {
        $this.Operation = "Mount"
    }

    DFMountException([string]$imagePath, [string]$mountPoint, [string]$details) : base(
        "Failed to mount image '$imagePath' to '$mountPoint': $details"
    ) {
        $this.ImagePath = $imagePath
        $this.MountPoint = $mountPoint
        $this.Operation = "Mount"
    }
}

# Dismount operation exception
class DFDismountException : DFException {
    [string]$MountPoint
    [bool]$SaveChanges

    DFDismountException([string]$message) : base($message) {
        $this.Operation = "Dismount"
    }

    DFDismountException([string]$mountPoint, [bool]$saveChanges, [string]$details) : base(
        "Failed to dismount '$mountPoint' (SaveChanges=$saveChanges): $details"
    ) {
        $this.MountPoint = $mountPoint
        $this.SaveChanges = $saveChanges
        $this.Operation = "Dismount"
    }
}

# DISM operation exception
class DFDismException : DFException {
    [int]$ExitCode
    [string]$Command
    [string]$StdErr

    DFDismException([string]$message) : base($message) {
        $this.Operation = "DISM"
    }

    DFDismException([string]$command, [int]$exitCode, [string]$stdErr) : base(
        "DISM command failed with exit code $exitCode"
    ) {
        $this.Command = $command
        $this.ExitCode = $exitCode
        $this.StdErr = $stdErr
        $this.Operation = "DISM"
    }
}

# File operation exception
class DFOperationException : DFException {
    [string]$FilePath
    [string]$OperationType

    DFOperationException([string]$message) : base($message) {
        $this.Operation = "FileOperation"
    }

    DFOperationException([string]$operationType, [string]$filePath, [string]$details) : base(
        "$operationType operation failed for '$filePath': $details"
    ) {
        $this.OperationType = $operationType
        $this.FilePath = $filePath
        $this.Operation = "FileOperation"
    }
}

# Validation exception
class DFValidationException : DFException {
    [string]$Parameter
    [object]$Value

    DFValidationException([string]$message) : base($message) {
        $this.Operation = "Validation"
    }

    DFValidationException([string]$parameter, [object]$value, [string]$reason) : base(
        "Validation failed for '$parameter': $reason"
    ) {
        $this.Parameter = $parameter
        $this.Value = $value
        $this.Operation = "Validation"
    }
}

# Registry operation exception
class DFRegistryException : DFException {
    [string]$HivePath
    [string]$KeyPath

    DFRegistryException([string]$message) : base($message) {
        $this.Operation = "Registry"
    }

    DFRegistryException([string]$hivePath, [string]$keyPath, [string]$details) : base(
        "Registry operation failed on '$keyPath': $details"
    ) {
        $this.HivePath = $hivePath
        $this.KeyPath = $keyPath
        $this.Operation = "Registry"
    }
}

# Driver injection exception
class DFDriverException : DFException {
    [string]$DriverPath
    [bool]$ForceUnsigned

    DFDriverException([string]$message) : base($message) {
        $this.Operation = "DriverInjection"
    }

    DFDriverException([string]$driverPath, [string]$details) : base(
        "Failed to inject driver '$driverPath': $details"
    ) {
        $this.DriverPath = $driverPath
        $this.Operation = "DriverInjection"
    }
}

# Package operation exception
class DFPackageException : DFException {
    [string]$PackageName

    DFPackageException([string]$message) : base($message) {
        $this.Operation = "Package"
    }

    DFPackageException([string]$packageName, [string]$details) : base(
        "Package operation failed for '$packageName': $details"
    ) {
        $this.PackageName = $packageName
        $this.Operation = "Package"
    }
}

# Template exception
class DFTemplateException : DFException {
    [string]$TemplateName

    DFTemplateException([string]$message) : base($message) {
        $this.Operation = "Template"
    }

    DFTemplateException([string]$templateName, [string]$details) : base(
        "Template operation failed for '$templateName': $details"
    ) {
        $this.TemplateName = $templateName
        $this.Operation = "Template"
    }
}

# Export exception types for use in catch blocks
$ExportedExceptions = @(
    'DFException',
    'DFImageNotFoundException',
    'DFUnsupportedFormatException',
    'DFMountException',
    'DFDismountException',
    'DFDismException',
    'DFOperationException',
    'DFValidationException',
    'DFRegistryException',
    'DFDriverException',
    'DFPackageException',
    'DFTemplateException'
)

Write-Verbose "Loaded DeployForge exception classes: $($ExportedExceptions.Count) types"
