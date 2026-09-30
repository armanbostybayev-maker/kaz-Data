$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontend = Join-Path $projectRoot "apps\frontend"

Push-Location $frontend
try {
    & npm.cmd install
    if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
    & npm.cmd run build:static
    if ($LASTEXITCODE -ne 0) { throw "Static build failed" }
    Write-Host "Static atlas built: $frontend\out" -ForegroundColor Green
} finally {
    Pop-Location
}
