# Kerf Generator Project Context

## Project Purpose
Python library for generating kerf cutting patterns (living hinges) for laser cutting. Outputs DXF files for Fusion 360/Lightburn and preview images for verification.

## Important Working Conventions

### ⚠️ NEVER Give Time Estimates
**DO NOT provide time estimates for implementation tasks** (e.g., "this will take 2-3 hours" or "30-45 minutes").

**Reasons:**
- AI time perception is meaningless
- Over-estimates AI capability, under-estimates human effort
- Provides no useful information to the user
- Creates false expectations

**Instead:** Just describe what needs to be done and start doing it, or ask if the user wants to proceed.

### 🤖 Use Sonnet Model at Startup
**ALWAYS use the Sonnet model (claude-sonnet-4-5) when starting a Claude Code session for this project.**

**Reasons:**
- Best balance of speed and capability for development tasks
- More cost-effective than Opus for routine coding work
- Fast enough for interactive development workflow
- Can always escalate to Opus for particularly complex tasks if needed

### 👥 Names and Address
**In this project:**
- Address the user as **Sparky**
- Refer to yourself as **Pancho**

## Key Project Details

### Technology Stack
- **Language**: Python 3.14
- **Package Manager**: uv
- **Virtual Environment**: `.venv/` (managed by uv)
- **Key Libraries**:
  - `ezdxf` - DXF file generation
  - `matplotlib` - Image previews
  - `numpy` - Calculations

### Project Structure
```
src/kerf_generator/    # Main package
  ├── __init__.py      # High-level API
  ├── patterns.py      # Pattern generation logic
  ├── geometry.py      # Mathematical calculations
  ├── exporters.py     # DXF and image export
  └── parameters.py    # Parameter validation
docs/                  # Documentation
examples/              # Example scripts
tests/                 # Unit tests
```

### Core Concepts
- **Kerf Cutting**: Making parallel cuts in rigid material to allow bending
- **Living Hinge**: Pattern of parallel cuts creating flexible joint
- **Kerf Width**: Material removed by laser cut (~0.2mm typical)
- **Target Use**: Laser cutting wood, acrylic, cardboard for bendable structures

### Design Decisions
1. **Pattern Type**: Living hinge (parallel cuts) only - simplest and most common
2. **Geometry**: Flat rectangles only - no imported shape support initially
3. **Output**: DXF (primary for precision) + PNG/SVG (preview)
4. **Units**: Millimeters throughout
5. **Parameters**: See `KerfParameters` in ONGOING_TASKS.md

### Important Constraints
- Lightburn prefers vector formats (DXF, SVG) over images
- DXF should use layers: outline (blue) and cuts (red)
- Must validate parameters to prevent material failure
- Bend radius depends on: spacing, material thickness, kerf width

## Development Workflow

### Working with Virtual Environment
```bash
# Activate venv (when needed)
source .venv/bin/activate

# Install dependencies
uv add <package-name>

# Install dev dependencies
uv add --dev <package-name>

# Run package
uv run python -m kerf_generator
```

### Git Workflow
- Repository initialized at project root
- Will be pushed to GitHub (not yet done)
- Use conventional commits when possible

### Testing
- Use `pytest` for testing
- Run tests with: `uv run pytest`
- Test files in `tests/` directory

## Implementation Status
See **[ONGOING_TASKS.md](./ONGOING_TASKS.md)** for detailed implementation plan and current progress.

### Current Phase
**Phase 1: Core Infrastructure** - Setting up project structure

### Completed
- [x] Project structure created with uv
- [x] Virtual environment initialized (.venv)
- [x] Git repository initialized
- [x] Documentation files created (CLAUDE.md, ONGOING_TASKS.md)
- [x] Module stub files created

### Next Steps
1. Add dependencies to pyproject.toml (ezdxf, matplotlib, numpy)
2. Implement geometry calculations
3. Create KerfParameters dataclass
4. Build pattern generator

## Reference Materials

### Kerf Bending Formula (Approximate)
```
bend_radius ≈ (material_thickness * cut_spacing) / (2 * kerf_width)
```
*(This is a simplified formula; actual implementation may need more sophisticated calculations)*

### File Format Notes
- **DXF**: Use AC1015 (AutoCAD 2000) for broad compatibility
- **Layer 0**: Outline/reference geometry (blue, 0.25mm weight)
- **Layer 1**: Cut lines (red, 0.13mm weight for laser cutting)

## Conventions

### Code Style
- Use `black` for formatting (to be configured)
- Type hints throughout
- Docstrings in numpy/Google style
- Imports: standard lib → third-party → local

### Naming
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private/internal: prefix with `_`

### File Paths
- Always use `pathlib.Path` for path manipulation
- Accept `str | Path` in APIs, convert internally
- Use forward slashes in examples (cross-platform)

## Questions & Decisions Log

### Answered
- **Q**: Multiple pattern types or just living hinge?
  **A**: Living hinge only (simplest, most common use case)

- **Q**: Work with imported geometry or just rectangles?
  **A**: Rectangles only initially (can expand later)

- **Q**: Key parameters to control?
  **A**: Spacing, length, dimensions, kerf width, bend angle/radius

### Pending
- CLI tool needed? (Probably yes, add after core library works)
- Calculator mode for reverse calculations? (Nice to have)
- Specific material presets? (Future enhancement)

## Useful Commands

```bash
# Project setup (already done)
uv init --name kerf-generator --lib
uv venv

# Development
uv add ezdxf matplotlib numpy
uv add --dev pytest black mypy ruff
uv run pytest
uv run black src/
uv run mypy src/

# Git operations
git status
git add .
git commit -m "message"
git push  # (after setting up GitHub remote)
```

## Notes
- This is a new project, started 2026-02-10
- Primary user is working on Linux (Arch) with Hyprland
- Target software: Fusion 360 (3D modeling) and Lightburn (laser cutting)
- Virtual environment managed by uv to avoid polluting system Python
