using Xunit;
using FluentAssertions;
using DeployForge.DismEngine;
using DeployForge.Common.Models;

namespace DeployForge.DismEngine.Tests;

public class DismManagerTests : IDisposable
{
    private readonly DismManager _dismManager;

    public DismManagerTests()
    {
        _dismManager = new DismManager();
    }

    [Fact]
    public void Initialize_ShouldSucceed()
    {
        // Act
        var result = _dismManager.Initialize();

        // Assert
        result.Success.Should().BeTrue();
    }

    [Fact]
    public void Initialize_CalledMultipleTimes_ShouldSucceed()
    {
        // Act
        var result1 = _dismManager.Initialize();
        var result2 = _dismManager.Initialize();

        // Assert
        result1.Success.Should().BeTrue();
        result2.Success.Should().BeTrue();
    }

    [Fact]
    public void GetMountedImages_WhenInitialized_ShouldSucceed()
    {
        // Arrange
        _dismManager.Initialize();

        // Act
        var result = _dismManager.GetMountedImages();

        // Assert
        result.Success.Should().BeTrue();
        result.Data.Should().NotBeNull();
    }

    [Fact]
    public void MountImage_WithInvalidPath_ShouldFail()
    {
        // Arrange
        _dismManager.Initialize();
        var nonExistentPath = "C:\\NonExistent.wim";
        var mountPath = "C:\\Mount";

        // Act
        var result = _dismManager.MountImage(nonExistentPath, 1, mountPath);

        // Assert
        result.Success.Should().BeFalse();
        result.ErrorMessage.Should().NotBeNullOrEmpty();
    }

    public void Dispose()
    {
        _dismManager.Dispose();
    }
}
