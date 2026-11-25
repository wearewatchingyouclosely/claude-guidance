# 31 — Style guide: desktop apps (.exe, WPF/XAML)

Every desktop tool offers the same two looks, so a user who knows one tool already knows the next:

| Style | Look | Colours |
|---|---|---|
| **Modern** (default) | Rounded cards, flat buttons, Segoe UI | Dark slate and blue. There's no light variant in the exe |
| **Windows 95** | Square corners, raised/sunken 3D bevels, MS Sans Serif | Grey controls on a teal desktop |

The user switches style in a Style option on the main window and in the window's right-click menu (**Appearance**). The change applies at once to every open window and is remembered in `%APPDATA%\<App>\settings.json`.

**Starter:** [starter-kits/wpf-app/](../starter-kits/wpf-app/) is a buildable app with the theme files and a demo window that uses every component. `MyApp.exe` in that folder is the built demo: run it to see both styles. Screenshots are in `starter-kits/wpf-app/screenshots/`.

## 1. How it's built
```
App.xaml  MergedDictionaries:  [0] Themes/Palette.<Style>.xaml   colours (SolidColorBrush keys)
                               [1] Themes/Shapes.<Style>.xaml    fonts, corner radii, card thickness, button templates
                               [2] Theme.xaml                    named styles, built only from [0] and [1]
ThemeManager.Apply(win95)  →  swaps [0] and [1]  →  every DynamicResource in every open window updates
```
- **The two palettes have identical keys.** The same applies to the two shape sets. Add a key to both, or to neither.
- **Merge the dictionaries straight into `Application.Resources`.** Changes to a dictionary loaded by `Source` never reach windows that are already open.
- **Order matters:** palette, then shapes, then `Theme.xaml`. `ThemeManager` replaces index 0 and index 1.
- `ThemeManager.ApplySaved()` runs in `App.OnStartup` **before** the first window opens, so the app never flashes the wrong style.

## 2. Rules
- **Never hard-code a colour, font or corner radius** in a window. Use a `Theme.xaml` style, or `{DynamicResource Key}`.
  - `StaticResource` is fine only for *style* keys, never for colours.
- **In code-behind:**
  - Use `element.SetResourceReference(Property, "Key")` so the colour follows a later style change. This works on `Run`/`Paragraph` too.
  - Use `ThemeManager.Brush("Key")` only for a one-off value that is redrawn anyway, and repaint on `ThemeManager.Changed`.
- **One primary button per window** (`PrimaryButton`, `IsDefault="True"`). Every other button is `SecondaryButton`, or `SmallButton` for minor actions.
- **Every tool window has a "← Main menu" button** at the top right, disabled while busy.
- **Every window fits the work area:** call `WindowSizing.FitToScreen(this)` on `Loaded`. Long content scrolls inside the window, never off screen.
- **The system context menu, menu items and tool tips ignore the style**, so `Theme.xaml` restyles them. Don't set colours on individual menus.
- **Check both styles** before calling a GUI change done: run the exe in each style and take a screenshot of each.
  - Windows may refuse to bring a launched window to the front, and a screen copy then grabs whatever is on top. Capture the window itself with `PrintWindow(hwnd, hdc, 2)`.

## 3. Palette keys (`Themes/Palette.*.xaml`)
| Group | Keys | Modern | Windows 95 |
|---|---|---|---|
| Window | `Window.Background`, `Window.Text`, `Window.TextMuted` | #0f172a / #f8fafc / #64748b | #008080 / #ffffff / #e0e0e0 |
| Cards | `Card.Background`, `Card.Border`, `Section.Background`, `Section.Border` | #111827, #334155, #0b1220, #1e293b | #c0c0c0, #808080 (both) |
| Text on cards | `Text.Strong`, `Text`, `Text.Body`, `Text.Muted`, `Text.Faint` | #f8fafc → #64748b | #000 → #606060 |
| Hints | `Notice`, `Hint.Success`, `Hint.Warning`, `Hint.Error` | amber, green, amber, red (light) | #800000, #006000, #806000, #c00000 |
| Inputs | `Input.Background`, `Input.Foreground`, `Input.Border` | #0f172a, #e2e8f0, #334155 | #fff, #000, #808080 |
| Buttons | `Accent.*` (primary), `Button.*`, `Focus` | blue #2563eb, slate #1f2937 | grey #c0c0c0, black outline on the primary button |
| Bevels | `Bevel.Light`, `Bevel.Shadow`, `Bevel.Dark` | (unused) | #fff, #808080, #000 |
| Launcher | `Launch.HoverBackground` | #172033 | #d8d8d8 |
| Scroll bars | `Scroll.Thumb`, `Scroll.ThumbHover`, `Scroll.ThumbDrag` | slate | greys |
| Badges | `Badge.{Pre,Done,Fail,Neutral}.{Background,Foreground}` | amber / green / red / slate | navy / green / maroon / grey, white text |
| Output log | `Log.Background`, `Log.Border`, `Log.Text`, `Log.Time`, `Log.Success`, `Log.Warning`, `Log.Error` | near-black pane | white pane, black text |
| Progress and pulse | `Progress.Background`, `Progress.Foreground`, `Pulse.Border`, `Pulse.Background` | blue bar, amber pulse | navy bar, yellow pulse |
| Menus | `Menu.Background`, `Menu.Border`, `Menu.Text`, `Menu.TextMuted`, `Menu.Highlight`, `Menu.HighlightText`, `Menu.Separator` | slate, blue highlight | grey, navy highlight |
| Checklist | `Check.Ok`, `Check.Warn`, `Check.Bad`, `Check.Off`, `Check.RowHover` | green, amber, red, slate | #008000, #806000, #c00000, #808080 |

