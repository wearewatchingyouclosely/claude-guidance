# Export a CODESYS project to text (PLCopen XML, tree, ST). The project itself is never opened: a copy is.
#   powershell -ExecutionPolicy Bypass -File export.ps1 -Project "<path\to\x.project>" -Out "<folder>"
param(
    [Parameter(Mandatory)] [string]$Project,
    [Parameter(Mandatory)] [string]$Out,
    [string]$CodesysExe, [string]$Profile
)
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\run_codesys.ps1"
$stage = New-CodesysStage "codesys_kit_export"
Copy-Item "$PSScriptRoot\cds_export.py" $stage
Copy-Item $Project "$stage\copy.project"
$a = @{ Script = "$stage\cds_export.py"; Env = @{ CDS_SRC = "$stage\copy.project"; CDS_OUT = "$stage\out" } }
if ($CodesysExe) { $a.CodesysExe = $CodesysExe }; if ($Profile) { $a.Profile = $Profile }
Invoke-Codesys @a
$log = Get-Content "$stage\out\_export_log.txt"
$log
if (-not ($log -match "RESULT: OK")) { throw "Export failed: $stage\out\_export_log.txt" }
New-Item -ItemType Directory -Force $Out | Out-Null
Copy-Item -Recurse -Force "$stage\out\*" $Out
Write-Host "Exported to $Out"
