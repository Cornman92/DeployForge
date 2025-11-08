using System.Globalization;
using System.Windows;
using System.Windows.Data;

namespace DeployForge.Desktop.Converters;

/// <summary>
/// Converts null to Visible, non-null to Collapsed.
/// </summary>
public class InvertedNullToVisibilityConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        return value == null ? Visibility.Visible : Visibility.Collapsed;
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
    {
        throw new NotImplementedException();
    }
}
