using System.Windows;

namespace MyApp;

public partial class App : Application
{
    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        // Command-line options run headless (scripts, tests) and never open a window; see rules\30_APP_DEVELOPMENT.md §3.
        // Only paths (dropped onto the exe in Explorer) open the window with them filled in.
        var onlyPaths = e.Args.Length > 0 && e.Args.All(a => System.IO.File.Exists(a) || System.IO.Directory.Exists(a));
        if (e.Args.Length > 0 && !onlyPaths)
        {
            Console.Error.WriteLine("No headless commands in the starter. Add them here and return an exit code.");
            Shutdown(2);
            return;
        }

        // Before the first window opens, so it starts in the saved style.
        ThemeManager.ApplySaved();
        var window = new MainWindow();
        MainWindow = window;
        window.Show();
        if (onlyPaths)
        {
            window.ApplyPaths(e.Args);
        }
    }
}
