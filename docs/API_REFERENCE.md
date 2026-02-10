# API Reference

Complete API documentation for the Kerf Generator library.

## Table of Contents
- [Main API](#main-api)
- [Parameters](#parameters)
- [Pattern Generation](#pattern-generation)
- [Export Functions](#export-functions)
- [Geometry Calculations](#geometry-calculations)

---

## Main API

### `generate_living_hinge()`

Main high-level function for generating living hinge patterns.

```python
def generate_living_hinge(
    params: KerfParameters,
    dxf_output: Optional[str | Path] = None,
    image_output: Optional[str | Path] = None,
    svg_output: Optional[str | Path] = None,
) -> List[LineSegment]
```

**Parameters:**
- `params`: KerfParameters object defining the pattern
- `dxf_output`: Optional path to save DXF file
- `image_output`: Optional path to save image preview
- `svg_output`: Optional path to save SVG file

**Returns:**
- List of LineSegment objects representing the cuts

**Example:**
```python
params = KerfParameters(...)
lines = generate_living_hinge(
    params,
    dxf_output="output.dxf",
    image_output="output.png"
)
```

---

### `print_pattern_info()`

Print detailed information about a pattern.

```python
def print_pattern_info(
    params: KerfParameters,
    lines: Optional[List[LineSegment]] = None
) -> None
```

**Parameters:**
- `params`: KerfParameters object
- `lines`: Optional list of LineSegments (will generate if not provided)

**Example:**
```python
print_pattern_info(params)
# Outputs:
# Kerf Pattern Parameters
# ==================================================
# Material: 100 × 200 × 3 mm
# ...
```

---

## Parameters

### `KerfParameters`

Main dataclass for defining pattern parameters.

```python
@dataclass
class KerfParameters:
    material_width: float
    material_height: float
    material_thickness: float
    kerf_width: float
    cut_spacing: float
    cut_length: float
    cut_offset: float
    pattern_direction: Literal["horizontal", "vertical"]
    material_name: Optional[str] = None
    notes: Optional[str] = None
```

**All dimensions in millimeters.**

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `material_width` | float | Width of material sheet (mm) |
| `material_height` | float | Height of material sheet (mm) |
| `material_thickness` | float | Thickness of material (mm) |
| `kerf_width` | float | Width of laser cut (mm) |
| `cut_spacing` | float | Distance between parallel cuts (mm) |
| `cut_length` | float | Length of each cut (mm) |
| `cut_offset` | float | Distance from edges (mm) |
| `pattern_direction` | str | "horizontal" or "vertical" |
| `material_name` | str | Optional material description |
| `notes` | str | Optional notes about pattern |

**Computed Properties:**

```python
params.bend_radius       # Estimated bend radius (mm)
params.max_bend_angle    # Maximum safe bend angle (degrees)
params.num_cuts          # Estimated number of cuts
```

**Methods:**

#### `validate()`

Validate parameters and return warnings.

```python
is_valid, warnings = params.validate()
```

Returns tuple of (bool, List[str])

#### `summary()`

Generate human-readable summary.

```python
summary_text = params.summary()
print(summary_text)
```

**Example:**
```python
params = KerfParameters(
    material_width=100,
    material_height=200,
    material_thickness=3,
    kerf_width=0.2,
    cut_spacing=5,
    cut_length=80,
    cut_offset=10,
    pattern_direction='horizontal',
    material_name="Birch Plywood"
)

print(f"Bend radius: {params.bend_radius}mm")
print(f"Number of cuts: {params.num_cuts}")
```

---

### `LineSegment`

Represents a single cut line.

```python
@dataclass
class LineSegment:
    x1: float           # Start X coordinate
    y1: float           # Start Y coordinate
    x2: float           # End X coordinate
    y2: float           # End Y coordinate
    layer: str = "cuts" # Layer name for DXF
```

**Computed Properties:**

```python
line.length      # Length of segment (mm)
line.midpoint    # Tuple of (x, y) midpoint coordinates
```

**Example:**
```python
line = LineSegment(0, 0, 10, 0)
print(f"Length: {line.length}mm")        # 10.0
print(f"Midpoint: {line.midpoint}")      # (5.0, 0.0)
```

---

## Pattern Generation

### `generate_living_hinge()` (low-level)

Generate pattern geometry without export.

```python
from kerf_generator.patterns import generate_living_hinge

lines = generate_living_hinge(params)
```

Returns List[LineSegment]

---

### `generate_outline()`

Generate material outline rectangle.

```python
from kerf_generator.patterns import generate_outline

outline = generate_outline(params)
```

Returns List[LineSegment] (4 lines forming rectangle)

**Example:**
```python
cuts = generate_living_hinge(params)
outline = generate_outline(params)

# Draw both in your own visualization
all_lines = cuts + outline
```

---

### `pattern_statistics()`

Calculate statistics about generated pattern.

```python
from kerf_generator.patterns import pattern_statistics

lines = generate_living_hinge(params)
stats = pattern_statistics(lines)
```

**Returns dict with:**
- `num_cuts`: Number of cuts
- `total_cut_length`: Total length to cut (mm)
- `avg_cut_length`: Average cut length (mm)
- `bounds`: Tuple of (min_x, min_y, max_x, max_y)

**Example:**
```python
stats = pattern_statistics(lines)
print(f"Will cut {stats['total_cut_length']:.2f}mm total")
print(f"Pattern bounds: {stats['bounds']}")
```

---

## Export Functions

### `export_dxf()`

Export pattern to DXF file.

```python
def export_dxf(
    lines: List[LineSegment],
    params: KerfParameters,
    output_path: str | Path,
    include_outline: bool = True
) -> None
```

**Parameters:**
- `lines`: List of LineSegment objects to export
- `params`: KerfParameters used to generate pattern
- `output_path`: Where to save DXF file
- `include_outline`: Whether to include material boundary (default: True)

**Layers created:**
- `"cuts"`: Red, cut lines
- `"outline"`: Blue, material boundary (reference only)

**Example:**
```python
from kerf_generator import export_dxf

lines = generate_living_hinge(params)
export_dxf(lines, params, "pattern.dxf")
```

---

### `export_image()`

Export pattern as image preview.

```python
def export_image(
    lines: List[LineSegment],
    params: KerfParameters,
    output_path: str | Path,
    format: Literal["png", "svg", "pdf"] = "png",
    dpi: int = 300,
    show_grid: bool = True,
    show_annotations: bool = True
) -> None
```

**Parameters:**
- `lines`: LineSegments to draw
- `params`: Pattern parameters
- `output_path`: Where to save image
- `format`: Output format ("png", "svg", "pdf")
- `dpi`: Resolution for raster formats (default: 300)
- `show_grid`: Show grid overlay (default: True)
- `show_annotations`: Show parameter info box (default: True)

**Example:**
```python
from kerf_generator import export_image

export_image(
    lines,
    params,
    "preview.png",
    format="png",
    dpi=300,
    show_grid=True
)
```

---

### `export_svg()`

Export pattern as SVG (convenience wrapper).

```python
def export_svg(
    lines: List[LineSegment],
    params: KerfParameters,
    output_path: str | Path,
    include_outline: bool = True
) -> None
```

Equivalent to `export_image()` with format="svg", no grid, no annotations.

---

### `export_all()`

Export pattern in all formats at once.

```python
def export_all(
    lines: List[LineSegment],
    params: KerfParameters,
    output_dir: str | Path,
    base_name: str = "pattern"
) -> dict[str, Path]
```

**Returns:** Dictionary mapping format names to file paths
```python
{
    "dxf": Path("output/pattern.dxf"),
    "png": Path("output/pattern.png"),
    "svg": Path("output/pattern.svg")
}
```

**Example:**
```python
from kerf_generator import export_all

files = export_all(lines, params, "output", "my_hinge")
print(f"DXF saved to: {files['dxf']}")
```

---

## Geometry Calculations

### `calculate_bend_radius()`

Calculate approximate bend radius from parameters.

```python
def calculate_bend_radius(
    material_thickness: float,
    cut_spacing: float,
    kerf_width: float,
    cut_length: float
) -> float
```

**Formula:**
```
bend_radius = (material_thickness × cut_spacing) / (2 × kerf_width)
```

**Example:**
```python
from kerf_generator import calculate_bend_radius

radius = calculate_bend_radius(
    material_thickness=3.0,
    cut_spacing=5.0,
    kerf_width=0.2,
    cut_length=80.0
)
print(f"Bend radius: {radius}mm")  # 37.5mm
```

---

### `calculate_required_spacing()`

Calculate spacing needed for target bend radius.

```python
def calculate_required_spacing(
    target_bend_radius: float,
    material_thickness: float,
    kerf_width: float
) -> float
```

Inverse of `calculate_bend_radius()`.

**Formula:**
```
cut_spacing = (2 × kerf_width × target_bend_radius) / material_thickness
```

**Example:**
```python
from kerf_generator import calculate_required_spacing

# I want a 30mm radius
spacing = calculate_required_spacing(
    target_bend_radius=30.0,
    material_thickness=3.0,
    kerf_width=0.2
)
print(f"Use {spacing}mm spacing")  # 4.0mm
```

---

### `calculate_max_bend_angle()`

Calculate maximum practical bend angle.

```python
def calculate_max_bend_angle(
    material_thickness: float,
    cut_spacing: float,
    cut_length: float
) -> float
```

Returns maximum angle in degrees (capped at 90°).

**Example:**
```python
from kerf_generator import calculate_max_bend_angle

max_angle = calculate_max_bend_angle(3.0, 5.0, 80.0)
print(f"Max angle: {max_angle}°")
```

---

### `calculate_minimum_spacing()`

Calculate minimum safe spacing between cuts.

```python
def calculate_minimum_spacing(
    material_thickness: float,
    kerf_width: float,
    safety_factor: float = 2.0
) -> float
```

**Parameters:**
- `material_thickness`: Thickness in mm
- `kerf_width`: Kerf width in mm
- `safety_factor`: Safety multiplier (default: 2.0)

Returns minimum spacing in mm.

**Example:**
```python
from kerf_generator import calculate_minimum_spacing

min_spacing = calculate_minimum_spacing(3.0, 0.2)
print(f"Don't go below {min_spacing}mm spacing")
```

---

## Type Hints

All functions include complete type hints:

```python
from typing import List, Optional, Literal
from pathlib import Path

def generate_living_hinge(
    params: KerfParameters,
    dxf_output: Optional[str | Path] = None,
    image_output: Optional[str | Path] = None,
    svg_output: Optional[str | Path] = None,
) -> List[LineSegment]:
    ...
```

Use with mypy for type checking:
```bash
uv run mypy src/
```

---

## Error Handling

### Parameter Validation

`KerfParameters` validates on creation:

```python
try:
    params = KerfParameters(
        material_width=-100,  # Invalid!
        ...
    )
except ValueError as e:
    print(f"Invalid parameters: {e}")
```

### Warnings

Non-fatal issues generate warnings:

```python
import warnings

params = KerfParameters(
    ...,
    cut_spacing=2,  # Very tight!
    ...
)
# UserWarning: Cut spacing (2mm) is below recommended minimum...
```

Suppress warnings:
```python
warnings.filterwarnings('ignore', category=UserWarning)
```

---

## Complete Example

```python
from kerf_generator import (
    KerfParameters,
    generate_living_hinge,
    calculate_required_spacing,
    print_pattern_info,
    export_all
)

# Calculate spacing for target radius
spacing = calculate_required_spacing(
    target_bend_radius=25.0,
    material_thickness=3.0,
    kerf_width=0.2
)

# Create parameters
params = KerfParameters(
    material_width=150,
    material_height=150,
    material_thickness=3.0,
    kerf_width=0.2,
    cut_spacing=spacing,
    cut_length=120,
    cut_offset=15,
    pattern_direction='horizontal',
    material_name="3mm Birch Plywood",
    notes="Box hinge - 25mm radius"
)

# Print info
print_pattern_info(params)

# Generate pattern
lines = generate_living_hinge(params)

# Export everything
files = export_all(lines, params, "output", "box_hinge")

print(f"\nExported to:")
for format, path in files.items():
    print(f"  {format.upper()}: {path}")
```
