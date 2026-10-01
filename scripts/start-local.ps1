#requires -Version 7.0
[CmdletBinding()]
param(
    [switch]$NoBuild,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RepoRoot = Split-Path -Parent $PSScriptRoot
$ComposeProd = Join-Path $RepoRoot "deployment/docker/docker-compose.prod.yml"
$ComposeLocal = Join-Path $RepoRoot "deployment/docker/docker-compose.local.yml"
$EnvFile = Join-Path $RepoRoot "deployment/docker/.env.local"

function Invoke-DockerCompose {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    & docker compose --env-file $EnvFile -f $ComposeProd -f $ComposeLocal @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "docker compose failed with exit code $LASTEXITCODE."
    }
}

Write-Host "=== ERPNext Business Suite - Local Environment ===" -ForegroundColor Cyan

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker CLI was not found. Install Docker Desktop and make sure the Docker daemon is running."
}

docker info *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Docker daemon is not reachable. Start Docker Desktop, then run this script again."
}

if (-not (Test-Path $ComposeProd)) { throw "Missing $ComposeProd" }
if (-not (Test-Path $ComposeLocal)) { throw "Missing $ComposeLocal" }

if (-not (Test-Path $EnvFile)) {
    Add-Type -AssemblyName System.Security
    function New-LocalSecret {
        param([int]$Length = 32)
        $bytes = New-Object byte[] $Length
        [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
        return [Convert]::ToBase64String($bytes).Replace("+","-").Replace("/","_").TrimEnd("=")
    }

    @"
ERPNEXT_IMAGE=frappe/erpnext:v16.36.0
CUSTOM_IMAGE=erpnext-business-suite
CUSTOM_TAG=local
SITE_NAME=erpnext.local
DB_ROOT_PASSWORD=$(New-LocalSecret)
ADMIN_PASSWORD=$(New-LocalSecret)
APP_PORT=8081
BUSINESS_UI_PORT=8080
FRAPPE_SITE_NAME_HEADER=erpnext.local
GUNICORN_WORKERS=2
GUNICORN_THREADS=4
GUNICORN_TIMEOUT=120
PROXY_READ_TIMEOUT=120
CLIENT_MAX_BODY_SIZE=50m
"@ | Set-Content -Path $EnvFile -Encoding utf8

    Write-Host "Created local environment file: $EnvFile" -ForegroundColor Green
    Write-Host "Keep this file private; it contains local development credentials." -ForegroundColor Yellow
}

if (-not $NoBuild) {
    Write-Host "Building local ERPNext Business Suite image..." -ForegroundColor Cyan
    & docker build --build-arg ERPNEXT_IMAGE=frappe/erpnext:v16.36.0 -t erpnext-business-suite:local -f "$RepoRoot/deployment/docker/Dockerfile" "$RepoRoot"
    if ($LASTEXITCODE -ne 0) { throw "Docker image build failed." }
} else {
    Write-Host "Skipping image build (-NoBuild)." -ForegroundColor DarkGray
}

Write-Host "Starting MariaDB, Redis, Frappe backend, workers and UI..." -ForegroundColor Cyan
Invoke-DockerCompose up -d db redis-cache redis-queue configurator create-site backend websocket queue-short queue-long scheduler frontend business-ui

Write-Host "Applying Frappe/ERPNext migrations..." -ForegroundColor Cyan
Invoke-DockerCompose run --rm create-site

Write-Host "Verifying services..." -ForegroundColor Cyan
Invoke-DockerCompose ps

Write-Host "Custom Business Suite UI : http://localhost:8080" -ForegroundColor Green
Write-Host "ERPNext/Frappe Desk      : http://localhost:8081" -ForegroundColor Green
Write-Host "Site                     : erpnext.local" -ForegroundColor Green
Write-Host "Administrator            : use the password stored in deployment/docker/.env.local" -ForegroundColor Green

if (-not $NoBrowser) {
    $chrome = @(
        "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
        "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
    ) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1

    if ($chrome) {
        Start-Process -FilePath $chrome -ArgumentList "http://localhost:8080"
        Write-Host "Chrome opened at http://localhost:8080" -ForegroundColor Green
    } else {
        Write-Host "Chrome was not found automatically. Open http://localhost:8080 manually." -ForegroundColor Yellow
    }
}

Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "docker compose --env-file deployment/docker/.env.local -f deployment/docker/docker-compose.prod.yml -f deployment/docker/docker-compose.local.yml logs -f backend"
Write-Host "docker compose --env-file deployment/docker/.env.local -f deployment/docker/docker-compose.prod.yml -f deployment/docker/docker-compose.local.yml run --rm create-site"
Write-Host "docker compose --env-file deployment/docker/.env.local -f deployment/docker/docker-compose.prod.yml -f deployment/docker/docker-compose.local.yml down"
