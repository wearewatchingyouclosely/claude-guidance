using System.IO;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Json;

namespace MyApp;

/// <summary>
/// Remembered between runs in %APPDATA%\MyApp\settings.json (never next to the exe: it may sit in a read-only or
/// shared folder). A missing or broken file just means defaults; failing to save is never an error.
/// </summary>
[DataContract]
public sealed class AppSettings
{
    private const string AppFolder = "MyApp"; // rename with the app

    private static readonly string SettingsPath = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), AppFolder, "settings.json");

    private static readonly DataContractJsonSerializerSettings Options = new() { UseSimpleDictionaryFormat = true };

    [DataMember] public bool Win95Style { get; set; }
    [DataMember] public string InputFolder { get; set; } = "";
    [DataMember] public bool OpenWhenDone { get; set; } = true;

    /// <summary>Recently used paths per field (newest first), for the right-click "Recent" menu.</summary>
    [DataMember] public Dictionary<string, List<string>> Recent { get; set; } = new();

    public static AppSettings Load()
    {
        try
        {
            if (File.Exists(SettingsPath))
            {
                using var s = File.OpenRead(SettingsPath);
                if (new DataContractJsonSerializer(typeof(AppSettings), Options).ReadObject(s) is AppSettings loaded)
                {
                    loaded.Recent ??= new();
                    return loaded;
                }
            }
        }
        catch (Exception)
        {
            // A broken settings file just means defaults.
        }

        return new AppSettings();
    }

    public void Save()
    {
        try
        {
            Directory.CreateDirectory(Path.GetDirectoryName(SettingsPath)!);
            using var s = File.Create(SettingsPath);
            new DataContractJsonSerializer(typeof(AppSettings), Options).WriteObject(s, this);
        }
        catch (Exception)
        {
            // Not being able to remember settings is not worth an error.
        }
    }

    public void AddRecent(string field, string path, int keep = 10)
    {
        if (string.IsNullOrWhiteSpace(path))
        {
            return;
        }

        if (!Recent.TryGetValue(field, out var list))
        {
            Recent[field] = list = new List<string>();
        }

        list.RemoveAll(p => string.Equals(p, path, StringComparison.OrdinalIgnoreCase));
        list.Insert(0, path);
        if (list.Count > keep)
        {
            list.RemoveRange(keep, list.Count - keep);
        }
    }
}
