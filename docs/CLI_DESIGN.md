# CLI Tool Design

## Current Usage (No CLI Yet)

**Currently, the utility is used as a Python library only:**

### Method 1: Write Python Scripts

```python
# my_pattern.py
from kerf_generator import KerfParameters, generate_living_hinge

params = KerfParameters(
    material_width=100,
    material_height=200,
    material_thickness=3,
    kerf_width=0.2,
    cut_spacing=5,
    cut_length=80,
    cut_offset=10,
    pattern_direction='horizontal'
)

generate_living_hinge(params, "output.dxf", "output.png")
```

Run with: `uv run python my_pattern.py`

### Method 2: Interactive Python/IPython

```python
>>> from kerf_generator import *
>>> params = KerfParameters(100, 200, 3, 0.2, 5, 80, 10, 'horizontal')
>>> lines = generate_living_hinge(params, "test.dxf", "test.png")
>>> print(f"Generated {len(lines)} cuts")
```

### Method 3: Jupyter Notebook

```python
# In Jupyter
from kerf_generator import *

params = KerfParameters(...)
print_pattern_info(params)

lines = generate_living_hinge(params, "pattern.dxf", "pattern.png")

# View the preview image inline
from IPython.display import Image
Image("pattern.png")
```

---

## Proposed CLI Tool

A command-line interface would make the tool more accessible without writing Python code.

### Design Goals

1. **Simple for common cases** - single command for basic patterns
2. **Flexible for advanced use** - support all parameter combinations
3. **Interactive mode** - ask questions if parameters missing
4. **Preset support** - save/load common configurations
5. **Batch processing** - generate multiple patterns

---

## Proposed Commands

### `kerf generate`

Generate a pattern with specified parameters.

```bash
# Basic usage
kerf generate \
  --width 100 \
  --height 200 \
  --thickness 3 \
  --kerf 0.2 \
  --spacing 5 \
  --length 80 \
  --offset 10 \
  --direction horizontal \
  --output pattern.dxf

# Short form
kerf generate -w 100 -h 200 -t 3 -k 0.2 -s 5 -l 80 -O 10 -d h -o pattern

# With preview
kerf generate --width 100 --height 200 ... --dxf pattern.dxf --png pattern.png

# All outputs
kerf generate ... --output-dir ./output --name my_pattern
# Creates: my_pattern.dxf, my_pattern.png, my_pattern.svg
```

### `kerf calculate`

Calculate parameters based on desired bend radius.

```bash
# What spacing do I need for a 30mm bend radius?
kerf calculate spacing --radius 30 --thickness 3 --kerf 0.2

# Output: Required spacing: 4.00mm

# What radius will I get with these parameters?
kerf calculate radius --spacing 5 --thickness 3 --kerf 0.2

# Output: Bend radius: 37.50mm
```

### `kerf interactive`

Interactive wizard for generating patterns.

```bash
kerf interactive

# Prompts:
# Material width (mm): 100
# Material height (mm): 200
# Material thickness (mm): 3
# Laser kerf width (mm) [0.2]: <enter for default>
# Cut spacing (mm): 5
# Cut length (mm): 80
# Edge offset (mm) [10]: <enter>
# Pattern direction (horizontal/vertical) [horizontal]: <enter>
# Output filename [pattern.dxf]: my_pattern.dxf
# Generate preview image? (y/n) [y]: <enter>
#
# Generating pattern...
# ✓ Generated 37 cuts
# ✓ Saved to my_pattern.dxf
# ✓ Preview saved to my_pattern.png
```

### `kerf preset`

Manage presets for common materials.

```bash
# List presets
kerf preset list

# Output:
# Available presets:
#   plywood-3mm    - 3mm plywood, 0.2mm kerf
#   acrylic-3mm    - 3mm acrylic, 0.25mm kerf
#   mdf-6mm        - 6mm MDF, 0.3mm kerf

# Use preset
kerf generate --preset plywood-3mm --width 100 --height 200 ...

# Create custom preset
kerf preset add my-material --thickness 3 --kerf 0.22 --min-spacing 6

# Show preset details
kerf preset show plywood-3mm
```

### `kerf info`

Display information about a pattern or parameters.

