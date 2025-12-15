using DeployForge.Core.Enums;
using Xunit;

namespace DeployForge.Core.Tests;

/// <summary>
/// Tests for enumeration types.
/// </summary>
public class EnumTests
{
    [Fact]
    public void ImageFormat_HasExpectedValues()
    {
        // Assert all expected image formats exist
        Assert.True(Enum.IsDefined(typeof(ImageFormat), ImageFormat.WIM));
        Assert.True(Enum.IsDefined(typeof(ImageFormat), ImageFormat.ESD));
        Assert.True(Enum.IsDefined(typeof(ImageFormat), ImageFormat.VHD));
        Assert.True(Enum.IsDefined(typeof(ImageFormat), ImageFormat.VHDX));
        Assert.True(Enum.IsDefined(typeof(ImageFormat), ImageFormat.ISO));
    }
    
    [Fact]
    public void GamingProfile_HasExpectedValues()
    {
        Assert.True(Enum.IsDefined(typeof(GamingProfile), GamingProfile.Minimal));
        Assert.True(Enum.IsDefined(typeof(GamingProfile), GamingProfile.Balanced));
        Assert.True(Enum.IsDefined(typeof(GamingProfile), GamingProfile.Performance));
        Assert.True(Enum.IsDefined(typeof(GamingProfile), GamingProfile.Extreme));
    }
    
    [Fact]
    public void DebloatLevel_HasExpectedValues()
    {
        Assert.True(Enum.IsDefined(typeof(DebloatLevel), DebloatLevel.Minimal));
        Assert.True(Enum.IsDefined(typeof(DebloatLevel), DebloatLevel.Standard));
        Assert.True(Enum.IsDefined(typeof(DebloatLevel), DebloatLevel.Aggressive));
        Assert.True(Enum.IsDefined(typeof(DebloatLevel), DebloatLevel.Extreme));
    }
    
    [Fact]
    public void DevelopmentProfile_HasExpectedValues()
    {
        Assert.True(Enum.IsDefined(typeof(DevelopmentProfile), DevelopmentProfile.General));
        Assert.True(Enum.IsDefined(typeof(DevelopmentProfile), DevelopmentProfile.WebDevelopment));
        Assert.True(Enum.IsDefined(typeof(DevelopmentProfile), DevelopmentProfile.DotNet));
        Assert.True(Enum.IsDefined(typeof(DevelopmentProfile), DevelopmentProfile.Python));
    }
    
    [Fact]
    public void BuildProfileType_HasExpectedValues()
    {
        Assert.True(Enum.IsDefined(typeof(BuildProfileType), BuildProfileType.Gaming));
        Assert.True(Enum.IsDefined(typeof(BuildProfileType), BuildProfileType.Developer));
        Assert.True(Enum.IsDefined(typeof(BuildProfileType), BuildProfileType.Enterprise));
        Assert.True(Enum.IsDefined(typeof(BuildProfileType), BuildProfileType.Student));
        Assert.True(Enum.IsDefined(typeof(BuildProfileType), BuildProfileType.Creator));
        Assert.True(Enum.IsDefined(typeof(BuildProfileType), BuildProfileType.Custom));
    }
}
