#!/bin/bash
# VibeLink Engine - Installation Script for Linux/Mac
# Usage: ./install.sh /path/to/YourUnityProject

set -e

PROJECT_PATH="$1"

echo "🚀 Installing VibeLink Engine..."

# Validate arguments
if [ -z "$PROJECT_PATH" ]; then
    echo "❌ Error: Project path required"
    echo "Usage: ./install.sh /path/to/YourUnityProject"
    exit 1
fi

# Validate project path
if [ ! -d "$PROJECT_PATH" ]; then
    echo "❌ Error: Project path does not exist: $PROJECT_PATH"
    exit 1
fi

# Check if Assets folder exists
if [ ! -d "$PROJECT_PATH/Assets" ]; then
    echo "❌ Error: Not a valid Unity project (Assets folder not found)"
    exit 1
fi

# Navigate to project
cd "$PROJECT_PATH"

# Initialize Git if needed
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
fi

# Add VibeLink as submodule
echo "📥 Downloading VibeLink Engine from GitHub..."
if ! git submodule add https://github.com/Kiuytree/VibeLink.git Engine 2>/dev/null; then
    echo "⚠️  Submodule already exists or error occurred. Updating..."
    git submodule update --init --recursive
fi

# Create necessary directories
TOOLS_PATH="$PROJECT_PATH/Assets/_Project/Tools"
if [ ! -d "$TOOLS_PATH" ]; then
    echo "📁 Creating Tools directory..."
    mkdir -p "$TOOLS_PATH"
fi

EXTERNAL_PATH="$PROJECT_PATH/External/Blender"
if [ ! -d "$EXTERNAL_PATH" ]; then
    echo "📁 Creating External/Blender directory..."
    mkdir -p "$EXTERNAL_PATH"
fi

# Create Unity symlink
UNITY_LINK="$TOOLS_PATH/VibeLink"
if [ -L "$UNITY_LINK" ] || [ -d "$UNITY_LINK" ]; then
    echo "🔗 Removing existing Unity link..."
    rm -rf "$UNITY_LINK"
fi

echo "🔗 Creating Unity symlink..."
ln -s "$PROJECT_PATH/Engine/Unity" "$UNITY_LINK"

# Create Blender symlink
BLENDER_LINK="$EXTERNAL_PATH/VibeLink"
if [ -L "$BLENDER_LINK" ] || [ -d "$BLENDER_LINK" ]; then
    echo "🔗 Removing existing Blender link..."
    rm -rf "$BLENDER_LINK"
fi

echo "🔗 Creating Blender symlink..."
ln -s "$PROJECT_PATH/Engine/Blender/VibeLink" "$BLENDER_LINK"

# Verify installation
echo ""
echo "✅ VibeLink Engine installed successfully!"
echo ""
echo "📋 Next steps:"
echo "  1. Open Unity Editor"
echo "  2. Wait for scripts to compile"
echo "  3. Go to Tools → VibeLink Control Panel"
echo "  4. Click 'Add Server to Scene'"
echo ""
echo "📖 For Blender setup, see: Engine/Documentation/Installation.md"
echo ""
