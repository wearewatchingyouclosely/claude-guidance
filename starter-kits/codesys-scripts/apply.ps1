# Build a CODESYS project from a template and a make_io.py build folder, then export and check it.
#   python -I make_io.py io_table.csv --out build --io-parent <name> ...
#   powershell -ExecutionPolicy Bypass -File apply.ps1 -Template <t.project> -Build build -Output <x.project> [-Force]
# The template is copied; it is never changed. Output is written only if the CODESYS build has no errors
# AND the export matches the table. A rebuild replaces Output, so it discards edits made in the IDE (-Force).
param(
    [Parameter(Mandatory)] [string]$Template,
    [Parameter(Mandatory)] [string]$Build,
    [Parameter(Mandatory)] [string]$Output,
    [switch]$Force,
    [string]$CodesysExe, [string]$Profile
)
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\run_codesys.ps1"
if ((Test-Path $Output) -and -not $Force) { throw "$Output exists. Re-run with -Force to replace it (IDE edits are lost)." }
if (-not (Test-Path $Template)) { throw "Template not found: $Template" }
$outParent = Split-Path -Parent $Output
if ($outParent) { New-Item -ItemType Directory -Force $outParent | Out-Null }
$Build = (Resolve-Path $Build).Path

$stage = New-CodesysStage "codesys_kit_apply"
New-Item -ItemType Directory -Force "$stage\build", "$stage\log", "$stage\export" | Out-Null
Copy-Item "$PSScriptRoot\cds_apply.py", "$PSScriptRoot\cds_export.py" $stage
Copy-Item "$Build\*" "$stage\build"
Copy-Item $Template "$stage\work.project"
$opt = @{}; if ($CodesysExe) { $opt.CodesysExe = $CodesysExe }; if ($Profile) { $opt.Profile = $Profile }

Invoke-Codesys -Script "$stage\cds_apply.py" -Env @{ CDS_SRC = "$stage\work.project"; CDS_BUILD = "$stage\build"; CDS_OUT = "$stage\log" } @opt
$log = Get-Content "$stage\log\apply_log.txt"
$log | Where-Object { $_ -notmatch "^  \S+\.(Input|Output) value" }
if (-not ($log -match "RESULT: OK")) { throw "Apply failed: $stage\log\apply_log.txt" }

Copy-Item "$stage\work.project" "$stage\export_copy.project"
Invoke-Codesys -Script "$stage\cds_export.py" -Env @{ CDS_SRC = "$stage\export_copy.project"; CDS_OUT = "$stage\export" } @opt
python -I "$PSScriptRoot\make_io.py" --check "$stage\build" --export "$stage\export"
if ($LASTEXITCODE -ne 0) { throw "Export does not match the table; $Output not written. See $stage\export" }

Copy-Item "$stage\work.project" $Output -Force
$exp = Join-Path (Split-Path -Parent $Output) "export"
if (Test-Path $exp) { Remove-Item -Recurse -Force $exp }
New-Item -ItemType Directory -Force $exp | Out-Null
Copy-Item -Recurse "$stage\export\*" $exp
Copy-Item "$stage\log\apply_log.txt", "$Build\IO_List.md" $exp
Write-Host "Built $Output (export in $exp)"
