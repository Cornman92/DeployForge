using System.Collections.ObjectModel;
using System.IO;
using CommunityToolkit.Mvvm.Input;
using DeployForge.Desktop.Services;
using Microsoft.Extensions.Logging;

namespace DeployForge.Desktop.ViewModels;

public partial class ImageManagementViewModel : ViewModelBase
{
    private readonly IApiClient _apiClient;
    private readonly IDialogService _dialogService;
    private readonly ILogger<ImageManagementViewModel> _logger;

    private string _selectedImagePath = string.Empty;
    private ImageInfo? _selectedImage;
    private MountedImage? _selectedMountedImage;
    private int _selectedImageIndex = 1;
    private string _mountPath = @"C:\Mount";
    private bool _mountReadOnly = false;

    public string SelectedImagePath
    {
        get => _selectedImagePath;
        set => SetProperty(ref _selectedImagePath, value);
    }

    public ImageInfo? SelectedImage
    {
        get => _selectedImage;
        set => SetProperty(ref _selectedImage, value);
    }

    public MountedImage? SelectedMountedImage
    {
        get => _selectedMountedImage;
        set
        {
            SetProperty(ref _selectedMountedImage, value);
            UnmountCommand.NotifyCanExecuteChanged();
        }
    }

    public int SelectedImageIndex
    {
        get => _selectedImageIndex;
        set => SetProperty(ref _selectedImageIndex, value);
    }

    public string MountPath
    {
        get => _mountPath;
        set => SetProperty(ref _mountPath, value);
    }

    public bool MountReadOnly
    {
        get => _mountReadOnly;
        set => SetProperty(ref _mountReadOnly, value);
    }

    public ObservableCollection<ImageInfo> Images { get; } = new();
    public ObservableCollection<MountedImage> MountedImages { get; } = new();
    public ObservableCollection<ImageIndexInfo> ImageIndices { get; } = new();

    public ImageManagementViewModel(
        IApiClient apiClient,
        IDialogService dialogService,
        ILogger<ImageManagementViewModel> logger)
    {
        _apiClient = apiClient;
        _dialogService = dialogService;
        _logger = logger;
    }

    public override async Task InitializeAsync()
    {
        await base.InitializeAsync();
        await LoadMountedImagesAsync();
    }

