# 50 — Dev branches and version control

How tool and app repos are branched, versioned, released and shared. Job workspaces usually aren't git repos: their versioning is the dated deliverable folders (00 §3).

## 1. Branches
| Branch | What | Who uses it |
|---|---|---|
| `main` | Releases only. Feature branches are merged in at release time | The dev session |
| `<area>` or `<area>/<topic>` | Dev work, one branch per feature area, e.g. `conversion-tool`, `gui`, `hmi-import-export`, `cleanup/project-agnostic`, `review/verify-hand-conversion` | The dev session |
| `public` | Released, project-agnostic, **history-free** (§4). The only branch that leaves the machine | Everyone else: job sessions, kit copies, GitHub |

- **Branch names never mention a job** (section 40).
- **One dev session owns a repo.** It's the only session that commits there. Job sessions use `public` and send reports (§6). This stops branch sprawl and half-finished work left on random branches.
- **At the start of a dev session, run `git status`.** Leftovers from another session get committed to their own branch, or you ask about them, before new work starts.
- Merge a feature branch into `main` only as part of a release. Unmerged branches are fine: list them in memory with their state.

## 2. Versions
- **Each tool inside the app has its own version**, in code (e.g. `AppVersions.cs`), and the **app has one version** (csproj `<Version>`). Bump rules:

  | Change | Tool version | App version |
  |---|---|---|
  | Fix or wording change in a tool | patch x.y.**Z** | rolls into the next release |
  | New feature or changed output of a tool | minor x.**Y**.0 | rolls into the next release |
  | Release (branch merged into `main`) | — | bump, local tag `vX.Y.Z` |
  | Tests, scripts, docs, notes | none | none |
  | GUI-only polish | none unless a tool window's behaviour changes | rolls into the next release |

- Bump once per branch per tool, not once per commit.
- **Check the versions on every commit**, before writing the message, and **name the bump in the message** ("SLC converter 0.2.3 → 0.3.0").
- 1.0 only when the user calls the tool released.
- Commit messages: imperative and generic. Use the repo's existing git identity (`git -c user.name=… -c user.email=…`); don't change the global config. In PowerShell, pass multi-line messages with `-F <file>`.

## 3. Dev folder vs release folder
- **Dev folder:** the clone, with a dev branch checked out and the dev build's exe in its root. Only the dev session works here.
- **Release folder:** a **detached worktree of `public`**, with the release exe in its root (gitignored). This is the folder that is linked to job workspaces and handed to users.

  ```powershell
  git -C <dev folder> worktree add --detach <release folder> public
  ```

  - Detached so that `git branch -f public …` still works.
  - **After every update to `public`:** run `git -C <release folder> checkout --detach public`, and on a version release copy the new release exe into it.
- **Build the release exe from `public`** in a scratch worktree. Never overwrite the dev folder's exe with a release build. A rebuild changes the exe hash, and hash-based approvals then have to be granted again.
- **Copying a repo that has worktrees:** the worktree's `.git` file and the main repo's `.git\worktrees\<name>\gitdir` store absolute paths.
  - After copying both folders, run `git -C <new main> worktree repair <new worktree>`. Then check that `git worktree list` is right in **both** the old and the new location.
  - `repair` also rewrites any other worktree it finds through the copied metadata, e.g. a scratch worktree. Point those back with `git -C <old main> worktree repair <path>`, and delete their stale entries from the copy's `.git\worktrees\`.

## 4. The history-free public branch
Private history usually holds job data in old diffs and messages. Cleaning the files doesn't remove it, so only a branch that never shared that history is published:
```bash
# first public commit: main's tree, no parents
git branch public $(git commit-tree main^{tree} -m "<Tool> vX.Y.Z")
# each later release: main's tree, parent = previous public commit
git branch -f public $(git commit-tree main^{tree} -p public -m "<Tool> vX.Y.Z")
```
- Before each release, grep the whole tree for job words (40 §5).
- **Push only `public`** (`git push origin public`), and only when the user asks.
  - **Never push `main`, other branches or local tags.** Tags point into the private history.
  - Never use an editor's "Publish Branch" on `main`.
- Release exes are uploaded on the hosting site's Releases page, with the tag created there on `public`.
- A docs-only fix after a release: commit it on `main`, then add a `public` commit with the same tree and the same version ("vX.Y.Z (docs only)"). No version bump.

## 5. Kits and shared docs inside a repo
- Generic kits (CLAUDE.md template, agents, lessons, hardware notes) live in the tool repo under `project-kit\` and ship through `public`.
- Job sessions take the kit from `public`, e.g. with `git archive public project-kit | tar -x -C <dest>`. They never take it from the dev folder, which may have an older copy or none at all.
- Kit changes go through a branch like any other change. In `.gitignore`, use `/.claude/` (root only) so that the kit's own `.claude/agents` stay tracked.

## 6. Reports from job sessions to the dev session
A job session never edits the tool. It writes `deliverables\YYYY-MM-DD_TOOL_<TOPIC>\README.md` (or `..._LESSONS_<TOPIC>` for kit lessons). The user hands it to the dev session. Layout, in this order:
1. **Status:** dated lines: written; checked against which version, branch and commit (`public` vX.Y.Z); later "implemented in vX.Y.Z" or "declined".
2. **For the tool developer, read first:**
   - the repo rules (no job data);
   - the version bump you'd expect;
   - "test on a test project, never a job project".
3. **Problem:** what goes wrong and why it matters, in generic words, with one observed case with numbers.
4. **Current behaviour (code):** file, method and approximate line numbers.
5. **Proposed behaviour:** numbered, including defaults, GUI wording, headless flags and messages.
6. **Design notes:** API shape, edge cases, what must not change.
7. **Acceptance tests:** a table (# / setup / option / expected) that a test project can reproduce.
8. **Out of scope / related ideas:** one line each.
9. **Stays with this job:** where it happened, which package is waiting. This is the only job-specific part.

Write one problem per report. The dev session treats the report as a feature request and confirms the scope with the user before building.