```bash
# Show calculated properties
kerf info --spacing 5 --thickness 3 --kerf 0.2

# Output:
# Bend radius: 37.5mm
# Minimum safe spacing: 9.0mm
# Warning: Spacing below recommended minimum

# Validate DXF file
kerf info pattern.dxf
```

### `kerf batch`

Generate multiple patterns from config file.

```bash
# batch_config.json:
# [
#   {
#     "name": "box_lid",
#     "width": 150,
#     "height": 50,
#     "thickness": 3,
#     "kerf": 0.2,
#     "spacing": 5.5,
#     ...
#   },
#   {
#     "name": "side_panel",
#     ...
#   }
# ]

kerf batch batch_config.json --output-dir ./batch_output
```

---

## Implementation Approach

### Option 1: Click (Recommended)

Use the `click` library for CLI - it's clean and Pythonic.

```python
# cli.py
import click
from kerf_generator import KerfParameters, generate_living_hinge

@click.group()
def cli():
    """Kerf Generator - Create living hinge patterns for laser cutting."""
    pass

@cli.command()
@click.option('--width', '-w', type=float, required=True, help='Material width (mm)')
@click.option('--height', '-h', type=float, required=True, help='Material height (mm)')
@click.option('--thickness', '-t', type=float, required=True, help='Material thickness (mm)')
# ... more options
@click.option('--dxf', type=click.Path(), help='Output DXF file')
@click.option('--png', type=click.Path(), help='Output PNG file')
def generate(width, height, thickness, ...):
    """Generate a living hinge pattern."""
    params = KerfParameters(
        material_width=width,
        material_height=height,
        ...
    )
    lines = generate_living_hinge(params, dxf, png)
    click.echo(f"✓ Generated {len(lines)} cuts")

if __name__ == '__main__':
    cli()
```

### Option 2: Typer

Modern alternative to Click, with better type hints.

```python
import typer
from kerf_generator import KerfParameters, generate_living_hinge

app = typer.Typer()

@app.command()
def generate(
    width: float = typer.Option(..., help="Material width (mm)"),
    height: float = typer.Option(..., help="Material height (mm)"),
    ...
):
    """Generate a living hinge pattern."""
    params = KerfParameters(...)
    lines = generate_living_hinge(params)
    typer.echo(f"✓ Generated {len(lines)} cuts")
```

### Option 3: argparse (Stdlib)

No dependencies, but more verbose.

---

## Configuration Files

Support YAML/JSON config files for complex patterns:

```yaml
# pattern.yaml
material:
  name: "3mm Birch Plywood"
  width: 150
  height: 200
  thickness: 3
  kerf: 0.2

pattern:
  type: living_hinge
  direction: horizontal
  spacing: 5.5
  length: 130
  offset: 10

output:
  directory: "./output"
  basename: "box_hinge"
  formats:
    - dxf
    - png
    - svg
```

Use with:
```bash
kerf generate --config pattern.yaml
```

---

## Installation as CLI Tool

Add to `pyproject.toml`:

```toml
[project.scripts]
kerf = "kerf_generator.cli:main"
```

Then install:
```bash
uv pip install -e .
```

Now `kerf` command is available globally!

---

## Priority Implementation Order

1. ✅ **Core library** (DONE)
2. **Basic generate command** - most important
3. **Calculate command** - very useful
4. **Interactive mode** - good for beginners
5. **Preset system** - nice to have
6. **Batch processing** - advanced feature

---

## Current Workaround

Until CLI is implemented, create helper scripts:

```bash
# generate_pattern.sh
#!/bin/bash
python3 << EOF
from kerf_generator import KerfParameters, generate_living_hinge

params = KerfParameters(
    material_width=$1,
    material_height=$2,
    material_thickness=$3,
    kerf_width=$4,
    cut_spacing=$5,
    cut_length=$6,
    cut_offset=$7,
    pattern_direction='$8'
)

generate_living_hinge(params, "$9.dxf", "$9.png")
print(f"✓ Generated pattern: $9")
EOF
```

Usage:
```bash
./generate_pattern.sh 100 200 3 0.2 5 80 10 horizontal my_pattern
```

---

## Feedback Welcome!

Which CLI features would be most useful for your workflow?
- Basic generate command?
- Interactive wizard?
- Preset system?
- Something else?
