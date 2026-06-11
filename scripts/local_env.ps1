$ProjectRoot = Split-Path -Parent $PSScriptRoot
$env:PIP_CACHE_DIR = Join-Path $ProjectRoot ".cache\pip"
$env:PYTHONPYCACHEPREFIX = Join-Path $ProjectRoot ".cache\pycache"
$env:ULTRALYTICS_CONFIG_DIR = Join-Path $ProjectRoot ".cache\ultralytics"
$env:YOLO_CONFIG_DIR = Join-Path $ProjectRoot ".cache\ultralytics"
$env:TORCH_HOME = Join-Path $ProjectRoot ".cache\torch"
$env:XDG_CACHE_HOME = Join-Path $ProjectRoot ".cache"
$env:MPLCONFIGDIR = Join-Path $ProjectRoot ".cache\matplotlib"
# Milestone 2B: keep InsightFace model cache inside project folder, not C:\Users\
$env:INSIGHTFACE_HOME = Join-Path $ProjectRoot ".cache\insightface"
$env:UVICORN_APP = "api.main:app"
New-Item -ItemType Directory -Force -Path `
  $env:PIP_CACHE_DIR, `
  $env:PYTHONPYCACHEPREFIX, `
  $env:ULTRALYTICS_CONFIG_DIR, `
  $env:TORCH_HOME, `
  $env:XDG_CACHE_HOME, `
  $env:MPLCONFIGDIR, `
  $env:INSIGHTFACE_HOME, `
  (Join-Path $ProjectRoot "models"), `
  (Join-Path $ProjectRoot "runs"), `
  (Join-Path $ProjectRoot "runs\benchmarks"), `
  (Join-Path $ProjectRoot "runs\videos"), `
  (Join-Path $ProjectRoot "runs\tracking"), `
  (Join-Path $ProjectRoot "data"), `
  (Join-Path $ProjectRoot "snapshots"), `
  (Join-Path $ProjectRoot "snapshots\evidence"), `
  (Join-Path $ProjectRoot "sample_videos") | Out-Null
Write-Host "Project-local environment active:"
Write-Host "  PIP_CACHE_DIR=$env:PIP_CACHE_DIR"
Write-Host "  PYTHONPYCACHEPREFIX=$env:PYTHONPYCACHEPREFIX"
Write-Host "  ULTRALYTICS_CONFIG_DIR=$env:ULTRALYTICS_CONFIG_DIR"
Write-Host "  TORCH_HOME=$env:TORCH_HOME"
Write-Host "  INSIGHTFACE_HOME=$env:INSIGHTFACE_HOME"
