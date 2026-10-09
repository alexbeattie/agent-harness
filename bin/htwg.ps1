$root = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot '_common.ps1')
Invoke-Harness -Root $root -Arguments (@('external', '--tool', 'twg', '--') + @($args))
exit $global:AgentHarnessExitCode
