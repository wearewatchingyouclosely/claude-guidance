using System.Windows;
using System.Windows.Media;

namespace MyApp;

/// <summary>
/// The app's look: Modern (dark slate and blue) or Windows 95 (grey 3D on teal). App.xaml merges one palette
/// (colours) and one shape set (corners, fonts, control templates); this swaps them. Everything in XAML uses
/// DynamicResource, so open windows change at once. Code that sets colours uses <see cref="Brush"/> for a one-off
/// value, or SetResourceReference(…, "Key") so the colour follows a later style change.
/// </summary>
public static class ThemeManager
{
    public static bool Win95 { get; private set; }

    /// <summary>Raised after a style change, for code-drawn content that has to repaint.</summary>
    public static event Action? Changed;

    /// <summary>Applies the style saved in the settings file; called once at start-up.</summary>
    public static void ApplySaved() => Apply(AppSettings.Load().Win95Style, save: false);

    public static void Apply(bool win95, bool save = true)
    {
        Win95 = win95;
        var name = win95 ? "Win95" : "Modern";
        var merged = Application.Current.Resources.MergedDictionaries;
        merged[0] = Load($"Themes/Palette.{name}.xaml");
        merged[1] = Load($"Themes/Shapes.{name}.xaml");

        if (save)
        {
            var settings = AppSettings.Load();
            settings.Win95Style = win95;
            settings.Save();
        }

        Changed?.Invoke();
    }

    public static Brush Brush(string key) => (Brush)Application.Current.FindResource(key);

    public static Color Color(string key) => ((SolidColorBrush)Brush(key)).Color;

    private static ResourceDictionary Load(string path) =>
        new() { Source = new Uri($"pack://application:,,,/{path}", UriKind.Absolute) };
}
