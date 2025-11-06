using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.Desktop.Services;
using Microsoft.Extensions.Logging;

namespace DeployForge.Desktop.ViewModels;

public partial class ImageManagementViewModel : ViewModelBase
{
    private readonly IApiClient _apiClient;
    private readonly IDialogService _dialogService;
    private readonly ILogger<ImageManagementViewModel> _logger;

    public ObservableCollection<ImageInfo> Images { get; } = new();
    public ObservableCollection<MountedImage> MountedImages { get; } = new();

    public ImageManagementViewModel(
        IApiClient apiClient,
        IDialogService dialogService,
        ILogger<ImageManagementViewModel> logger)
    {
        _apiClient = apiClient;
        _dialogService = dialogService;
        _logger = logger;
    }

    [RelayCommand]
    private async Task LoadMountedImagesAsync()
    {
        try
        {
            IsBusy = true;
            var mounted = await _apiClient.GetAsync<List<MountedImage>>("images/mounted");
            MountedImages.Clear();
            if (mounted != null)
            {
                foreach (var image in mounted)
                {
                    MountedImages.Add(image);
                }
            }
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private void BrowseImage()
    {
        var file = _dialogService.ShowOpenFileDialog(
            "Image Files (*.wim;*.esd;*.vhd;*.vhdx)|*.wim;*.esd;*.vhd;*.vhdx|All Files (*.*)|*.*",
            "Select Windows Image");

        if (!string.IsNullOrEmpty(file))
        {
            StatusMessage = $"Selected: {file}";
        }
    }
}

public class ImageInfo
{
    public string FilePath { get; set; } = string.Empty;
    public string Format { get; set; } = string.Empty;
    public long Size { get; set; }
    public DateTime ModifiedDate { get; set; }
}

public class MountedImage
{
    public string ImagePath { get; set; } = string.Empty;
    public string MountPath { get; set; } = string.Empty;
    public int Index { get; set; }
    public bool ReadOnly { get; set; }
}
