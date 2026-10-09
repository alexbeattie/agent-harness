$root = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot '_common.ps1')
Invoke-Harness -Root $root -Arguments @($args)
exit $global:AgentHarnessExitCode
