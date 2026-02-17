# VibeLink Engine - Installation Script for Windows
# Usage: .\install.ps1 -ProjectPath "C:\Path\To\YourUnityProject"

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectPath
)

Write-Host "🚀 Installing VibeLink Engine..." -ForegroundColor Cyan

# Validate project path
if (-not (Test-Path $ProjectPath)) {
    Write-Host "❌ Error: Project path does not exist: $ProjectPath" -ForegroundColor Red
    exit 1
}

# Check if Assets folder exists
$assetsPath = Join-Path $ProjectPath "Assets"
if (-not (Test-Path $assetsPath)) {
    Write-Host "❌ Error: Not a valid Unity project (Assets folder not found)" -ForegroundColor Red
    exit 1
}

# Navigate to project
Set-Location $ProjectPath

# Initialize Git if needed
if (-not (Test-Path ".git")) {
    Write-Host "📦 Initializing Git repository..." -ForegroundColor Yellow
    git init
}

# Add VibeLink as submodule
Write-Host "📥 Downloading VibeLink Engine from GitHub..." -ForegroundColor Yellow
git submodule add https://github.com/Kiuytree/VibeLink.git Engine 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Submodule already exists or error occurred. Updating..." -ForegroundColor Yellow
    git submodule update --init --recursive
}

# Create necessary directories
$toolsPath = Join-Path $assetsPath "_Project\Tools"
if (-not (Test-Path $toolsPath)) {
    Write-Host "📁 Creating Tools directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $toolsPath -Force | Out-Null
}

$externalPath = Join-Path $ProjectPath "External\Blender"
if (-not (Test-Path $externalPath)) {
    Write-Host "📁 Creating External/Blender directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $externalPath -Force | Out-Null
}

# Create Unity junction (symlink alternative, no admin required)
$unityLinkPath = Join-Path $toolsPath "VibeLink"
if (Test-Path $unityLinkPath) {
    Write-Host "🔗 Removing existing Unity link..." -ForegroundColor Yellow
    Remove-Item $unityLinkPath -Force -Recurse
}

Write-Host "🔗 Creating Unity junction..." -ForegroundColor Yellow
$unityTarget = Join-Path $ProjectPath "Engine\Unity"
New-Item -ItemType Junction -Path $unityLinkPath -Target $unityTarget | Out-Null

# Create Blender junction
$blenderLinkPath = Join-Path $externalPath "VibeLink"
if (Test-Path $blenderLinkPath) {
    Write-Host "🔗 Removing existing Blender link..." -ForegroundColor Yellow
    Remove-Item $blenderLinkPath -Force -Recurse
}

Write-Host "🔗 Creating Blender junction..." -ForegroundColor Yellow
$blenderTarget = Join-Path $ProjectPath "Engine\Blender\VibeLink"
New-Item -ItemType Junction -Path $blenderLinkPath -Target $blenderTarget | Out-Null

# Verify installation
Write-Host ""
Write-Host "✅ VibeLink Engine installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Open Unity Editor"
Write-Host "  2. Wait for scripts to compile"
Write-Host "  3. Go to Tools → VibeLink Control Panel"
Write-Host "  4. Click 'Add Server to Scene'"
Write-Host ""
Write-Host "📖 For Blender setup, see: Engine/Documentation/Installation.md" -ForegroundColor Cyan
Write-Host ""
