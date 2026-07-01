[CmdletBinding()]
param(
    [string]$Project = ".",
    [string]$Env = "auto",
    [switch]$DryRun,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

Write-Host "== Context Bridge install ==" -ForegroundColor Cyan

Push-Location $repoRoot
try {
    pip install -e ".[mcp]" --quiet
} finally {
    Pop-Location
}

$cmdArgs = @("install", "--project", $Project, "--env", $Env)
if ($DryRun) { $cmdArgs += "--dry-run" }
if ($Force) { $cmdArgs += "--force" }

& context-bridge @cmdArgs
exit $LASTEXITCODE
