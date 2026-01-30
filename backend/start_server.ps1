# Start the backend lightweight HTTP server in a detached process using the venv python
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$python = Join-Path $scriptDir '.\.venv\Scripts\python.exe'
$serverScript = Join-Path $scriptDir 'main_http.py'

if (-not (Test-Path $python)) {
    Write-Error "Python executable not found at $python. Activate your venv or run \"python -m venv .venv\" first."
    exit 1
}

Start-Process -FilePath $python -ArgumentList $serverScript -WorkingDirectory $scriptDir -WindowStyle Normal
Write-Output "Started backend via: $python $serverScript (detached window)"
