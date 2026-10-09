param(
    [switch]$SkipTools,
    [string]$TargetHome,
    [string[]]$Agents = @('all'),
    [switch]$IncludeServices
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($Agents.Count -eq 0) { throw 'Choose cursor, codex, claude, or all.' }
$Agents = @($Agents | ForEach-Object {
    if ([string]::IsNullOrWhiteSpace($_)) { throw 'Choose cursor, codex, claude, or all.' }
    $_.ToLowerInvariant()
})
if ('all' -in $Agents -and $Agents.Count -ne 1) { throw 'Do not mix all with named agents.' }
if (@($Agents | Where-Object { $_ -notin @('all', 'cursor', 'codex', 'claude') }).Count) { throw 'Choose cursor, codex, claude, or all.' }
. (Join-Path $root 'bin/_common.ps1')
$fixtureMode = -not [string]::IsNullOrWhiteSpace($TargetHome)
if (-not $TargetHome) { $TargetHome = $env:USERPROFILE }
if (-not $TargetHome) { throw 'The current user home could not be determined. Pass -TargetHome explicitly.' }
if ($fixtureMode -and -not $SkipTools) {
    throw 'A custom -TargetHome is fixture-only. Use -SkipTools to avoid installing tools or changing live user settings.'
}
if (-not $SkipTools) {
    if ($env:OS -ne 'Windows_NT') { throw 'Tool installation is supported on native Windows only. Use -SkipTools for a local generation fixture.' }
    & (Join-Path $root 'scripts/install-tools.ps1') -Agents $Agents -IncludeServices:$IncludeServices
}

$arguments = @('generate', '--home', $TargetHome)
foreach ($agent in $Agents) { $arguments += @('--agent', $agent) }
Invoke-Harness -Root $root -Arguments $arguments
if ($global:AgentHarnessExitCode -ne 0) { throw "Managed file generation failed with exit code $global:AgentHarnessExitCode. Existing user files were preserved." }

if (-not $fixtureMode) {
    $bin = Join-Path $root 'bin'
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    $updated = (Get-UserPathEntries -Current $userPath -Bin $bin) -join ';'
    if ($updated -ne $userPath) {
        [Environment]::SetEnvironmentVariable('Path', $updated, 'User')
    }
}

Write-Host 'Selected harness files are installed. Reopen PowerShell and run check.ps1 with the same -Agents selection.'
if ('cursor' -in $Agents -or 'all' -in $Agents) { Write-Host 'Cursor User Rules need manual setup in Cursor.' }
if ($fixtureMode) { Write-Host 'Fixture mode: no tools were installed and no live user environment settings were changed.' }
