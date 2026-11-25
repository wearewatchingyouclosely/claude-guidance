# Shared launcher for headless CODESYS scripts. Dot-source it:  . "$PSScriptRoot\run_codesys.ps1"
# See rules/21_CODESYS_PROJECTS.md §2 for why it works this way.

$script:DefaultCodesysExe = "C:\Program Files (x86)\CODESYS 3.5.22.30\CODESYS\Common\CODESYS.exe"
$script:DefaultProfile    = "CODESYS V3.5 SP22 Patch 3"

function New-CodesysStage([string]$Name) {
    # CODESYS --runscript breaks on paths with spaces. The temp folder (8.3 form) has none.
    $stage = Join-Path ([System.IO.Path]::GetTempPath()) $Name
    if ($stage -match " ") { throw "Temp path has spaces: $stage. Set TEMP to a folder without spaces." }
    if (Test-Path $stage) { Remove-Item -Recurse -Force $stage }
    New-Item -ItemType Directory -Force $stage | Out-Null
    return $stage
}

function Invoke-Codesys {
    param(
        [Parameter(Mandatory)] [string]$Script,     # .py in a path without spaces
        [hashtable]$Env = @{},                      # paths for the script (no spaces)
        [string]$CodesysExe = $script:DefaultCodesysExe,
        [string]$Profile = $script:DefaultProfile,
        [int]$TimeoutSec = 540
    )
    if ($Script -match " ") { throw "Script path has spaces: $Script" }
    if (-not (Test-Path $CodesysExe)) { throw "CODESYS.exe not found: $CodesysExe (pass -CodesysExe)" }
    # ProcessStartInfo, not & or Start-Process: those mangle the quoted --profile/--runscript arguments.
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $CodesysExe
    $psi.Arguments = "--profile=`"$Profile`" --noUI --runscript=`"$Script`""
    $psi.UseShellExecute = $false
    foreach ($k in $Env.Keys) {
        if ("$($Env[$k])" -match " ") { throw "Env $k has spaces: $($Env[$k])" }
        $psi.EnvironmentVariables[$k] = "$($Env[$k])"
    }
    $p = [System.Diagnostics.Process]::Start($psi)
    if (-not $p.WaitForExit($TimeoutSec * 1000)) { $p.Kill(); throw "CODESYS timed out after $TimeoutSec s: $Script" }
}
