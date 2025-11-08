using System.Globalization;
using System.Windows;
using System.Windows.Data;

namespace DeployForge.Desktop.Converters;

/// <summary>
/// Converts an integer count to Visibility. Visible if count > 0, Collapsed if count = 0.
/// </summary>
public class CountToVisibilityConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        if (value is int count)
        {
            return count > 0 ? Visibility.Visible : Visibility.Collapsed;
        }

        // Handle collection counts
        if (value is System.Collections.ICollection collection)
        {
            return collection.Count > 0 ? Visibility.Visible : Visibility.Collapsed;
        }

        return Visibility.Collapsed;
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
    {
        throw new NotImplementedException();
    }
}
