using DeployForge.Services;
using Xunit;

namespace DeployForge.Services.Tests;

/// <summary>
/// Tests for SettingsService.
/// </summary>
public class SettingsServiceTests : IDisposable
{
    private readonly string _testPath;
    private readonly SettingsService _service;
    
    public SettingsServiceTests()
    {
        _testPath = Path.Combine(Path.GetTempPath(), "DeployForgeTests", $"settings-{Guid.NewGuid()}.json");
        Directory.CreateDirectory(Path.GetDirectoryName(_testPath)!);
        _service = new SettingsService(_testPath);
    }
    
    public void Dispose()
    {
        if (File.Exists(_testPath))
        {
            File.Delete(_testPath);
        }
    }
    
    [Fact]
    public void Theme_DefaultsToDark()
    {
        Assert.Equal("Dark", _service.Theme);
    }
    
    [Fact]
    public void ShowAdvancedOptions_DefaultsToFalse()
    {
        Assert.False(_service.ShowAdvancedOptions);
    }
    
    [Fact]
    public void CreateBackups_DefaultsToTrue()
    {
        Assert.True(_service.CreateBackups);
    }
    
    [Fact]
    public void MaxConcurrentOperations_DefaultsTo4()
    {
        Assert.Equal(4, _service.MaxConcurrentOperations);
    }
    
    [Fact]
    public void SetSetting_StoresValue()
    {
        _service.SetSetting("TestKey", "TestValue");
        
        var result = _service.GetSetting<string>("TestKey");
        
        Assert.Equal("TestValue", result);
    }
    
    [Fact]
    public void GetSetting_ReturnsDefaultWhenNotSet()
    {
        var result = _service.GetSetting("NonExistent", "DefaultValue");
        
        Assert.Equal("DefaultValue", result);
    }
    
    [Fact]
    public void AddRecentImage_AddsToList()
    {
        _service.AddRecentImage(@"C:\test\image.wim");
        
        Assert.Contains(@"C:\test\image.wim", _service.RecentImages);
    }
    
    [Fact]
    public void AddRecentImage_MovesToTop()
    {
        _service.AddRecentImage(@"C:\test\image1.wim");
        _service.AddRecentImage(@"C:\test\image2.wim");
        _service.AddRecentImage(@"C:\test\image1.wim"); // Add again
        
        Assert.Equal(@"C:\test\image1.wim", _service.RecentImages[0]);
    }
    
    [Fact]
    public void ClearRecentImages_ClearsList()
    {
        _service.AddRecentImage(@"C:\test\image.wim");
        Assert.NotEmpty(_service.RecentImages);
        
        _service.ClearRecentImages();
        
        Assert.Empty(_service.RecentImages);
    }
    
    [Fact]
    public async Task SaveAndLoad_PersistsSettings()
    {
        _service.Theme = "Light";
        _service.ShowAdvancedOptions = true;
        _service.AddRecentImage(@"C:\test\image.wim");
        
        await _service.SaveAsync();
        
        // Create new service instance
        var service2 = new SettingsService(_testPath);
        await service2.LoadAsync();
        
        Assert.Equal("Light", service2.Theme);
        Assert.True(service2.ShowAdvancedOptions);
        Assert.Contains(@"C:\test\image.wim", service2.RecentImages);
    }
    
    [Fact]
    public async Task Reset_ClearsAllSettings()
    {
        _service.Theme = "Light";
        _service.ShowAdvancedOptions = true;
        await _service.SaveAsync();
        
        await _service.ResetAsync();
        
        // Load fresh
        await _service.LoadAsync();
        
        Assert.Equal("Dark", _service.Theme);
        Assert.False(_service.ShowAdvancedOptions);
    }
    
    [Fact]
    public async Task ExportAndImport_TransfersSettings()
    {
        _service.Theme = "Light";
        _service.MaxConcurrentOperations = 8;
        
        var exportPath = Path.Combine(Path.GetTempPath(), "export-test.json");
        
        try
        {
            await _service.ExportAsync(exportPath);
            Assert.True(File.Exists(exportPath));
            
            // Reset and import
            await _service.ResetAsync();
            await _service.ImportAsync(exportPath);
            
            Assert.Equal("Light", _service.Theme);
            Assert.Equal(8, _service.MaxConcurrentOperations);
        }
        finally
        {
            if (File.Exists(exportPath))
            {
                File.Delete(exportPath);
            }
        }
    }
}
