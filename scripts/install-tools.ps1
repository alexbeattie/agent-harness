param([switch]$SkipTools, [string[]]$Agents = @('all'), [switch]$IncludeServices)
$ErrorActionPreference = 'Stop'
if ($SkipTools) { return }
if ($env:OS -ne 'Windows_NT') { throw 'Tool installation requires native Windows. WSL is not used by this installer.' }
if ($Agents.Count -eq 0) { throw 'Choose cursor, codex, claude, or all.' }
$Agents = @($Agents | ForEach-Object {
    if ([string]::IsNullOrWhiteSpace($_)) { throw 'Choose cursor, codex, claude, or all.' }
    $_.ToLowerInvariant()
})
if ('all' -in $Agents -and $Agents.Count -ne 1) { throw 'Do not mix all with named agents.' }
if (@($Agents | Where-Object { $_ -notin @('all', 'cursor', 'codex', 'claude') }).Count) { throw 'Choose cursor, codex, claude, or all.' }
if ($Agents -eq 'all') { $Agents = @('cursor', 'codex', 'claude') }
. (Join-Path (Split-Path -Parent $PSScriptRoot) 'bin/_common.ps1')

function Get-NativeCommand {
    param([string]$Name)
    return Get-Command -Name ($Name + '.exe') -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
}

function Refresh-ProcessPath {
    $machinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = @($machinePath, $userPath) -join ';'
}

function Test-Python311 {
    try { $null = Find-HarnessPython; return $true } catch { return $false }
}

function Invoke-WingetInstall {
    param([string]$Id, [switch]$Portable)
    $winget = Get-NativeCommand 'winget'
    if (-not $winget) { throw "WinGet is required to install $Id. Install App Installer from Microsoft Store, then retry." }
    $arguments = @('install', '--id', $Id, '--exact', '--source', 'winget',
                   '--accept-source-agreements', '--accept-package-agreements', '--silent')
    if (-not $Portable) { $arguments += @('--scope', 'user') }
    & $winget.Source @arguments
    if ($LASTEXITCODE -notin @(0, 3010)) { throw "WinGet failed to install $Id (exit $LASTEXITCODE)." }
    Refresh-ProcessPath
}

function Install-Codex {
    $previous = $env:CODEX_NON_INTERACTIVE
    try {
        $env:CODEX_NON_INTERACTIVE = '1'
        $response = Invoke-WebRequest -UseBasicParsing -Uri 'https://chatgpt.com/codex/install.ps1' -MaximumRedirection 5 -TimeoutSec 30
        $finalUri = $response.BaseResponse.ResponseUri
        if (-not $finalUri -and $response.BaseResponse.RequestMessage) { $finalUri = $response.BaseResponse.RequestMessage.RequestUri }
        if (-not $response.Content -or -not $finalUri -or $finalUri.Host -notin @('chatgpt.com', 'releases.openai.com')) {
            throw 'The Codex installer response did not come from an official OpenAI host.'
        }
        $installer = [scriptblock]::Create($response.Content)
        & $installer
        Refresh-ProcessPath
    } finally {
        $env:CODEX_NON_INTERACTIVE = $previous
    }
    if (-not (Get-NativeCommand 'codex')) { throw 'The official Codex installer finished, but native codex.exe is still missing from PATH. Reopen PowerShell and retry.' }
}

function Install-SignedMsi {
    param([string]$Uri, [string]$SignerPattern, [string]$Name)
    $destination = Join-Path ([IO.Path]::GetTempPath()) ("agent-harness-" + [guid]::NewGuid().ToString('N') + '.msi')
    try {
        Invoke-WebRequest -UseBasicParsing -Uri $Uri -OutFile $destination -MaximumRedirection 5 -TimeoutSec 180
        $signature = Get-AuthenticodeSignature -LiteralPath $destination
        if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch $SignerPattern) {
            throw "$Name installer signature was not valid for the expected publisher."
        }
        $process = Start-Process -FilePath 'msiexec.exe' -ArgumentList @('/i', ('"' + $destination + '"'), '/qn', '/norestart') -Wait -PassThru
        if ($process.ExitCode -notin @(0, 3010)) { throw "$Name MSI failed with exit code $($process.ExitCode)." }
        if ($process.ExitCode -eq 3010) { Write-Warning "$Name installed. Reopen PowerShell to refresh PATH." }
        Refresh-ProcessPath
    } finally {
        Remove-Item -LiteralPath $destination -Force -ErrorAction SilentlyContinue
    }
}

if (-not (Get-NativeCommand 'git')) { Invoke-WingetInstall 'Git.Git' }
if (-not (Test-Python311)) { Invoke-WingetInstall 'Python.Python.3.13' }
if ('cursor' -in $Agents) { Write-Host 'Cursor app: Install from the official Cursor download if needed; sign in and set User Rules in the app.' }
if ('codex' -in $Agents -and -not (Get-NativeCommand 'codex')) { Install-Codex }
if ('claude' -in $Agents -and -not (Get-NativeCommand 'claude')) { Invoke-WingetInstall 'Anthropic.ClaudeCode' -Portable }
if ($IncludeServices -and -not (Get-NativeCommand 'aws')) {
    Install-SignedMsi 'https://awscli.amazonaws.com/AWSCLIV2-User.msi' 'Amazon' 'AWS CLI'
}
if ($IncludeServices -and -not (Get-NativeCommand 'twg')) {
    $architecture = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString()
    if ($architecture -eq 'Arm64') { $twgUrl = 'https://teamwork-graph.atlassian.com/cli/twg-windows-arm64.msi' }
    else { $twgUrl = 'https://teamwork-graph.atlassian.com/cli/twg-windows-x64.msi' }
    Install-SignedMsi $twgUrl 'Atlassian' 'TWG CLI'
}

Write-Host 'Selected command-line tools are installed. No sign-in was started.'
