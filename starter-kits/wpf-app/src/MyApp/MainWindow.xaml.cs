using System.Diagnostics;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Media;
using System.Windows.Threading;

namespace MyApp;

/// <summary>
/// Starter window: every themed component in use (card, section box, path field with right-click menu, checklist,
/// primary/secondary/small buttons, output log, status strip with badge, busy bar and the waiting-for-you pulse).
/// Replace the demo Run with the real work; keep the patterns.
/// </summary>
public partial class MainWindow : Window
{
    private static readonly string Version =
        typeof(MainWindow).Assembly.GetName().Version is { } v ? $"{v.Major}.{v.Minor}.{v.Build}" : "0.0.0";

    private readonly AppSettings _settings = AppSettings.Load();
    private readonly DispatcherTimer _pulse = new() { Interval = TimeSpan.FromMilliseconds(600) };
    private bool _loading = true;

    public MainWindow()
    {
        InitializeComponent();
        Title = $"MyApp {Version}";
        VersionBadge.Text = "v" + Version;
        Footer.Text = $"MyApp {Version} · right-click anywhere for appearance";
        InputBox.Text = _settings.InputFolder;
        OpenWhenDone.IsChecked = _settings.OpenWhenDone;
        (ThemeManager.Win95 ? Win95Radio : ModernRadio).IsChecked = true;
        SyncAppearanceMenu();
        _pulse.Tick += (_, _) => Status.Opacity = Status.Opacity < 1 ? 1 : 0.55;
        InputBox.TextChanged += (_, _) => RefreshChecklist();
        Loaded += (_, _) => { WindowSizing.FitToScreen(this); _loading = false; };
        Closing += (_, _) => SaveSettings();
        RefreshChecklist();
        Write("MyApp started. This is the output pane: time, then the message.", null);
        Write("Success lines are green.", "Log.Success");
        Write("Warnings are amber and say what to check.", "Log.Warning");
        Write("Errors are red and say what to do about them.", "Log.Error");
    }

    /// <summary>Paths dropped onto the exe in Explorer.</summary>
    public void ApplyPaths(IEnumerable<string> paths)
    {
        foreach (var p in paths)
        {
            if (Directory.Exists(p))
            {
                InputBox.Text = p;
            }
        }
    }

    // ---------------------------------------------------------------- appearance

    private void Style_Changed(object sender, RoutedEventArgs e)
    {
        if (_loading)
        {
            return;
        }

        ThemeManager.Apply(win95: Win95Radio.IsChecked == true);
        SyncAppearanceMenu();
        RefreshChecklist();
    }

    private void MenuModern_Click(object sender, RoutedEventArgs e) => ModernRadio.IsChecked = true;

    private void MenuWin95_Click(object sender, RoutedEventArgs e) => Win95Radio.IsChecked = true;

    private void SyncAppearanceMenu()
    {
        MenuModern.IsChecked = !ThemeManager.Win95;
        MenuWin95.IsChecked = ThemeManager.Win95;
    }

    private void About_Click(object sender, RoutedEventArgs e) =>
        MessageBox.Show(this, $"MyApp {Version}\nPortable: one exe, .NET Framework 4.8, no install.", "About MyApp");

    // ---------------------------------------------------------------- inputs

    private void Window_DragOver(object sender, DragEventArgs e)
    {
        e.Effects = e.Data.GetDataPresent(DataFormats.FileDrop) ? DragDropEffects.Copy : DragDropEffects.None;
        e.Handled = true;
    }

    private void Window_Drop(object sender, DragEventArgs e)
    {
        if (e.Data.GetData(DataFormats.FileDrop) is string[] paths)
        {
            ApplyPaths(paths);
        }
    }

    private void Browse_Click(object sender, RoutedEventArgs e)
    {
        using var dlg = new System.Windows.Forms.FolderBrowserDialog { SelectedPath = InputBox.Text };
        if (dlg.ShowDialog() == System.Windows.Forms.DialogResult.OK)
        {
            InputBox.Text = dlg.SelectedPath;
        }
    }

    private void OpenFolder_Click(object sender, RoutedEventArgs e)
    {
        if (Directory.Exists(InputBox.Text))
        {
            Process.Start("explorer.exe", $"\"{InputBox.Text}\"");
        }
    }

    private void ClearInput_Click(object sender, RoutedEventArgs e) => InputBox.Text = "";

    private void InputMenu_Opened(object sender, RoutedEventArgs e)
    {
        RecentMenu.Items.Clear();
        var recent = _settings.Recent.TryGetValue("input", out var list) ? list : new List<string>();
        foreach (var path in recent)
        {
            var item = new MenuItem { Header = path };
            item.Click += (_, _) => InputBox.Text = path;
            RecentMenu.Items.Add(item);
        }

        RecentMenu.IsEnabled = recent.Count > 0;
    }

    // ---------------------------------------------------------------- checklist

    private void RefreshChecklist()
    {
        Checklist.Children.Clear();
        var folder = InputBox.Text.Trim();
        if (folder.Length == 0)
        {
            AddCheck("Bad", "Input folder", "Not set. Browse, or drop a folder on the window.");
        }
        else if (Directory.Exists(folder))
        {
            AddCheck("Ok", "Input folder", folder);
        }
        else
        {
            AddCheck("Bad", "Input folder", "Doesn't exist: " + folder);
        }

        AddCheck("Warn", "Optional extra", "Not found. The run works without it (example of a warning row).");
        AddCheck("Off", "Unused input", "Not used with these options (example of a skipped row).");
        RunButton.IsEnabled = Directory.Exists(folder);
    }

