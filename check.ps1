param(
    [switch]$ProbeModels,
    [string]$TargetHome = $env:USERPROFILE
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $root 'bin/_common.ps1')
if (-not $TargetHome) { throw 'The current user home could not be determined. Pass -TargetHome explicitly.' }
$arguments = @('check', '--home', $TargetHome)
if ($ProbeModels) { $arguments += '--probe-models' }
Invoke-Harness -Root $root -Arguments $arguments
if ($env:OS -eq 'Windows_NT') {
    $policy = Get-InteractiveExecutionPolicy -Policies (Get-ExecutionPolicy -List)
    if ($policy -in 'RemoteSigned', 'Unrestricted', 'Bypass') {
        Write-Host "Execution policy: $policy lets a normal terminal run harness, hx, haws and htwg."
    } else {
        Write-Host "Execution policy: $policy stops a normal terminal from running harness, hx, haws and htwg. With IT approval run Set-ExecutionPolicy -Scope CurrentUser RemoteSigned, then rerun check.ps1."
        $global:AgentHarnessExitCode = 1
    }
    $bin = (Join-Path $root 'bin').TrimEnd('\')
    foreach ($name in 'harness', 'hx', 'haws', 'htwg') {
        $command = Get-Command -Name $name -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($command -and $command.Source -and ((Split-Path -Parent $command.Source).TrimEnd('\') -ieq $bin)) {
            Write-Host "Command ${name}: resolves to this package."
        } else {
            Write-Host "Command ${name}: not found on PATH in this terminal. Quit Cursor completely and start it again, or rerun install.ps1."
            $global:AgentHarnessExitCode = 1
        }
    }
}
exit $global:AgentHarnessExitCode
