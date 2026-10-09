param(
    [switch]$SkipTools,
    [string]$TargetHome
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $root 'bin/_common.ps1')
$fixtureMode = -not [string]::IsNullOrWhiteSpace($TargetHome)
if (-not $TargetHome) { $TargetHome = $env:USERPROFILE }
if (-not $TargetHome) { throw 'The current user home could not be determined. Pass -TargetHome explicitly.' }
if ($fixtureMode -and -not $SkipTools) {
    throw 'A custom -TargetHome is fixture-only. Use -SkipTools to avoid installing tools or changing live user settings.'
}
if (-not $SkipTools) {
    if ($env:OS -ne 'Windows_NT') { throw 'Tool installation is supported on native Windows only. Use -SkipTools for a local generation fixture.' }
    & (Join-Path $root 'scripts/install-tools.ps1')
}

Invoke-Harness -Root $root -Arguments @('generate', '--home', $TargetHome)
if ($global:AgentHarnessExitCode -ne 0) { throw "Managed file generation failed with exit code $global:AgentHarnessExitCode. Existing user files were preserved." }

if (-not $fixtureMode) {
    $bin = Join-Path $root 'bin'
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    $updated = (Get-UserPathEntries -Current $userPath -Bin $bin) -join ';'
    if ($updated -ne $userPath) {
        [Environment]::SetEnvironmentVariable('Path', $updated, 'User')
    }
}

Write-Host 'Harness files are installed. Quit Cursor completely, start it again, then run check.ps1 to verify the execution policy, tool sign-in and configured models.'
if ($fixtureMode) { Write-Host 'Fixture mode: no tools were installed and no live user environment settings were changed.' }