    [RelayCommand]
    private async Task LoadMountedImagesAsync()
    {
        try
        {
            IsBusy = true;
            StatusMessage = "Loading mounted images...";

            var mounted = await _apiClient.GetAsync<List<MountedImage>>("images/mounted");
            MountedImages.Clear();
            if (mounted != null)
            {
                foreach (var image in mounted)
                {
                    MountedImages.Add(image);
                }
            }

            StatusMessage = $"Loaded {MountedImages.Count} mounted image(s)";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load mounted images");
            StatusMessage = "Failed to load mounted images";
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task BrowseImageAsync()
    {
        var file = _dialogService.ShowOpenFileDialog(
            "Image Files (*.wim;*.esd;*.vhd;*.vhdx)|*.wim;*.esd;*.vhd;*.vhdx|All Files (*.*)|*.*",
            "Select Windows Image");

        if (!string.IsNullOrEmpty(file))
        {
            SelectedImagePath = file;
            await LoadImageInfoAsync(file);
        }
    }

    [RelayCommand]
    private void BrowseMountPath()
    {
        var folder = _dialogService.ShowFolderBrowserDialog("Select Mount Directory");
        if (!string.IsNullOrEmpty(folder))
        {
            MountPath = folder;
        }
    }

    private async Task LoadImageInfoAsync(string imagePath)
    {
        try
        {
            IsBusy = true;
            StatusMessage = "Loading image information...";

            // Get image info from API
            var imageInfo = await _apiClient.GetAsync<ImageDetailsResponse>(
                $"images/info?imagePath={Uri.EscapeDataString(imagePath)}");

            if (imageInfo != null)
            {
                SelectedImage = new ImageInfo
                {
                    FilePath = imagePath,
                    Format = imageInfo.ImageType ?? "Unknown",
                    Size = imageInfo.ImageSize,
                    ModifiedDate = File.GetLastWriteTime(imagePath),
                    ImageName = imageInfo.ImageName,
                    Description = imageInfo.ImageDescription,
                    Version = imageInfo.Version
                };

                // Load image indices
                ImageIndices.Clear();
                if (imageInfo.Images != null)
                {
                    foreach (var img in imageInfo.Images)
                    {
                        ImageIndices.Add(new ImageIndexInfo
                        {
                            Index = img.Index,
                            Name = img.Name,
                            Description = img.Description,
                            Size = img.Size
                        });
                    }
                }

                StatusMessage = $"Loaded: {Path.GetFileName(imagePath)}";
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load image info");
            StatusMessage = "Failed to load image information";
            _dialogService.ShowErrorMessage("Failed to load image information", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task MountImageAsync()
    {
        if (string.IsNullOrEmpty(SelectedImagePath))
        {
            _dialogService.ShowWarningMessage("No Image Selected", "Please select an image to mount.");
            return;
        }

        try
        {
            IsBusy = true;
            StatusMessage = $"Mounting image index {SelectedImageIndex}...";

            var request = new
            {
                ImagePath = SelectedImagePath,
                MountPath = MountPath,
                Index = SelectedImageIndex,
                ReadOnly = MountReadOnly
            };

            var result = await _apiClient.PostAsync<object>("images/mount", request);

            StatusMessage = "Image mounted successfully";
            _dialogService.ShowSuccessMessage("Success", $"Image mounted at {MountPath}");

            await LoadMountedImagesAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to mount image");
            StatusMessage = "Failed to mount image";
            _dialogService.ShowErrorMessage("Mount Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand(CanExecute = nameof(CanUnmount))]
    private async Task UnmountAsync()
    {
        if (SelectedMountedImage == null) return;

        var confirm = _dialogService.ShowConfirmation(
            "Unmount Image",
            $"Do you want to unmount the image at {SelectedMountedImage.MountPath}?");

        if (!confirm) return;

        try
        {
            IsBusy = true;
            StatusMessage = "Unmounting image...";

            var request = new
            {
                MountPath = SelectedMountedImage.MountPath,
                Save = true
            };

            await _apiClient.PostAsync<object>("images/unmount", request);

            StatusMessage = "Image unmounted successfully";
            await LoadMountedImagesAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to unmount image");
            StatusMessage = "Failed to unmount image";
            _dialogService.ShowErrorMessage("Unmount Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private bool CanUnmount() => SelectedMountedImage != null;

    [RelayCommand]
    private async Task ValidateImageAsync()
    {
        if (string.IsNullOrEmpty(SelectedImagePath))
        {
            _dialogService.ShowWarningMessage("No Image Selected", "Please select an image to validate.");
            return;
        }

        try
        {
            IsBusy = true;
            StatusMessage = "Validating image...";

            var request = new
            {
                ImagePath = SelectedImagePath,
                ImageIndex = SelectedImageIndex,
                DeepValidation = false
            };

            var result = await _apiClient.PostAsync<ValidationResultResponse>("validation/validate-image", request);

            if (result != null)
            {
                var message = result.Status == "Passed"
                    ? "Image validation passed successfully!"
                    : $"Image validation {result.Status}. {result.Errors.Count} error(s), {result.Warnings.Count} warning(s).";

                StatusMessage = message;

                if (result.Status == "Passed")
                {
                    _dialogService.ShowSuccessMessage("Validation Passed", message);
                }
                else
                {
                    _dialogService.ShowWarningMessage("Validation Issues", message);
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to validate image");
            StatusMessage = "Failed to validate image";
            _dialogService.ShowErrorMessage("Validation Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task GetImageInfoAsync()
    {
        if (string.IsNullOrEmpty(SelectedImagePath))
        {
            _dialogService.ShowWarningMessage("No Image Selected", "Please select an image.");
            return;
        }

        await LoadImageInfoAsync(SelectedImagePath);
    }

    [RelayCommand]
    private async Task RefreshAsync()
    {
        await LoadMountedImagesAsync();
        if (!string.IsNullOrEmpty(SelectedImagePath))
        {
            await LoadImageInfoAsync(SelectedImagePath);
        }
    }
}

public class ImageInfo
{
    public string FilePath { get; set; } = string.Empty;
    public string Format { get; set; } = string.Empty;
    public long Size { get; set; }
    public DateTime ModifiedDate { get; set; }
    public string ImageName { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string Version { get; set; } = string.Empty;

    public string SizeFormatted => FormatBytes(Size);

    private static string FormatBytes(long bytes)
    {
        string[] sizes = { "B", "KB", "MB", "GB", "TB" };
        double len = bytes;
        int order = 0;
        while (len >= 1024 && order < sizes.Length - 1)
        {
            order++;
            len /= 1024;
        }
        return $"{len:0.##} {sizes[order]}";
    }
}

public class MountedImage
{
    public string ImagePath { get; set; } = string.Empty;
    public string MountPath { get; set; } = string.Empty;
    public int Index { get; set; }
    public bool ReadOnly { get; set; }
    public string ImageName { get; set; } = string.Empty;
}

public class ImageIndexInfo
{
    public int Index { get; set; }
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public long Size { get; set; }

    public string SizeFormatted => FormatBytes(Size);

    private static string FormatBytes(long bytes)
    {
        string[] sizes = { "B", "KB", "MB", "GB", "TB" };
        double len = bytes;
        int order = 0;
        while (len >= 1024 && order < sizes.Length - 1)
        {
            order++;
            len /= 1024;
        }
        return $"{len:0.##} {sizes[order]}";
    }
}

public class ImageDetailsResponse
{
    public string? ImageType { get; set; }
    public long ImageSize { get; set; }
    public string? ImageName { get; set; }
    public string? ImageDescription { get; set; }
    public string? Version { get; set; }
    public List<ImageIndexResponse>? Images { get; set; }
}

public class ImageIndexResponse
{
    public int Index { get; set; }
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public long Size { get; set; }
}

public class ValidationResultResponse
{
    public string Status { get; set; } = string.Empty;
    public List<string> Errors { get; set; } = new();
    public List<string> Warnings { get; set; } = new();
}
