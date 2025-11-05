using Xunit;
using FluentAssertions;
using DeployForge.Common.Models;

namespace DeployForge.Common.Tests;

public class OperationResultTests
{
    [Fact]
    public void SuccessResult_WithData_ShouldReturnSuccessTrue()
    {
        // Arrange & Act
        var result = OperationResult<string>.SuccessResult("test data");

        // Assert
        result.Success.Should().BeTrue();
        result.Data.Should().Be("test data");
        result.ErrorMessage.Should().BeNull();
    }

    [Fact]
    public void FailureResult_WithErrorMessage_ShouldReturnSuccessFalse()
    {
        // Arrange & Act
        var result = OperationResult<string>.FailureResult("Something went wrong", "ERROR_001");

        // Assert
        result.Success.Should().BeFalse();
        result.ErrorMessage.Should().Be("Something went wrong");
        result.ErrorCode.Should().Be("ERROR_001");
        result.Data.Should().BeNull();
    }

    [Fact]
    public void ExceptionResult_WithException_ShouldCaptureExceptionDetails()
    {
        // Arrange
        var exception = new InvalidOperationException("Test exception");

        // Act
        var result = OperationResult<string>.ExceptionResult(exception);

        // Assert
        result.Success.Should().BeFalse();
        result.ErrorMessage.Should().Be("Test exception");
        result.ExceptionDetails.Should().Contain("InvalidOperationException");
        result.ExceptionDetails.Should().Contain("Test exception");
    }

    [Fact]
    public void OperationResult_WithoutData_ShouldWorkCorrectly()
    {
        // Arrange & Act
        var result = OperationResult.SuccessResult();

        // Assert
        result.Success.Should().BeTrue();
    }

    [Fact]
    public void Timestamp_ShouldBeSet()
    {
        // Arrange & Act
        var result = OperationResult<string>.SuccessResult("test");

        // Assert
        result.Timestamp.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromSeconds(1));
    }
}
