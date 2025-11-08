using QuestPDF.Fluent;
using QuestPDF.Helpers;
using QuestPDF.Infrastructure;

namespace DeployForge.Core.Services;

/// <summary>
/// Helper class for generating charts in PDF reports
/// </summary>
public static class ChartGenerator
{
    /// <summary>
    /// Generate a simple bar chart
    /// </summary>
    public static void GenerateBarChart(IContainer container, string title, Dictionary<string, double> data, string xAxisLabel = "", string yAxisLabel = "")
    {
        container.Column(column =>
        {
            column.Spacing(5);

            // Chart title
            column.Item().Text(title).FontSize(12).Bold();

            // Chart area
            column.Item().Height(200).Canvas((canvas, size) =>
            {
                if (!data.Any()) return;

                var maxValue = data.Values.Max();
                var barWidth = size.Width / data.Count;
                var chartHeight = size.Height - 40; // Leave space for labels

                var index = 0;
                foreach (var kvp in data)
                {
                    var barHeight = (float)(kvp.Value / maxValue * chartHeight);
                    var x = index * barWidth;
                    var y = size.Height - barHeight - 20;

                    // Draw bar
                    canvas.DrawRectangle(
                        new Point(x + 5, y),
                        new Size(barWidth - 10, barHeight),
                        Colors.Blue.Medium);

                    // Draw value on top of bar
                    canvas.DrawText(
                        kvp.Value.ToString("F1"),
                        new Point(x + barWidth / 2, y - 15),
                        TextStyle.Default.FontSize(8).FontColor(Colors.Black));

                    // Draw label
                    canvas.DrawText(
                        kvp.Key,
                        new Point(x + barWidth / 2, size.Height - 10),
                        TextStyle.Default.FontSize(8).FontColor(Colors.Black));

                    index++;
                }
            });

            // Axis labels
            if (!string.IsNullOrEmpty(xAxisLabel))
            {
                column.Item().AlignCenter().Text(xAxisLabel).FontSize(9).Italic();
            }

            if (!string.IsNullOrEmpty(yAxisLabel))
            {
                column.Item().Text(yAxisLabel).FontSize(9).Italic();
            }
        });
    }

    /// <summary>
    /// Generate a line chart for time series data
    /// </summary>
    public static void GenerateLineChart(IContainer container, string title, List<(DateTime Time, double Value)> data, string yAxisLabel = "")
    {
        container.Column(column =>
        {
            column.Spacing(5);

            // Chart title
            column.Item().Text(title).FontSize(12).Bold();

            // Chart area
            column.Item().Height(200).Canvas((canvas, size) =>
            {
                if (!data.Any()) return;

                var maxValue = data.Max(d => d.Value);
                var minValue = data.Min(d => d.Value);
                var valueRange = maxValue - minValue;
                if (valueRange == 0) valueRange = 1;

                var chartHeight = size.Height - 40;
                var chartWidth = size.Width - 40;

                var pointSpacing = chartWidth / (data.Count - 1);

                // Draw axes
                canvas.DrawLine(
                    new Point(30, 10),
                    new Point(30, size.Height - 30),
                    1,
                    Colors.Grey.Medium);

                canvas.DrawLine(
                    new Point(30, size.Height - 30),
                    new Point(size.Width - 10, size.Height - 30),
                    1,
                    Colors.Grey.Medium);

                // Draw line
                for (int i = 0; i < data.Count - 1; i++)
                {
                    var x1 = 30 + (i * pointSpacing);
                    var y1 = size.Height - 30 - (float)((data[i].Value - minValue) / valueRange * chartHeight);

                    var x2 = 30 + ((i + 1) * pointSpacing);
                    var y2 = size.Height - 30 - (float)((data[i + 1].Value - minValue) / valueRange * chartHeight);

                    canvas.DrawLine(
                        new Point(x1, y1),
                        new Point(x2, y2),
                        2,
                        Colors.Blue.Medium);

                    // Draw point
                    canvas.DrawRectangle(
                        new Point(x1 - 2, y1 - 2),
                        new Size(4, 4),
                        Colors.Blue.Darken2);
                }

                // Draw last point
                var lastX = 30 + ((data.Count - 1) * pointSpacing);
                var lastY = size.Height - 30 - (float)((data[^1].Value - minValue) / valueRange * chartHeight);
                canvas.DrawRectangle(
                    new Point(lastX - 2, lastY - 2),
                    new Size(4, 4),
                    Colors.Blue.Darken2);

                // Draw min/max labels
                canvas.DrawText(
                    maxValue.ToString("F1"),
                    new Point(5, 10),
                    TextStyle.Default.FontSize(8).FontColor(Colors.Black));

                canvas.DrawText(
                    minValue.ToString("F1"),
                    new Point(5, size.Height - 35),
                    TextStyle.Default.FontSize(8).FontColor(Colors.Black));
            });

            if (!string.IsNullOrEmpty(yAxisLabel))
            {
                column.Item().Text(yAxisLabel).FontSize(9).Italic();
            }
        });
    }

