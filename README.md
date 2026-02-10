# Kerf Generator

Python library for generating kerf cutting patterns (living hinges) for laser cutting.

## Overview

Kerf cutting creates flexible joints in rigid materials by making strategic parallel cuts. This library generates these patterns and exports them as DXF files (for Fusion 360, Lightburn) and preview images.

## Features

- **Living Hinge Pattern Generation**: Create parallel cut patterns for bendable joints
- **DXF Export**: Compatible with Fusion 360 and Lightburn
- **Image Previews**: Visual verification of patterns before cutting
- **Parametric Control**: Adjust spacing, cut length, material dimensions, and more

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd kerf-burning

# Install dependencies with uv
uv sync
```

## Quick Start

```python
from kerf_generator import generate_living_hinge, KerfParameters

# Define your pattern parameters
params = KerfParameters(
    material_width=100,        # mm
    material_height=200,       # mm
    material_thickness=3,      # mm
    kerf_width=0.2,           # mm
    cut_spacing=5,            # mm
    cut_length=80,            # mm
    cut_offset=10,            # mm
    pattern_direction='horizontal'
)

# Generate and export
generate_living_hinge(
    params,
    dxf_output="pattern.dxf",
    image_output="pattern.png"
)
```

## Project Status

🚧 **In Development** - Core infrastructure complete, implementing mathematical model and pattern generation.

See [ONGOING_TASKS.md](./ONGOING_TASKS.md) for detailed implementation progress.

## Documentation

- [Implementation Plan](./ONGOING_TASKS.md) - Detailed roadmap and tasks
- [Project Context](./CLAUDE.md) - Technical decisions and conventions

## Development

```bash
# Activate virtual environment (if needed)
source .venv/bin/activate

# Run tests
uv run pytest

# Format code
uv run black src/

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/
```

## License

TBD

## Author

Christopher Brown
