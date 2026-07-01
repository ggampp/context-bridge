[CmdletBinding()]
param(
    [string]$Project = "."
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

function Step($name, [scriptblock]$action) {
    Write-Host ""
    Write-Host "== $name ==" -ForegroundColor Cyan
    & $action
    if ($LASTEXITCODE -ne 0) {
        Write-Host "FAILED: $name" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

# Like Step, but non-fatal: used for steps that depend on an optional backend
# (Engram) being reachable. A WARN here mirrors `doctor`'s WARN/FAIL split —
# missing Engram is an expected degraded state, not a smoke failure.
function StepSoft($name, [scriptblock]$action) {
    Write-Host ""
    Write-Host "== $name ==" -ForegroundColor Cyan
    & $action
    if ($LASTEXITCODE -ne 0) {
        Write-Host "WARN: $name (non-fatal — run 'context-bridge doctor' to check the Engram backend)" -ForegroundColor Yellow
    }
}

Push-Location $repoRoot
try {
    Step "pytest (offline)" { pytest -q -m "not network" }
    Step "doctor" { context-bridge doctor --project $Project }
    Step "sync --dry-run" { context-bridge sync --project $Project --dry-run --verbose }
    StepSoft "enrich" { context-bridge enrich "authentication flow" --project $Project --json --limit 5 }
    Step "suggest" { context-bridge suggest --project $Project }
    Step "graph stats" { context-bridge graph stats --project $Project }
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "Smoke test passed." -ForegroundColor Green
exit 0
