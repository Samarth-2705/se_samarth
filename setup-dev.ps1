<#
  setup-dev.ps1
  Usage: Open PowerShell in D:\GIT\se_samarth and run:
    .\setup-dev.ps1
  If you get an execution policy error, run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
#>

# Fail fast
$ErrorActionPreference = "Stop"

# Paths
$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"
$venv = Join-Path $backend "venv"

Write-Host "Working directory: $root"

# 1) Create & activate venv for backend
if (-Not (Test-Path $venv)) {
    Write-Host "Creating virtual environment..."
    python -m venv $venv
} else {
    Write-Host "Virtual environment already exists."
}

# Activate venv (PowerShell activation script)
$activateScript = Join-Path $venv "Scripts\Activate.ps1"
if (-Not (Test-Path $activateScript)) {
    throw "Activation script not found at $activateScript"
}
Write-Host "Activating virtual environment..."
& $activateScript

# 2) Install backend dependencies
Write-Host "Installing backend dependencies..."
Push-Location $backend
if (-Not (Test-Path "requirements.txt")) {
    Write-Host "WARNING: requirements.txt not found in backend. Skipping pip install."
} else {
    pip install --upgrade pip
    pip install -r requirements.txt
}

# 3) Create backend .env (SQLite dev)
Write-Host "Creating backend .env for SQLite..."
$envContent = @"
DATABASE_URL=sqlite:///admission_system.db
SECRET_KEY=devsecret_change_me
JWT_SECRET_KEY=devjwt_change_me
MAIL_SERVER=
MAIL_PORT=
MAIL_USERNAME=
MAIL_PASSWORD=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
"@
$envPath = Join-Path $backend ".env"
$envContent | Out-File -FilePath $envPath -Encoding UTF8
Write-Host "Created $envPath"

# 4) Try to initialize DB using Flask CLI if available
$flaskCmd = ""
try {
    # set FLASK_APP if repo uses run.py
    $env:FLASK_APP = "run.py"
    Write-Host "Attempting 'flask init-db' and 'flask seed-db' (if implemented)..."
    python -m flask init-db
    python -m flask seed-db
} catch {
    Write-Host "flask init/seed not available or failed. Skipping. (This is okay if the project creates DB on startup.)"
    Write-Host "Exception: $($_.Exception.Message)"
}

# 5) Start backend in background (run in a new PowerShell window)
Write-Host "Starting backend (opens a new PowerShell window)..."
$startBackendScript = @"
cd `"$backend`"
`"$venv\Scripts\python.exe`" run.py
"@
$startBackendPath = Join-Path $root "start-backend.ps1"
$startBackendScript | Out-File -FilePath $startBackendPath -Encoding UTF8
Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-File",$startBackendPath

Pop-Location

# 6) Setup & start frontend
Write-Host "Setting up frontend..."
if (-Not (Test-Path $frontend)) {
    Write-Host "ERROR: frontend folder not found at $frontend"
    exit 1
}

Push-Location $frontend
Write-Host "Installing frontend dependencies (npm install)..."
npm install

# Create frontend .env
$frontendEnv = "REACT_APP_API_URL=http://localhost:5000/api"
$frontendEnvPath = Join-Path $frontend ".env"
$frontendEnv | Out-File -FilePath $frontendEnvPath -Encoding UTF8
Write-Host "Created $frontendEnvPath"

Write-Host "Starting frontend (opens a new PowerShell window)..."
$startFrontendScript = @"
cd `"$frontend`"
npm start
"@
$startFrontendPath = Join-Path $root "start-frontend.ps1"
$startFrontendScript | Out-File -FilePath $startFrontendPath -Encoding UTF8
Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-File",$startFrontendPath

Pop-Location

Write-Host "`nSetup complete. Backend should be at http://localhost:5000 and frontend at http://localhost:3000"
Write-Host "If servers did not start, open the created start-backend.ps1 and start-frontend.ps1 files manually to inspect logs."