    /// <summary>
    /// Generate a pie chart
    /// </summary>
    public static void GeneratePieChart(IContainer container, string title, Dictionary<string, double> data)
    {
        container.Column(column =>
        {
            column.Spacing(5);

            // Chart title
            column.Item().Text(title).FontSize(12).Bold();

            column.Item().Row(row =>
            {
                // Pie chart
                row.RelativeItem().Height(200).Canvas((canvas, size) =>
                {
                    if (!data.Any()) return;

                    var total = data.Values.Sum();
                    var centerX = size.Width / 2;
                    var centerY = size.Height / 2;
                    var radius = Math.Min(size.Width, size.Height) / 2 - 10;

                    var startAngle = 0.0;
                    var colors = new[] {
                        Colors.Blue.Medium,
                        Colors.Green.Medium,
                        Colors.Orange.Medium,
                        Colors.Red.Medium,
                        Colors.Purple.Medium,
                        Colors.Teal.Medium
                    };

                    var index = 0;
                    foreach (var kvp in data)
                    {
                        var angle = (kvp.Value / total) * 360;
                        var color = colors[index % colors.Length];

                        // Draw slice (simplified - just draw a colored rectangle as placeholder)
                        // In a real implementation, you'd draw actual pie slices
                        canvas.DrawRectangle(
                            new Point(centerX - radius + (index * 20), centerY - radius),
                            new Size(15, 15),
                            color);

                        startAngle += angle;
                        index++;
                    }
                });

                // Legend
                row.ConstantItem(150).Column(legendColumn =>
                {
                    legendColumn.Spacing(5);
                    legendColumn.Item().Text("Legend").FontSize(10).Bold();

                    var colors = new[] {
                        Colors.Blue.Medium,
                        Colors.Green.Medium,
                        Colors.Orange.Medium,
                        Colors.Red.Medium,
                        Colors.Purple.Medium,
                        Colors.Teal.Medium
                    };

                    var index = 0;
                    foreach (var kvp in data)
                    {
                        var percentage = (kvp.Value / data.Values.Sum()) * 100;
                        var color = colors[index % colors.Length];

                        legendColumn.Item().Row(legendRow =>
                        {
                            legendRow.ConstantItem(15).Height(15).Canvas((canvas, size) =>
                            {
                                canvas.DrawRectangle(new Point(0, 0), size, color);
                            });

                            legendRow.RelativeItem().PaddingLeft(5).Text($"{kvp.Key} ({percentage:F1}%)")
                                .FontSize(8);
                        });

                        index++;
                    }
                });
            });
        });
    }

    /// <summary>
    /// Generate a simple progress bar
    /// </summary>
    public static void GenerateProgressBar(IContainer container, string label, double percentage, string color = "blue")
    {
        container.Column(column =>
        {
            column.Item().Row(row =>
            {
                row.RelativeItem().Text(label).FontSize(10);
                row.ConstantItem(50).AlignRight().Text($"{percentage:F1}%").FontSize(10).Bold();
            });

            column.Item().Height(20).Canvas((canvas, size) =>
            {
                // Background
                canvas.DrawRectangle(
                    new Point(0, 0),
                    size,
                    Colors.Grey.Lighten3);

                // Progress
                var progressWidth = (float)(size.Width * (percentage / 100));
                var barColor = color.ToLower() switch
                {
                    "green" => Colors.Green.Medium,
                    "red" => Colors.Red.Medium,
                    "orange" => Colors.Orange.Medium,
                    "yellow" => Colors.Yellow.Medium,
                    _ => Colors.Blue.Medium
                };

                canvas.DrawRectangle(
                    new Point(0, 0),
                    new Size(progressWidth, size.Height),
                    barColor);
            });
        });
    }
}
