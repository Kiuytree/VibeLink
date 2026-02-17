# Installation Guide

## Prerequisites

- **Unity 6.0+** with URP 17.3+
- **Blender 5.0+**
- **Git** (for submodule installation)

---

## Unity Installation

### Method 1: Git Submodule (Recommended)

1. **Navigate to your Unity project root**:
   ```bash
   cd C:/Path/To/YourUnityProject
   ```

2. **Add VibeLink as a submodule**:
   ```bash
   git submodule add https://github.com/Kiuytree/VibeLink.git Engine
   git submodule update --init --recursive
   ```

3. **Create symbolic link** (Windows PowerShell as Administrator):
   ```powershell
   cd Assets/_Project/Tools
   New-Item -ItemType SymbolicLink -Name "VibeLink" -Target "..\..\..\Engine\Unity"
   ```

   **Linux/Mac**:
   ```bash
   cd Assets/_Project/Tools
   ln -s ../../../Engine/Unity VibeLink
   ```

4. **Verify in Unity**:
   - Open Unity Editor
   - Check that `Assets/_Project/Tools/VibeLink/` appears
   - No compilation errors should occur

### Method 2: Manual Copy (Not Recommended)

If you can't use submodules:

1. Download the repository as ZIP
2. Extract to a temporary location
3. Copy `Unity/` folder contents to `Assets/_Project/Tools/VibeLink/`
4. Copy `Blender/` folder to `External/Blender/` (or anywhere outside Assets)

---

## Blender Installation

1. **Open Blender** (5.0 or later)

2. **Install the Addon**:
   - Edit → Preferences → Add-ons
   - Click "Install..." button
   - Navigate to `Engine/Blender/VibeLink/__init__.py`
   - Click "Install Add-on"

3. **Enable the Addon**:
   - Search for "VibeLink" in the add-ons list
   - Check the checkbox to enable it
   - The addon should show: "Development: VibeLink (Unity Bridge)"

4. **Verify Installation**:
   - Press `N` to open the side panel
   - You should see a "VibeLink" tab
   - Click "Start Server" button
   - Console should show: `[VibeLink] Connecting to Unity...`

---

## First Connection Test

### In Unity:
1. Tools → VibeLink Control Panel
2. If server is not running, click "Add Server to Scene"
3. Status should show: "Running on Port: 8085"

### In Blender:
1. Open N-Panel → VibeLink
2. Click "Start Server"
3. Status should change to "Connected ✅"

### Generate Test Asset:
1. In Unity Control Panel, click "Generate House Level 1"
2. Blender console should show: `[VibeLink] Generating House...`
3. After ~2 seconds, a house should appear in Unity scene at (0,0,0)

---

## Troubleshooting

### "Server not found in scene"
- Click "Add Server to Scene" in the Control Panel
- Make sure `VibeLinkServer` GameObject exists in the Hierarchy

### "Connection refused" in Blender
- Ensure Unity is running and the server started
- Check Windows Firewall (allow port 8085)
- Verify no other application is using port 8085

### "Scripts not compiling" in Unity
- Check Unity version (must be 6.0+)
- Verify URP is installed (`com.unity.render-pipelines.universal`)
- Check Console for specific errors

### "Addon not appearing" in Blender
- Make sure you selected `__init__.py` (not the folder)
- Check Blender version (must be 5.0+)
- Look in Blender Console (Window → Toggle System Console) for errors

---

## Updating the Engine

If you installed via submodule:

```bash
cd Engine
git pull origin main
cd ..
git add Engine
git commit -m "Update VibeLink Engine"
```

Unity will auto-recompile the scripts.

In Blender, you may need to:
1. Disable the addon
2. Restart Blender
3. Re-enable the addon

---

## Uninstallation

### Unity:
```bash
# If using submodule
git submodule deinit -f Engine
git rm -f Engine
rm -rf .git/modules/Engine

# Remove symlink
Remove-Item Assets/_Project/Tools/VibeLink
```

### Blender:
1. Edit → Preferences → Add-ons
2. Find "VibeLink"
3. Click "Remove" button

---

## Next Steps

- Read the [API Reference](API.md) to understand the JSON protocol
- Check [Generators Guide](Generators_Guide.md) to create custom generators
- Join the community (link TBD)
