function Get-InteractiveExecutionPolicy {
    # The policy a normal terminal applies to the wrappers; the Process scope is skipped because install.ps1 and check.ps1 run under a bypass.
    param([object[]]$Policies)
    foreach ($scope in 'MachinePolicy', 'UserPolicy', 'CurrentUser', 'LocalMachine') {
        $entry = $Policies | Where-Object { "$($_.Scope)" -eq $scope } | Select-Object -First 1
        if ($entry -and "$($entry.ExecutionPolicy)" -ne 'Undefined') { return "$($entry.ExecutionPolicy)" }
    }
    return 'Restricted'
}

function Get-UserPathEntries {
    # Keep every entry except bin folders of other package copies, then append this package once.
    param([string]$Current, [string]$Bin, [string]$Separator = ';')
    $target = $Bin.TrimEnd('\')
    $kept = foreach ($entry in @($Current -split [regex]::Escape($Separator) | Where-Object { $_ })) {
        if ($entry.TrimEnd('\') -ieq $target) { continue }
        $parent = [IO.Path]::GetDirectoryName($entry.TrimEnd('\'))
        $stale = $parent -and (Test-Path -LiteralPath ([IO.Path]::Combine($entry, 'haws.ps1')) -PathType Leaf) -and
                 (Test-Path -LiteralPath ([IO.Path]::Combine($parent, 'harness.py')) -PathType Leaf)
        if ($stale) { continue }
        $entry
    }
    return @($kept) + @($target)
}

function Find-HarnessPython {
    $names = @('python3.14', 'python3.13', 'python3.12', 'python3.11', 'python3', 'python')
    foreach ($name in $names) {
        $command = Get-Command -Name $name -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
        if (-not $command) { continue }
        $path = $command.Source
        if ($env:OS -eq 'Windows_NT' -and $path -notmatch '(?i)\.exe$') { continue }
        if ($path -match '(?i)[\\/]WindowsApps[\\/]') { continue }
        $version = & $path -c 'import sys; print(str(sys.version_info.major)+chr(46)+str(sys.version_info.minor))' 2>$null
        if ($LASTEXITCODE -eq 0 -and $version -match '^3\.(\d+)$' -and [int]$Matches[1] -ge 11) {
            return [PSCustomObject]@{ Path = $path; Prefix = @() }
        }
    }
    $launcher = Get-Command -Name py -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($launcher -and $launcher.Source -notmatch '(?i)[\\/]WindowsApps[\\/]' -and
        ($env:OS -ne 'Windows_NT' -or $launcher.Source -match '(?i)\.exe$')) {
        $version = & $launcher.Source -3 -c 'import sys; print(str(sys.version_info.major)+chr(46)+str(sys.version_info.minor))' 2>$null
        if ($LASTEXITCODE -eq 0 -and $version -match '^3\.(\d+)$' -and [int]$Matches[1] -ge 11) {
            return [PSCustomObject]@{ Path = $launcher.Source; Prefix = @('-3') }
        }
    }
    throw 'Python 3.11 or later was not found. Install it with install.ps1, then reopen PowerShell.'
}

function Invoke-Harness {
    param([string]$Root, [object[]]$Arguments)
    $resolvedRoot = (Resolve-Path -LiteralPath $Root).Path
    $python = Find-HarnessPython
    # An unquoted a,b argument reaches a script as an array; a native program would receive the comma, so rejoin it.
    $flat = [string[]]@(foreach ($item in @($Arguments)) { if ($item -is [array]) { @($item) -join ',' } else { [string]$item } })
    $payload = Join-Path ([IO.Path]::GetTempPath()) ('agent-harness-' + [guid]::NewGuid().ToString('N') + '.json')
    try {
        $json = ConvertTo-Json -InputObject $flat -Compress
        [IO.File]::WriteAllText($payload, $json, [Text.UTF8Encoding]::new($false))
        $argv = @($python.Prefix) + @((Join-Path $resolvedRoot 'bin/launch.py'), $payload, $resolvedRoot)
        & $python.Path @argv
        $global:AgentHarnessExitCode = [int]$LASTEXITCODE
    } finally {
        Remove-Item -LiteralPath $payload -Force -ErrorAction SilentlyContinue
    }
}
