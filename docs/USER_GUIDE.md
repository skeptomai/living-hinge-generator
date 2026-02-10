# Kerf Generator User Guide

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Basic Usage](#basic-usage)
- [Understanding Parameters](#understanding-parameters)
- [Export Formats](#export-formats)
- [Pattern Types](#pattern-types)
- [Advanced Usage](#advanced-usage)
- [Tips & Best Practices](#tips--best-practices)

## Introduction

Kerf Generator creates living hinge patterns for laser cutting. A living hinge is a series of parallel cuts that allows rigid materials (wood, acrylic, cardboard) to bend flexibly.

### What is Kerf Cutting?

**Kerf** is the width of material removed by a cutting tool. In laser cutting, the kerf is typically 0.1-0.3mm depending on:
- Laser power
- Material type
- Material thickness

By making strategic parallel cuts, you create flexible joints in otherwise rigid materials.

## Installation

### Prerequisites
- Python 3.14+ (or compatible version)
- uv package manager

### Install from source

```bash
# Clone the repository
git clone <repository-url>
cd kerf-burning

# Install dependencies
uv sync
```

## Quick Start

Here's the simplest way to generate a pattern:

```python
from kerf_generator import KerfParameters, generate_living_hinge

# Define your pattern
params = KerfParameters(
    material_width=100,         # mm
    material_height=200,        # mm
    material_thickness=3,       # mm
    kerf_width=0.2,            # mm
    cut_spacing=5,             # mm
    cut_length=80,             # mm
    cut_offset=10,             # mm
    pattern_direction='horizontal'
)

# Generate and export
lines = generate_living_hinge(
    params,
    dxf_output="pattern.dxf",      # For laser cutting
    image_output="pattern.png"      # For preview
)

print(f"Generated {len(lines)} cuts!")
```

Run this script:
```bash
uv run python your_script.py
```

## Basic Usage

### As a Python Library

The primary way to use Kerf Generator is by importing it in your Python scripts:

```python
from kerf_generator import (
    KerfParameters,
    generate_living_hinge,
    export_dxf,
    export_image,
    print_pattern_info,
)
```

### Creating Parameters

```python
# Minimum required parameters
params = KerfParameters(
    material_width=100,           # Width of material sheet
    material_height=200,          # Height of material sheet
    material_thickness=3,         # Thickness of material
    kerf_width=0.2,              # Laser kerf width
    cut_spacing=5,               # Distance between cuts
    cut_length=80,               # Length of each cut
    cut_offset=10,               # Margin from edges
    pattern_direction='horizontal'  # or 'vertical'
)

# Optional: Add metadata
params.material_name = "3mm Birch Plywood"
params.notes = "Test pattern for box hinge"
```

### Generating Patterns

```python
# Option 1: Generate with automatic export
lines = generate_living_hinge(
    params,
    dxf_output="output/my_pattern.dxf",
    image_output="output/my_pattern.png"
)

# Option 2: Generate first, export later
lines = generate_living_hinge(params)
export_dxf(lines, params, "pattern.dxf")
export_image(lines, params, "pattern.png")

# Option 3: Export all formats
from kerf_generator import export_all
files = export_all(lines, params, "output", "my_pattern")
# Creates: my_pattern.dxf, my_pattern.png, my_pattern.svg
```

## Understanding Parameters

### Material Dimensions

```python
material_width=100      # X dimension (mm)
material_height=200     # Y dimension (mm)
material_thickness=3    # Z dimension (mm)
```

**Note:** Orientation matters! For horizontal cuts, the width determines cut length constraints, and height determines how many cuts fit.

### Kerf Width

The kerf width depends on your laser and material:

| Material | Typical Kerf (CO2 Laser) |
|----------|-------------------------|
| 3mm Plywood | 0.2-0.25mm |
| 3mm Acrylic | 0.15-0.2mm |
| Cardboard | 0.3-0.4mm |
| 6mm MDF | 0.25-0.3mm |

**Pro Tip:** Cut a test square and measure the difference between the design size and actual size to determine your kerf.

### Cut Spacing

Closer spacing = tighter bend radius, but:
- **Too close:** Material may break or collapse during cutting
- **Too far:** Pattern won't bend well

**Safe range:** 1.5x to 3x material thickness

```python
# For 3mm material:
cut_spacing=5     # Tight bend (~37mm radius)
cut_spacing=10    # Gentle bend (~75mm radius)
```

### Cut Length

Length of individual cuts. Longer cuts = more flexibility, but:
- Must be less than material dimension
- Should leave material at offset boundaries

```python
# For 100mm wide material with 10mm offset:
cut_length=80     # Uses 80mm of the 80mm available
cut_length=70     # More conservative, leaves more margin
```

### Cut Offset

Distance from material edges where cuts should not be placed.

```python
cut_offset=10     # 10mm margin on all sides
```

**Purpose:**
- Prevents cuts from reaching edges (structural integrity)
- Leaves space for mounting holes or fasteners
- Provides gripping area for handling

### Pattern Direction

```python
pattern_direction='horizontal'  # Cuts run left-right, bend up-down
pattern_direction='vertical'    # Cuts run up-down, bend left-right
```

**Horizontal cuts:** Bend the material along the Y-axis (like a book cover)
**Vertical cuts:** Bend the material along the X-axis (like rolling paper)

## Export Formats

### DXF (Recommended for Cutting)

DXF is the preferred format for laser cutting software.

```python
export_dxf(lines, params, "pattern.dxf")
```

**Features:**
- Layer 0 (blue): Material outline - reference only, do not cut
- Layer 1 (red): Cut lines - set these to "cut" mode in your laser software

**Compatible with:**
- Lightburn
- Fusion 360
- AutoCAD
- LaserWeb
- Most laser cutting software

### PNG/Image (Preview & Verification)

```python
export_image(lines, params, "pattern.png",
             format="png",
             dpi=300,
             show_grid=True)
```

**Options:**
- `format`: "png", "svg", or "pdf"
- `dpi`: Resolution for raster formats (300 recommended)
- `show_grid`: Display reference grid
- `show_annotations`: Show parameter info box

**Use cases:**
- Verify pattern before cutting
- Documentation
- Sharing designs

### SVG (Vector Preview)

```python
export_svg(lines, params, "pattern.svg")
```

SVG files are:
- Vector format (scalable)
- Can be imported into some laser software
- Smaller file size than PNG
- Good for web display

## Pattern Types

### Horizontal Living Hinge

```python
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
```

**Best for:**
- Book covers
- Box lids
- Cylindrical wrapping (horizontal axis)

### Vertical Living Hinge

```python
params = KerfParameters(
    material_width=200,
    material_height=100,
    material_thickness=3,
    kerf_width=0.2,
    cut_spacing=5,
    cut_length=70,
    cut_offset=15,
    pattern_direction='vertical'
)
```

**Best for:**
- Standing panels
- Cylindrical wrapping (vertical axis)
- Cross-grain bending in wood

## Advanced Usage

### Calculating Required Spacing for Target Bend Radius

```python
from kerf_generator import calculate_required_spacing

# I want a 30mm bend radius
target_radius = 30.0
spacing = calculate_required_spacing(
    target_bend_radius=target_radius,
    material_thickness=3.0,
    kerf_width=0.2
)

print(f"Use {spacing:.2f}mm spacing for {target_radius}mm radius")

# Now create params with this spacing
params = KerfParameters(
    material_width=150,
    material_height=150,
    material_thickness=3.0,
    kerf_width=0.2,
    cut_spacing=spacing,  # Use calculated spacing
    cut_length=120,
    cut_offset=15,
    pattern_direction='horizontal'
)
```

### Checking Pattern Info Before Export

```python
from kerf_generator import print_pattern_info

# View all calculated properties
print_pattern_info(params)

# Or access properties directly
print(f"Estimated cuts: {params.num_cuts}")
print(f"Bend radius: {params.bend_radius:.2f}mm")
print(f"Max bend angle: {params.max_bend_angle:.1f}°")
```

### Pattern Statistics

```python
from kerf_generator.patterns import pattern_statistics

lines = generate_living_hinge(params)
stats = pattern_statistics(lines)

print(f"Total cutting length: {stats['total_cut_length']:.2f}mm")
print(f"Average cut length: {stats['avg_cut_length']:.2f}mm")
print(f"Bounds: {stats['bounds']}")
```

### Multiple Patterns in One File

```python
import ezdxf

# Generate multiple patterns
params1 = KerfParameters(..., pattern_direction='horizontal')
params2 = KerfParameters(..., pattern_direction='vertical')

lines1 = generate_living_hinge(params1)
lines2 = generate_living_hinge(params2)

# Create combined DXF
doc = ezdxf.new("R2000")
msp = doc.modelspace()

# Add both patterns (offset the second one)
for line in lines1:
    msp.add_line((line.x1, line.y1), (line.x2, line.y2))

for line in lines2:
    # Offset by 250mm to the right
    msp.add_line((line.x1 + 250, line.y1), (line.x2 + 250, line.y2))

doc.saveas("combined_pattern.dxf")
```

## Tips & Best Practices

### Material Selection

**Best materials for kerf bending:**
- ✅ Plywood (3-6mm)
- ✅ MDF (3-6mm)
- ✅ Acrylic (2-4mm)
- ✅ Cardboard/Chipboard
- ⚠️ Solid wood (watch grain direction)
- ❌ Very thick materials (>6mm)

### Grain Direction in Wood

For plywood:
- **Cuts perpendicular to grain:** Easier bending, risk of splitting
- **Cuts parallel to grain:** More resistance, better strength

### Testing

**Always test first!**
1. Cut a small test piece (50×50mm)
2. Verify kerf width matches your settings
3. Test the flexibility and strength
4. Adjust spacing if needed

### Spacing Guidelines

| Bend Type | Spacing (relative to thickness) |
|-----------|--------------------------------|
| Very tight | 1.5× - 2× thickness |
| Normal | 2× - 3× thickness |
| Gentle | 3× - 4× thickness |

### Common Issues

**Pattern too stiff:**
- Decrease `cut_spacing`
- Increase `cut_length`
- Check material grain direction

**Pattern breaks when bending:**
- Increase `cut_spacing`
- Use thinner material
- Reduce kerf width (different laser settings)

**Cuts too close to edge:**
- Increase `cut_offset`

### Lightburn Setup

1. Import DXF file: File → Import
2. Select the outline layer (blue) → Right-click → Set to "Ignore"
3. Select the cuts layer (red) → Set to "Cut" mode
4. Set appropriate power and speed for your material
5. **Do a test cut first!**

### Fusion 360 Workflow

1. Create new design
2. Insert → Insert DXF
3. The pattern appears as a sketch
4. Use "Extrude" to create 3D geometry
5. Use for visualization or further CAD work

## Safety Notes

⚠️ **Laser Cutting Safety:**
- Always supervise laser cutter during operation
- Use proper ventilation
- Wear laser safety glasses
- Know your material's properties (some materials release toxic fumes)

⚠️ **Pattern Safety:**
- Very tight spacing can cause material failure
- Test patterns before final cuts
- Consider stress concentrations at cut tips

## Getting Help

- Check `examples/` directory for working scripts
- See `ONGOING_TASKS.md` for implementation details
- Run tests: `uv run pytest tests/`

## Quick Reference

```python
# Typical 3mm plywood pattern
params = KerfParameters(
    material_width=100,
    material_height=200,
    material_thickness=3,
    kerf_width=0.2,
    cut_spacing=6,           # 2× thickness
    cut_length=80,
    cut_offset=10,
    pattern_direction='horizontal'
)

# Generate and export
generate_living_hinge(params, "pattern.dxf", "pattern.png")
```
