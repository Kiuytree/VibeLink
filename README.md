# VibeLink Engine
**Procedural Asset Pipeline: Blender ↔ Unity**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Unity](https://img.shields.io/badge/Unity-6.0%2B-green)
![Blender](https://img.shields.io/badge/Blender-5.0%2B-orange)

## 🎯 Overview

VibeLink is a bidirectional communication system between Unity and Blender that enables **real-time procedural asset generation**. Send a JSON command from Unity, and Blender generates a custom 3D model (house, tree, rock) that auto-imports into your scene.

## ✨ Features

- **WebSocket Server** (Unity): RFC 6455 compliant, runs in Edit & Play Mode
- **Blender Addon**: Python-based generators with native mesh construction
- **Auto-Import System**: FBX files are detected, configured, and spawned automatically
- **Auto-Paint**: Materials are assigned URP colors based on naming conventions
- **Evolutionary House Generator**: 5 architectural levels (Cabin → Mansion)
- **Nature Generator**: Procedural trees and rocks with organic distortion

## 📦 What's Included

### Unity Scripts
- `VibeLinkServer.cs`: WebSocket server (port 8085)
- `VibeLinkEditor.cs`: Control panel with generation buttons
- `VibeAssetImporter.cs`: Auto-configuration for imported FBX
- `HierarchyDumper.cs`: Scene state serializer (JSON)

### Blender Addon
- `__init__.py`: Addon registration and UI panel
- `server.py`: WebSocket client with threading
- `house_generator.py`: Beam & Post architecture (L1-L5)
- `nature_generator.py`: Trees and rocks with BMesh distortion

## 🚀 Quick Start

### 1. Install in Unity
```bash
cd YourUnityProject
git submodule add https://github.com/Kiuytree/VibeLink.git Engine
```

Create symbolic link (PowerShell as Admin):
```powershell
cd Assets/_Project/Tools
New-Item -ItemType SymbolicLink -Name "VibeLink" -Target "..\..\..\Engine\Unity"
```

### 2. Install in Blender
1. Edit → Preferences → Add-ons → Install
2. Navigate to `Engine/Blender/VibeLink/__init__.py`
3. Enable "VibeLink (Unity Bridge)"
4. Open N-Panel → VibeLink → Start Server

### 3. Generate Your First Asset
1. In Unity: Tools → VibeLink Control Panel
2. Click "🧬 Generate Evolution (L1 → L5)"
3. Watch as 5 houses appear in your scene!

## 📖 Documentation

- [Installation Guide](Documentation/Installation.md)
- [API Reference](Documentation/API.md)
- [Creating Custom Generators](Documentation/Generators_Guide.md)

## 🛠️ Requirements

- **Unity**: 6.0+ (URP 17.3+)
- **Blender**: 5.0+ (tested on 5.0.1)
- **OS**: Windows 10/11 (Linux/Mac untested but should work)

## 📋 Roadmap

- [ ] Character Generator (modular humanoids)
- [ ] Props Generator (furniture, tools)
- [ ] Batch generation commands
- [ ] Unity Package Manager support
- [ ] Linux/Mac testing

## 🤝 Contributing

Contributions are welcome! Please read the contributing guidelines first.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with ❤️ for procedural generation enthusiasts.

---

**Made by Kiuytree** | [GitHub](https://github.com/Kiuytree)
