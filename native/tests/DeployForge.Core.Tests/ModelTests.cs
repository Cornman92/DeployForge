using DeployForge.Core.Enums;
using DeployForge.Core.Models;
using Xunit;

namespace DeployForge.Core.Tests;

/// <summary>
/// Tests for data model types.
/// </summary>
public class ModelTests
{
    [Fact]
    public void BuildProfile_CreateGamingProfile_HasCorrectDefaults()
    {
        var profile = BuildProfile.CreateGamingProfile();
        
        Assert.Equal("Gaming PC", profile.Name);
        Assert.Equal(BuildProfileType.Gaming, profile.Type);
        Assert.True(profile.EnableGaming);
        Assert.True(profile.EnableDebloat);
        Assert.NotNull(profile.Gaming);
        Assert.Equal(GamingProfile.Performance, profile.Gaming.Profile);
    }
    
    [Fact]
    public void BuildProfile_CreateDeveloperProfile_HasCorrectDefaults()
    {
        var profile = BuildProfile.CreateDeveloperProfile();
        
        Assert.Equal("Developer Workstation", profile.Name);
        Assert.Equal(BuildProfileType.Developer, profile.Type);
        Assert.True(profile.EnableDevEnvironment);
        Assert.NotNull(profile.DevEnvironment);
        Assert.True(profile.DevEnvironment.EnableDeveloperMode);
    }
    
    [Fact]
    public void BuildProfile_CreateEnterpriseProfile_HasCorrectDefaults()
    {
        var profile = BuildProfile.CreateEnterpriseProfile();
        
        Assert.Equal("Enterprise Workstation", profile.Name);
        Assert.Equal(BuildProfileType.Enterprise, profile.Type);
        Assert.True(profile.EnableDebloat);
        Assert.True(profile.EnablePrivacyHardening);
        Assert.Equal(PrivacyLevel.Maximum, profile.PrivacyLevel);
    }
    
    [Fact]
    public void GamingConfig_FromProfile_CreatesCorrectConfig()
    {
        var config = GamingConfig.FromProfile(GamingProfile.Performance);
        
        Assert.Equal(GamingProfile.Performance, config.Profile);
        Assert.True(config.EnableGameMode);
        Assert.True(config.DisableGameBar);
        Assert.True(config.OptimizeNetwork);
    }
    
    [Fact]
    public void DebloatConfig_Default_HasCorrectValues()
    {
        var config = DebloatConfig.Default;
        
        Assert.Equal(DebloatLevel.Standard, config.Level);
        Assert.True(config.DisableTelemetry);
        Assert.True(config.DisableCortana);
        Assert.NotEmpty(config.RemoveApps);
    }
    
    [Fact]
    public void ImageInfo_EmptyByDefault()
    {
        var info = new ImageInfo();
        
        Assert.Equal(string.Empty, info.Path);
        Assert.Equal(ImageFormat.WIM, info.Format);
        Assert.Empty(info.Indexes);
    }
    
    [Fact]
    public void MountResult_DefaultValues()
    {
        var result = new MountResult();
        
        Assert.False(result.Success);
        Assert.Equal(string.Empty, result.MountPath);
        Assert.Equal(1, result.Index);
    }
    
    [Fact]
    public void PartitionConfig_CreateUefiLayout_HasCorrectPartitions()
    {
        var config = PartitionConfig.CreateUefiLayout();
        
        Assert.True(config.UseUefi);
        Assert.Equal(4, config.Partitions.Count); // EFI, MSR, Windows, Recovery
        
        Assert.Equal(PartitionType.EFI, config.Partitions[0].Type);
        Assert.Equal(PartitionType.MSR, config.Partitions[1].Type);
        Assert.Equal(PartitionType.Primary, config.Partitions[2].Type);
        Assert.Equal(PartitionType.Recovery, config.Partitions[3].Type);
    }
    
    [Fact]
    public void UnattendConfig_CreateBasic_HasCorrectDefaults()
    {
        var config = UnattendConfig.CreateBasic("TestPC", "TestUser");
        
        Assert.Equal("TestPC", config.ComputerName);
        Assert.Single(config.Users);
        Assert.Equal("TestUser", config.Users[0].Name);
        Assert.True(config.SkipOobe);
    }
}