    /// <summary>One checklist row: a coloured mark (✔ ! ✖ –), a title and what was found.</summary>
    private void AddCheck(string state, string title, string detail)
    {
        var mark = new TextBlock
        {
            Text = state switch { "Ok" => "✔", "Warn" => "!", "Bad" => "✖", _ => "–" },
            FontWeight = FontWeights.Bold, Width = 22, TextAlignment = TextAlignment.Center,
        };
        mark.SetResourceReference(TextBlock.ForegroundProperty, "Check." + state);
        var head = new TextBlock { Text = title, FontWeight = FontWeights.SemiBold, Width = 140 };
        head.SetResourceReference(TextBlock.ForegroundProperty, "Text.Strong");
        var body = new TextBlock { Text = detail, TextTrimming = TextTrimming.CharacterEllipsis };
        body.SetResourceReference(TextBlock.ForegroundProperty, "Text.Body");

        var row = new DockPanel();
        DockPanel.SetDock(mark, Dock.Left);
        DockPanel.SetDock(head, Dock.Left);
        row.Children.Add(mark);
        row.Children.Add(head);
        row.Children.Add(body);

        var border = new Border { Child = row };
        border.SetResourceReference(StyleProperty, "CheckRow");
        var copy = new MenuItem { Header = "Copy this line" };
        copy.Click += (_, _) => Clipboard.SetText($"{mark.Text} {title}: {detail}");
        border.ContextMenu = new ContextMenu { Items = { copy } };
        Checklist.Children.Add(border);
    }

    // ---------------------------------------------------------------- run (demo)

    private async void Run_Click(object sender, RoutedEventArgs e)
    {
        _settings.AddRecent("input", InputBox.Text.Trim());
        SaveSettings();
        SetBusy(true, "Running…");
        Write("Run started on " + InputBox.Text.Trim(), null);
        await Task.Delay(1500);
        var count = Directory.GetFiles(InputBox.Text.Trim()).Length;
        Write($"Found {count} file(s).", "Log.Success");
        SetBusy(false, "Done.");
        SetResult("Done", $"{count} file(s) found.");
    }

    private void Cancel_Click(object sender, RoutedEventArgs e)
    {
        // Demo of the waiting-for-you pulse: use it while a prompt elsewhere (firewall, UAC, dialog) needs the user.
        var on = !_pulse.IsEnabled;
        if (on)
        {
            Status.SetResourceReference(Border.BorderBrushProperty, "Pulse.Border");
            Status.SetResourceReference(BackgroundProperty, "Pulse.Background");
            StatusText.Text = "Waiting for you: approve the prompt in the other window. (Press Cancel again to stop.)";
            _pulse.Start();
        }
        else
        {
            _pulse.Stop();
            Status.Opacity = 1;
            Status.SetResourceReference(Border.BorderBrushProperty, "Card.Border");
            Status.SetResourceReference(BackgroundProperty, "Card.Background");
            StatusText.Text = "Ready.";
        }
    }

    private void CopyCommand_Click(object sender, RoutedEventArgs e)
    {
        Clipboard.SetText($"\"{Process.GetCurrentProcess().MainModule!.FileName}\" run \"{InputBox.Text.Trim()}\"");
        Write("Command line copied.", null);
    }

    private void SetBusy(bool busy, string message)
    {
        Busy.Visibility = busy ? Visibility.Visible : Visibility.Collapsed;
        RunButton.IsEnabled = !busy;
        StatusText.Text = message;
        if (busy)
        {
            SetResult("Neutral", "Running");
        }
    }

    /// <summary>Badge kinds: Pre (version/pre-release), Done, Fail, Neutral.</summary>
    private void SetResult(string kind, string text)
    {
        ResultBadge.SetResourceReference(BackgroundProperty, $"Badge.{kind}.Background");
        ResultText.SetResourceReference(TextBlock.ForegroundProperty, $"Badge.{kind}.Foreground");
        ResultText.Text = text;
    }

    // ---------------------------------------------------------------- output log

    /// <summary>One log line: grey time, then the message in the given palette key (null = normal text).</summary>
    private void Write(string message, string? colourKey)
    {
        var time = new Run(DateTime.Now.ToString("HH:mm:ss") + "  ");
        time.SetResourceReference(TextElement.ForegroundProperty, "Log.Time");
        var text = new Run(message);
        if (colourKey != null)
        {
            text.SetResourceReference(TextElement.ForegroundProperty, colourKey);
        }

        LogDoc.Blocks.Add(new Paragraph(time) { Margin = new Thickness(0), Inlines = { text } });
        Log.ScrollToEnd();
    }

    private void CopyLog_Click(object sender, RoutedEventArgs e) =>
        Clipboard.SetText(new TextRange(LogDoc.ContentStart, LogDoc.ContentEnd).Text);

    private void ClearLog_Click(object sender, RoutedEventArgs e) => LogDoc.Blocks.Clear();

    private void SaveSettings()
    {
        _settings.InputFolder = InputBox.Text.Trim();
        _settings.OpenWhenDone = OpenWhenDone.IsChecked == true;
        _settings.Win95Style = ThemeManager.Win95;
        _settings.Save();
    }
}
