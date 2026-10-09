$root = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot '_common.ps1')
Invoke-Harness -Root $root -Arguments (@('external', '--tool', 'aws', '--') + @($args))
exit $global:AgentHarnessExitCode
