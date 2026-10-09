$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$pwshPath = (Get-Process -Id $PID).Path
$targets = @(
    (Join-Path $root 'install.ps1'),
    (Join-Path $root 'check.ps1'),
    (Join-Path $root 'bin/_common.ps1'),
    (Join-Path $root 'bin/harness.ps1'),
    (Join-Path $root 'bin/hx.ps1'),
    (Join-Path $root 'bin/haws.ps1'),
    (Join-Path $root 'bin/htwg.ps1'),
    (Join-Path $root 'scripts/install-tools.ps1')
)
foreach ($path in $targets) {
    if (-not (Test-Path -LiteralPath $path)) { throw "Missing PowerShell entrypoint: $path" }
    $tokens = $null
    $errors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($path, [ref]$tokens, [ref]$errors) | Out-Null
    if ($errors.Count) { throw "PowerShell parse error in $path`: $($errors[0].Message)" }
}
. (Join-Path $root 'bin/_common.ps1')

$policies = @(
    [PSCustomObject]@{ Scope = 'MachinePolicy'; ExecutionPolicy = 'Undefined' },
    [PSCustomObject]@{ Scope = 'UserPolicy'; ExecutionPolicy = 'Undefined' },
    [PSCustomObject]@{ Scope = 'Process'; ExecutionPolicy = 'Bypass' },
    [PSCustomObject]@{ Scope = 'CurrentUser'; ExecutionPolicy = 'Undefined' },
    [PSCustomObject]@{ Scope = 'LocalMachine'; ExecutionPolicy = 'Undefined' }
)
if ((Get-InteractiveExecutionPolicy -Policies $policies) -ne 'Restricted') { throw 'An all-Undefined policy list must report the Windows client default, Restricted, and ignore the Bypass process scope.' }
$policies[3].ExecutionPolicy = 'RemoteSigned'
if ((Get-InteractiveExecutionPolicy -Policies $policies) -ne 'RemoteSigned') { throw 'CurrentUser RemoteSigned must win over Undefined LocalMachine.' }
$policies[0].ExecutionPolicy = 'AllSigned'
if ((Get-InteractiveExecutionPolicy -Policies $policies) -ne 'AllSigned') { throw 'MachinePolicy must win over CurrentUser.' }

