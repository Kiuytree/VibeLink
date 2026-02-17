# Contributing to VibeLink Engine

Thank you for your interest in improving VibeLink! This guide is designed for both **human developers** and **AI agents** who want to contribute code, fix bugs, or add new features.

---

## 🤖 For AI Agents

If you're an AI agent tasked with modifying the VibeLink Engine, follow this workflow:

### 1. Locate the Engine Repository

The Engine is always in the `Engine/` folder of the Unity project:
```bash
cd YourUnityProject/Engine
```

### 2. Make Your Changes

Edit files in:
- `Unity/` - C# scripts for Unity
- `Blender/` - Python scripts for Blender
- `Documentation/` - Markdown documentation

**Example: Adding a new generator**
```bash
# Create new generator
touch Blender/VibeLink/generators/prop_generator.py

# Register in server.py
# (Edit Blender/VibeLink/server.py to import and handle "generate_prop")

# Update documentation
# (Edit Documentation/Generators_Guide.md)
```

### 3. Test Your Changes

**Unity:**
- The changes are immediately visible (symlink/junction)
- Unity will auto-recompile C# scripts
- Test in Unity Editor

**Blender:**
- Reload scripts: F3 → "Reload Scripts"
- Or restart Blender and re-enable the addon

### 4. Commit and Push

```bash
cd Engine
git add .
git commit -m "feat: Add prop generator for furniture and tools"
git push origin main
```

### 5. Update the Parent Project (Optional)

If you want the parent project (e.g., Sentis) to track the new Engine version:
```bash
cd ..  # Back to project root
git add Engine
git commit -m "chore: Update VibeLink Engine to latest version"
```

---

## 👨‍💻 For Human Developers

### Setting Up Development Environment

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YourUsername/VibeLink.git
   cd VibeLink
   ```
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/my-new-feature
   ```

### Making Changes

- **Unity Scripts**: Edit files in `Unity/`
- **Blender Scripts**: Edit files in `Blender/`
- **Documentation**: Update `README.md`, `CHANGELOG.md`, or files in `Documentation/`

### Testing

#### Unity Testing
1. Create a test Unity project
2. Run the install script:
   ```powershell
   .\install.ps1 -ProjectPath "C:\TestProject"
   ```
3. Verify your changes work in Unity Editor

#### Blender Testing
1. Install the addon from your local `Blender/VibeLink/` folder
2. Test generation commands
3. Check console for errors

### Submitting Changes

1. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: Add new feature X"
   ```

2. **Push to your fork**:
   ```bash
   git push origin feature/my-new-feature
   ```

3. **Create a Pull Request** on GitHub

---

## 📋 Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

**Examples:**
```
feat: Add character generator with modular body parts
fix: Correct roof normal orientation in house generator
docs: Update Installation.md with Junction instructions
refactor: Extract export logic into reusable function
```

---

## 🔄 Updating the Engine in Projects

### For AI Agents

When a user asks you to update the Engine in their project:

```bash
cd YourUnityProject/Engine
git pull origin main
cd ..
git add Engine
git commit -m "chore: Update VibeLink Engine"
```

Unity will auto-recompile. Blender may need a restart.

### For Humans

Same process, or use the GUI:
1. Open terminal in `Engine/` folder
2. Run `git pull origin main`
3. Unity will detect changes and recompile

---

## 🐛 Reporting Bugs

If you find a bug:

1. **Check existing issues** on GitHub
2. **Create a new issue** with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Unity/Blender versions
   - Error messages (if any)

---

## 🎯 Feature Requests

Have an idea for a new generator or feature?

1. **Open a discussion** on GitHub
2. Describe the use case
3. Propose an implementation approach

---

## 📝 Code Style

### C# (Unity)
- Follow [Microsoft C# Coding Conventions](https://docs.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)
- Use `PascalCase` for public members
- Use `camelCase` for private members
- Add XML comments for public APIs

### Python (Blender)
- Follow [PEP 8](https://pep8.org/)
- Use `snake_case` for functions and variables
- Add docstrings for all functions
- Keep functions focused and small

---

## 🚀 Release Process

### For Maintainers

1. Update `CHANGELOG.md` with new version
2. Commit changes:
   ```bash
   git commit -m "chore: Release v1.1.0"
   ```
3. Create and push tag:
   ```bash
   git tag -a v1.1.0 -m "Release v1.1.0: Description"
   git push origin v1.1.0
   ```
4. Create GitHub Release with release notes

---

## 🙏 Thank You!

Every contribution helps make VibeLink better for the community. Whether you're fixing a typo or adding a major feature, your work is appreciated!

---

**Questions?** Open an issue or discussion on GitHub.
