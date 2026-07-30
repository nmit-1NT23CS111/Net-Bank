# Net Bank Frontend Setup and Run Script
# This script installs dependencies and starts the Vite development server

$ErrorActionPreference = "Stop"

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  Net Bank React + Vite Setup  " -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check if Node.js is installed
Write-Host "`nChecking for Node.js..." -ForegroundColor Yellow
$nodeVersion = node -v 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Node.js is not installed. Please install Node.js from https://nodejs.org/" -ForegroundColor Red
    exit 1
}
Write-Host "Node.js $nodeVersion found" -ForegroundColor Green

# Check if npm is installed
Write-Host "Checking for npm..." -ForegroundColor Yellow
$npmVersion = npm -v 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "npm is not installed. Please install Node.js which includes npm." -ForegroundColor Red
    exit 1
}
Write-Host "npm $npmVersion found" -ForegroundColor Green

# Install dependencies
if (-not (Test-Path ".\node_modules")) {
    Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    Write-Host "Dependencies installed successfully" -ForegroundColor Green
}
else {
    Write-Host "`nDependencies already installed" -ForegroundColor Green
}

# Start the development server
Write-Host "`nStarting development server..." -ForegroundColor Yellow
Write-Host "The application will run at http://localhost:5173" -ForegroundColor Cyan
npm run dev

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start the development server" -ForegroundColor Red
    exit 1
}