$temp = Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString('N'))
try {
    $package = Join-Path $temp 'pack age'
    $output = Join-Path $temp 'arguments.json'
    New-Item -ItemType Directory -Path (Join-Path $package 'bin') -Force | Out-Null
    @'
import json, os
def main(args):
    with open(os.environ['HARNESS_TEST_ARGUMENTS'], 'w', encoding='utf-8') as f:
        json.dump(args, f)
    print('HARNESS_STDOUT_VISIBLE')
    return 7
'@ | Set-Content -LiteralPath (Join-Path $package 'harness.py') -Encoding utf8
    foreach ($name in 'launch.py', '_common.ps1', 'harness.ps1', 'hx.ps1', 'haws.ps1', 'htwg.ps1') {
        Copy-Item -LiteralPath (Join-Path $root "bin/$name") -Destination (Join-Path $package "bin/$name")
    }
    $env:HARNESS_TEST_ARGUMENTS = $output
    $prefixes = @{
        'harness.ps1' = @()
        'hx.ps1' = @('dispatch')
        'haws.ps1' = @('external', '--tool', 'aws', '--')
        'htwg.ps1' = @('external', '--tool', 'twg', '--')
    }
    $tail = @('ec2', 'create-tags', '--tags', 'Key=HarnessTest,Value=Denied', '--filters', 'Name=a,Values=b,c', '--task-file', 'a file;$(whoami).txt', '--task', 'double " quote and slash\', '--empty', '', 'after')
    foreach ($mode in 'Legacy', 'Standard') {
        foreach ($name in 'harness.ps1', 'hx.ps1', 'haws.ps1', 'htwg.ps1') {
            if (Test-Path -LiteralPath $output) { Remove-Item -LiteralPath $output -Force }
            $wrapper = (Join-Path $package "bin/$name").Replace("'", "''")
            $invokeText = @"
`$PSNativeCommandArgumentPassing = '$mode'
& '$wrapper' ec2 create-tags --tags Key=HarnessTest,Value=Denied --filters Name=a,Values=b,c --task-file 'a file;`$(whoami).txt' --task 'double " quote and slash\' --empty '' -- after
exit `$LASTEXITCODE
"@
            $invokePath = Join-Path $temp 'invoke.ps1'
            [IO.File]::WriteAllText($invokePath, $invokeText, [Text.UTF8Encoding]::new($false))
            $start = [Diagnostics.ProcessStartInfo]::new($pwshPath)
            $start.UseShellExecute = $false
            $start.RedirectStandardOutput = $true
            $start.RedirectStandardError = $true
            $start.Arguments = '-NoProfile -File "' + $invokePath + '"'
            $process = [Diagnostics.Process]::Start($start)
            $stdout = $process.StandardOutput.ReadToEnd()
            $stderr = $process.StandardError.ReadToEnd()
            $process.WaitForExit()
            if ($process.ExitCode -ne 7) { throw "$name ($mode) changed its exit code: $($process.ExitCode) $stderr" }
            if ($stdout -notmatch 'HARNESS_STDOUT_VISIBLE') { throw "$name ($mode) did not preserve native stdout." }
            $received = @(Get-Content -LiteralPath $output -Raw | ConvertFrom-Json)
            # PowerShell consumes a bare -- between a script and its arguments; everything after it must still arrive.
            $received = @($received | Where-Object { $_ -ne '--' -or $prefixes[$name] -contains '--' } )
            $expected = @($prefixes[$name]) + $tail
            if ($received.Count -ne $expected.Count -or (Compare-Object -ReferenceObject $expected -DifferenceObject $received -SyncWindow 0)) {
                throw "$name ($mode) changed argument boundaries: $($received -join '|')"
            }
        }
    }

    $oldBin = Join-Path $temp 'old copy/bin'
    New-Item -ItemType Directory -Path $oldBin -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $oldBin 'haws.ps1') -Value '# stale wrapper'
    Set-Content -LiteralPath (Join-Path (Split-Path -Parent $oldBin) 'harness.py') -Value '# stale package'
    $newBin = Join-Path $package 'bin'
    $entries = Get-UserPathEntries -Current ('C:\Windows;' + $oldBin + ';D:\Tools;' + $newBin + ';' + $newBin + '\') -Bin $newBin -Separator ';'
    $wanted = @('C:\Windows', 'D:\Tools', $newBin)
    if ($entries.Count -ne $wanted.Count -or (Compare-Object -ReferenceObject $wanted -DifferenceObject $entries -SyncWindow 0)) {
        throw "User PATH update kept a stale package bin or duplicated the new one: $($entries -join '|')"
    }

    $fixtureHome = Join-Path $temp 'Fixture Home'
    $pathBefore = [Environment]::GetEnvironmentVariable('Path', 'User')
    & (Join-Path $root 'install.ps1') -SkipTools -TargetHome $fixtureHome
    if ($global:AgentHarnessExitCode -ne 0) { throw "Fixture install failed with exit code $global:AgentHarnessExitCode" }
    if (-not (Test-Path -LiteralPath (Join-Path $fixtureHome '.agent-harness/install-state.json'))) {
        throw 'Fixture install did not generate the managed install manifest.'
    }
    if ([Environment]::GetEnvironmentVariable('Path', 'User') -ne $pathBefore) {
        throw 'Fixture install changed live user environment settings.'
    }
    $selectedHome = Join-Path $temp 'Codex only'
    & (Join-Path $root 'install.ps1') -SkipTools -TargetHome $selectedHome -Agents codex
    if ($global:AgentHarnessExitCode -ne 0) { throw 'Codex-only fixture install failed.' }
    if (-not (Test-Path -LiteralPath (Join-Path $selectedHome '.codex/agent-harness.config.toml'))) {
        throw 'Codex-only fixture lacks its profile.'
    }
    if (Test-Path -LiteralPath (Join-Path $selectedHome '.agent-harness/claude-plugin')) {
        throw 'Codex-only fixture installed the Claude plugin.'
    }
    if (Test-Path -LiteralPath (Join-Path $selectedHome '.agent-harness/cursor-user-rules.txt')) {
        throw 'Codex-only fixture installed Cursor User Rules.'
    }
    $mixedCaseHome = Join-Path $temp 'Mixed case Codex'
    & (Join-Path $root 'install.ps1') -SkipTools -TargetHome $mixedCaseHome -Agents Codex
    if ($global:AgentHarnessExitCode -ne 0 -or -not (Test-Path -LiteralPath (Join-Path $mixedCaseHome '.codex/agent-harness.config.toml'))) {
        throw 'Mixed-case Codex selection did not install Codex files.'
    }
    $upperHome = Join-Path $temp 'Uppercase all'
    & (Join-Path $root 'install.ps1') -SkipTools -TargetHome $upperHome -Agents ALL
    if ($global:AgentHarnessExitCode -ne 0 -or -not (Test-Path -LiteralPath (Join-Path $upperHome '.agent-harness/claude-plugin'))) {
        throw 'Uppercase ALL did not select every agent.'
    }
    $emptyHome = Join-Path $temp 'Empty selection'
    try {
        & (Join-Path $root 'install.ps1') -SkipTools -TargetHome $emptyHome -Agents @()
        throw 'Empty agent selection was accepted.'
    } catch {
        if ($_.Exception.Message -eq 'Empty agent selection was accepted.') { throw }
    }
    if (Test-Path -LiteralPath (Join-Path $emptyHome '.agent-harness/install-state.json')) {
        throw 'Empty agent selection changed fixture files.'
    }
    $checkOutput = & $pwshPath -NoProfile -File (Join-Path $root 'check.ps1') -TargetHome $selectedHome -Agents Codex 2>&1 | Out-String
    if ($checkOutput -notmatch 'Cross-provider Claude review and routed models: Pending') {
        throw 'check.ps1 did not forward the selected Codex agent.'
    }
    if ($checkOutput -match 'Cursor model status:') {
        throw 'Codex-only check evaluated Cursor model readiness.'
    }
} finally {
    Remove-Item -LiteralPath $temp -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item Env:HARNESS_TEST_ARGUMENTS -ErrorAction SilentlyContinue
}

Write-Host 'PowerShell syntax, execution-policy and PATH helpers, four-wrapper Legacy/Standard argument forwarding, exit-code, stdout and fixture-install tests passed.'
