$root = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot '_common.ps1')
Invoke-Harness -Root $root -Arguments (@('dispatch') + @($args))
exit $global:AgentHarnessExitCode
