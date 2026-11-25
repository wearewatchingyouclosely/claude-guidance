# 32 — Style guide: generated HTML pages (viewers, reports, XML-to-HTML output)

Tools that turn exports into something people read produce **one self-contained HTML file**. That covers viewers, cross-reference pages, reports and rendered XML. The page opens in Edge or Chrome without a server and can be mailed. It offers the same two looks as the desktop apps (31):

| Style | Look | Themes |
|---|---|---|
| **Modern** (default) | Light panels, rounded corners, Segoe UI | **System / Light / Dark**. System follows the OS |
| **Windows 95** | Grey 3D bevels on teal, blue title-bar gradient, MS Sans Serif | Has its own colours. The theme setting is disabled |

The desktop exe is Modern-dark only. A page can also be light because it's read in a browser next to other pages, so it follows the reader's system.

**Starter:** [starter-kits/html-page/](../starter-kits/html-page/):
- `theme.css`: tokens and components;
- `appearance.js`: style/theme state, right-click menu, toast, copy;
- `demo.html`: every component. Open it and right-click.

Screenshots of the four looks are in `screenshots/`.

## 1. How it's built
```html
<html data-style="win95" data-theme="dark">   ← set by appearance.js; absent = Modern / follow the system
<style>  …theme.css inlined…  </style>
<script> …appearance.js inlined… </script>     ← in <head>, so the page never flashes the wrong look
```
- **Tokens on `:root`:** Modern light is the default; Modern dark comes from `prefers-color-scheme: dark` unless `data-theme="light"`, or from `data-theme="dark"`; Windows 95 comes from `data-style="win95"`. Components use only tokens (`var(--panel)` and so on). When you add a token, add it to all three blocks.
- **Windows 95 also changes shapes:** `[data-style="win95"]` rules remove every radius and draw bevels with `box-shadow: var(--out)` (raised) or `var(--in)` (sunken).
- **Inline everything into the generated page:** CSS, JS, images (as data URIs) and fonts. No CDN, no links, no second file. The kit's `demo.html` links the two files only so the kit keeps a single copy of each.
- `appearance.js` remembers the choice per browser in `localStorage`, under one key per app (`STORE_KEY`), inside try/catch: a private window or blocked storage just means defaults.
- `?style=win95&theme=dark` in the URL overrides the saved choice for that visit. Use it for links, screenshots and tests.

## 2. Tokens (`theme.css`)
| Token | Modern light | Modern dark | Windows 95 |
|---|---|---|---|
| `--bg` page, `--panel` cards | #f4f5f7, #fff | #14171d, #1c2028 | #c0c0c0 (`--desktop` #008080 behind) |
| `--ink` text, `--muted`, `--line` borders | #1d2330, #6b7385, #dde1e8 | #e6e9ef, #9aa3b5, #2c3240 | #000, #404040, #808080 |
| `--acc` accent, `--acc-ink` on accent | #1f6feb, #fff | #5b9cff, #0b1220 | #000080, #fff |
| `--ok`, `--warn`, `--bad`, `--off` | green, amber, red, slate | lighter versions | #008000, #806000, #c00000, #808080 |
| `--log-bg`, `--code-bg` | near-white | near-black | #fff (sunken) |
| `--font`, `--mono` | 13px Segoe UI, Consolas | same | 11px MS Sans Serif, Lucida Console |
| `--radius`, `--radius-s` | 8px, 6px | same | 0 |
| `--out`, `--in` | — | — | raised / sunken bevel shadows |

## 3. Components (class names)
| Class | What | Desktop equivalent |
|---|---|---|
| `.appbar` (+ `h1`, `.sp` spacer) | 44px top bar: title, generated date and version, then the controls on the right. Windows 95: navy-to-blue gradient | Header row |
| `.btn`, `.btn.primary`, `.btn.on`, `.seg` | Buttons; one primary per view; toggles use `.on`; `.seg` groups toggles | Secondary / Primary / SmallButton |
| `input`, `select`, `textarea`, `label.opt` | Inputs and options. Windows 95: white, sunken | PathBox, OptionCheckBox/Radio |
| `.card` | Grouping box | CardStyle |
| `.pop` | Floating panel (settings, details). Windows 95: raised with a hard shadow | — |
| `.tabs > button.on` | Tab strip | — |
| `.check.ok/.warn/.bad/.off` with `.m` `.t` `.d` | Checklist row: mark ✔ ! ✖ –, title, detail | CheckRow + Check.* |
| `.badge` (`.ok` `.warn` `.bad` `.acc`) | Status and version pills | Badge |
| `table`, `th` (sticky), `tr.act`, `td.num`, `.tablewrap` | Data tables; the selected row in accent; numbers right-aligned in mono; wrap wide tables | — |
| `.log` with `.time` `.ok` `.warn` `.bad` | Output and log text | LogBox + Log.* |
| `.code`, `.mono` | Code, addresses, mnemonics | Font.Mono |
| `.ctx` (built by `Appearance.ctxMenu`) | Right-click menu | ContextMenu |
| `.toast` (via `Appearance.toast`) | "Copied" confirmation | — |
| `.muted`, `.small` | Secondary text | Text.Muted, FooterText |

## 4. `appearance.js` API (`window.Appearance`)
| Call | Does |
|---|---|
| `UI` | `{style, theme}`, the current choice. You can add your own UI state here (pane widths, pins); it's saved with it |
| `set(key, value)` | Changes `style` or `theme`, saves it, applies it, and fires the `appearance` event on `document` |
| `ctxMenu(x, y, items)` | Opens a right-click menu. Items: `{t, ic, k, chk, dis, on, sub}`, or `"-"` for a separator |
| `appearanceItems()` | The standard **Appearance ▸ Modern / Windows 95 / System / Light / Dark** entry. Put it at the end of every menu |
| `toast(text)`, `copy(text, what)` | Short confirmation; clipboard copy with a toast, or a "select and press Ctrl+C" hint if the copy fails |

## 5. Rules
- **Right-click menus everywhere:**
  - first the actions for what's under the pointer (copy row, go to, show details);
  - then "Copy link to this view";
  - then Appearance.

  **Shift+right-click** gives the browser's own menu. Escape, clicking elsewhere or leaving the window closes the menu.
- **The URL holds the view** (`#…` hash for the screen, row or selection), so a copied link or bookmark reopens exactly there.
- **Phone width:** no sideways page scroll. Wide tables scroll inside `.tablewrap`; checklist rows wrap to two lines. Test at about 520 px: headless Edge doesn't lay out narrower than about 500 px, so a 390 px screenshot is cropped, not reflowed.
- **Never style with inline colours.** If a colour isn't a token, add a token to all three blocks.
- Don't rely on hover alone for anything important: touch screens and Windows 95 users expect click.
- **Check all three looks** (Modern light, Modern dark, Windows 95) before calling a page change done, and check one narrow width. Headless Edge:
  ```powershell
  msedge --headless=new --hide-scrollbars --window-size=1000,900 --screenshot=out.png "file:///…/page.html?style=win95"
  ```

## 6. XML and other source data shown on a page
- Render source XML (exports, SimaticML, tag lists) into the page's own components, such as tables, cards and `.code`. Don't dump raw XML unless the reader needs it. When they do, show it in `.code` with `white-space:pre-wrap`, and offer Copy.
- Escape every value taken from source data before it goes into HTML.
- Values and addresses use `--mono`. Names and descriptions use the UI font.
