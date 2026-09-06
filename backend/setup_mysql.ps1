param(
    [string]$RootUser = "root",
    [string]$RootPassword = "",
    [string]$DatabaseName = "net_bank",
    [switch]$SkipSeed
)

$ErrorActionPreference = "Stop"

function Invoke-Step {
    param(
        [string]$Title,
        [scriptblock]$Action
    )

    Write-Host ""
    Write-Host "==> $Title" -ForegroundColor Cyan
    & $Action
}

$BackendDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $BackendDir

if ($env:MYSQL_ROOT_PASSWORD) {
    $RootPassword = $env:MYSQL_ROOT_PASSWORD
}

if (-not $RootPassword) {
    $RootPassword = Read-Host "MySQL root password"
}

$setupSql = @"
CREATE DATABASE IF NOT EXISTS ``$DatabaseName`` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
FLUSH PRIVILEGES;
SHOW DATABASES LIKE '$DatabaseName';
"@

Invoke-Step "Checking MySQL client" {
    mysql --version
}

Invoke-Step "Creating MySQL database" {
    $env:MYSQL_PWD = $RootPassword
    try {
        $setupSql | mysql -u $RootUser -h 127.0.0.1
    }
    finally {
        Remove-Item Env:\MYSQL_PWD -ErrorAction SilentlyContinue
    }
}

$envContent = @"
DJANGO_SECRET_KEY=$([guid]::NewGuid().ToString())-$([guid]::NewGuid().ToString())
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

MYSQL_DATABASE=$DatabaseName
MYSQL_USER=$RootUser
MYSQL_PASSWORD=$RootPassword
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306

MAX_TRANSFERS_PER_HOUR=10
"@

Invoke-Step "Writing backend .env" {
    Set-Content -Path ".env" -Value $envContent -Encoding ASCII
    Write-Host ".env written for database '$DatabaseName' using MySQL user '$RootUser'."
}

if (-not (Test-Path ".\venv\Scripts\python.exe")) {
    Invoke-Step "Creating Python virtual environment" {
        python -m venv venv
    }
}

Invoke-Step "Installing Python dependencies" {
    .\venv\Scripts\python.exe -m pip install -r requirements.txt
}

Invoke-Step "Running Django migrations" {
    .\venv\Scripts\python.exe manage.py migrate
}

if (-not $SkipSeed) {
    Invoke-Step "Seeding demo users, accounts, and transactions" {
        .\venv\Scripts\python.exe manage.py seed_demo
    }
}

Invoke-Step "Verifying MySQL tables" {
    $env:MYSQL_PWD = $RootPassword
    try {
        mysql -u $RootUser -h 127.0.0.1 $DatabaseName -e "SHOW TABLES; SELECT TABLE_NAME, TABLE_ROWS FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '$DatabaseName' ORDER BY TABLE_NAME;"
    }
    finally {
        Remove-Item Env:\MYSQL_PWD -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host "Setup complete." -ForegroundColor Green
Write-Host "Backend:  cd `"$BackendDir`"; .\venv\Scripts\python.exe manage.py runserver 8000"
Write-Host "Frontend: cd `"$((Resolve-Path "$BackendDir\..\frontend").Path)`"; npm run dev"
Write-Host ""
Write-Host "Run 'python manage.py seed_demo' to create local demo data and receive generated credentials."
