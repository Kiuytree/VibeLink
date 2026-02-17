# Changelog

All notable changes to VibeLink Engine will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-17

### Added
- **WebSocket Server (Unity)**: RFC 6455 compliant server running on port 8085
  - Supports Edit Mode and Play Mode
  - Thread-safe command queue
  - Broadcast capability for relay commands
- **Blender Addon**: Python-based client with UI panel
  - Auto-reconnect on connection loss
  - Thread-safe execution queue
  - Persistent export path memory
- **House Generator v2.1**: Evolutionary architecture system
  - Level 1: Cabin with beam & post structure
  - Level 2: Two-story house
  - Level 3: Balcony addition
  - Level 4: Side wing extension
  - Level 5: Tower element
  - Explicit BMesh roof construction (gable style)
  - Recessed walls with pillar detail
- **Nature Generator v1.0**: Organic asset creation
  - Trees: Distorted cylinder trunk + icosphere foliage
  - Rocks: Non-uniform scaled icospheres with vertex displacement
- **Auto-Import System (Unity)**:
  - Automatic FBX detection in `Generated/Models/`
  - Material-based color assignment (URP)
  - Scale correction (Blender → Unity)
  - Smart positioning for evolution tests
- **Control Panel (Unity Editor)**:
  - Scene setup automation (Plane, Light, Camera, NavMesh)
  - Hierarchy dump to JSON
  - Server control (start/restart)
  - Generation buttons (House L1, L2, Evolution, Nature Set)

### Fixed
- FBX scale issues (100x factor → 1x with proper axis conversion)
- Roof normal orientation (switched from vertex collapse to explicit mesh)
- Foliage appearing white (added Grass/Leaves material detection)
- Export path persistence across Blender sessions

### Technical Details
- Unity: Tested on 6.3.8 with URP 17.3
- Blender: Tested on 5.0.1
- Protocol: JSON over WebSocket (text frames)
- Export Format: FBX with `FBX_SCALE_ALL` option

---

## [Unreleased]

### Planned
- Character generator (modular humanoids)
- Props generator (furniture, tools, decorations)
- Batch generation commands
- Unity Package Manager support
- Linux/Mac compatibility testing
- API documentation expansion

---

[1.0.0]: https://github.com/Kiuytree/VibeLink/releases/tag/v1.0.0