The exact values are in the XAML files. Change them there, in both files, and never in a window.

## 4. Shape keys (`Themes/Shapes.*.xaml`)
| Key | Modern | Windows 95 |
|---|---|---|
| `Font.UI` / `Font.Mono` | Segoe UI / Consolas | Microsoft Sans Serif / Lucida Console |
| `Radius.Card`, `.Section`, `.Option`, `.Button`, `.Badge`, `.Thumb` | 14, 10, 10, 6, 6, 3 | all 0 |
| `Thickness.Card` | 1 | 2 |
| `Template.Button` | Flat rounded border. Hover 0.85 opacity, press 0.7, disabled 0.4 | Four nested borders (outer, dark, light, shadow). Pressed swaps the edges and shifts the content 2,2 |
| `Template.LaunchOption` | Rounded card; the border lights up on hover | Raised panel; an accent outline on hover |

## 5. Named styles (`Theme.xaml`)
| Key | Target | Use for |
|---|---|---|
| `ToolWindow` | Window | Every window: background and UI font |
| `WindowTitle` | TextBlock | The app or tool name in the header (18, SemiBold) |
| `FooterText` | TextBlock | Version line under everything (11, muted) |
| `CardStyle` | Border | Main grouping box (padding 18) |
| `SectionBox` | Border | Inner box inside a card, or the output pane (padding 14) |
| `SectionHeader` / `SubHeader` | TextBlock | Card title (18) / box title (15) |
| `HintText` | TextBlock | One-line explanation under a title (12, muted, wraps) |
| `FieldLabel` | TextBlock | Label left of an input (14, SemiBold, fixed column ~130) |
| `PathBox` | TextBox | Path and text inputs (height 34) |
| `OptionCheckBox` / `OptionRadio` | CheckBox / RadioButton | Options |
| `PrimaryButton` / `SecondaryButton` / `SmallButton` | Button | The one main action / other actions / minor actions |
| `LogBox` | RichTextBox | Output pane (read-only, monospace, coloured lines) |
| `StatusStrip` | Border | Bottom strip: result badge, message, busy bar |
| `Badge` | Border | Version or result badge. Set `Badge.<Kind>.Background/Foreground` |
| `BusyBar` | ProgressBar | Thin indeterminate bar while running |
| `CheckRow` | Border | One checklist row (hover highlight) |
| *(implicit)* | ContextMenu, MenuItem, Separator, ToolTip, ScrollBar | Restyled automatically |

## 6. Window layout
```
┌ Title  [v0.1.0]                                   [← Main menu] ┐   header: WindowTitle + Pre badge
│ ┌ Card: Inputs ───────────────────────────────────────────────┐ │   margins 20, gap 14 between blocks
│ │ Input folder  [ path box ……………………………………… ] [Browse…]       │ │   drop target: whole window
│ │ ☑ option   Style: ◉ Modern ○ Windows 95                       │ │
│ └─────────────────────────────────────────────────────────────┘ │
│ ┌ Card: Before you go ────────────────────────────────────────┐ │   ✔ found  ! optional  ✖ blocks  – unused
│ └─────────────────────────────────────────────────────────────┘ │
│ [ Run ] [Cancel] [Copy command line]                             │   one primary button
│ ┌ Section: Output ────────────────────────────────────────────┐ │   time grey, then message; green/amber/red
│ └─────────────────────────────────────────────────────────────┘ │
│ [Done] message ……………………………………………………………… [busy bar]          │   StatusStrip; pulses when waiting for the user
│ App 0.1.0 · right-click anywhere for appearance                 │   FooterText
└─────────────────────────────────────────────────────────────────┘
```
- **Spacing:** window margin 20, gap 14 between cards, 8 between buttons, 12 between rows inside a card.
- **Type scale:** 18 for the title and card titles, 15 for box titles, 14 for labels, 12 for hints and the log, 11 for the footer and badges.

## 7. Behaviour that goes with the look
- **Right-click menus everywhere.** Each menu holds the actions for what's under the pointer, then **Appearance**. Path fields offer Browse, Open in Explorer, Recent and Clear. The run button offers Run and Copy command line. The log offers Copy all, Save and Clear. Checklist rows offer their fix and Copy.
- **Checklist marks:** ✔ `Check.Ok`, ! `Check.Warn`, ✖ `Check.Bad`, – `Check.Off`. Any ✖ disables the primary button.
- **Waiting-for-you pulse:** while a prompt elsewhere needs the user (firewall, UAC, dialog), set the status strip to `Pulse.Border`/`Pulse.Background`, blink its opacity at 600 ms, and say what to approve.
- **Output log:** one line per event, `HH:mm:ss` in `Log.Time`, then the message. Successes are green, warnings amber and errors red. Errors say what to do.
- **Icons:** made from the supplied image with the repo's `make-icon` script. Don't crop or reinterpret the image.

## 8. Starting a new app from the kit
1. Copy `starter-kits/wpf-app/` into the new repo and rename `MyApp`:
   - the folder and the csproj;
   - `namespace` and `x:Class` everywhere;
   - `AppSettings.AppFolder`;
   - the `Product` and `AssemblyTitle`.
2. Run `.\build.ps1`. It writes the portable exe next to it.
3. Replace the demo `Run_Click` with the real work. Keep the components and patterns.
4. Keep the theme files identical to the kit unless you're changing the house style. In that case change the kit, and give its change log a line in the guidance `_INDEX.md`.
