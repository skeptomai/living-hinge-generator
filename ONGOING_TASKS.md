# Kerf Cutting Pattern Generator - Implementation Plan

## Project Overview
Python tool for generating kerf cutting and bending patterns for laser cutting. Outputs DXF files (for Fusion 360 and Lightburn) and preview images for verification.

## Target Scope
- **Pattern Type**: Living hinge (parallel cuts)
- **Geometry**: Flat rectangular surfaces
- **Key Parameters**: Cut spacing, cut length, material dimensions, kerf width, bend angle/radius
- **Output Formats**: DXF (primary), PNG/SVG (preview)

## Project Structure
```
kerf-burning/
├── src/
│   └── kerf_generator/
│       ├── __init__.py          # Package initialization
│       ├── patterns.py          # Core pattern generation logic
│       ├── geometry.py          # Mathematical calculations for bending
│       ├── exporters.py         # DXF and image export functions
│       └── parameters.py        # Parameter validation and dataclasses
├── docs/                        # Documentation
├── examples/                    # Example scripts and outputs
├── tests/                       # Unit tests
├── pyproject.toml              # Project metadata and dependencies
├── CLAUDE.md                   # Project context for AI assistant
└── ONGOING_TASKS.md           # This file

```

## Core Functionality

### 1. Mathematical Model (geometry.py)
- Implement kerf bending calculations based on material properties
- Formula to relate: cut spacing, cut length, material thickness, kerf width → achievable bend radius
- Allow both forward (specify dimensions) and reverse (specify desired bend, calculate spacing) calculations
- **Key formulas to implement**:
  - Bend radius calculation from spacing and material thickness
  - Maximum bend angle calculations
  - Stress/strain considerations (optional, advanced)

### 2. Parameter Management (parameters.py)
```python
@dataclass
class KerfParameters:
    material_width: float      # mm - width of material sheet
    material_height: float     # mm - height of material sheet
    material_thickness: float  # mm - thickness of material
    kerf_width: float          # mm - laser kerf width
    cut_spacing: float         # mm - distance between parallel cuts
    cut_length: float          # mm - length of each cut
    cut_offset: float          # mm - offset from edges
    pattern_direction: str     # 'horizontal' or 'vertical'
    # Optional calculated fields:
    # bend_radius: Optional[float]
    # bend_angle: Optional[float]
```

**Parameter Validation**:
- Ensure all dimensions are positive
- Verify cut_length < material dimension
- Check that spacing allows for structural integrity
- Warn if parameters might lead to material failure

### 3. Pattern Generator (patterns.py)
- Generate array of cut lines based on parameters
- Calculate cut positions with proper spacing
- Handle edge cases (partial cuts, offset requirements)
- Return geometry as list of line segments
- Support both horizontal and vertical cut directions

**Core function**:
```python
def generate_living_hinge(params: KerfParameters) -> List[LineSegment]:
    """
    Generate living hinge pattern based on parameters.
    Returns list of line segments representing cuts.
    """
```

### 4. Export Functions (exporters.py)

#### DXF Export
- Use `ezdxf` library
- Create layers:
  - Layer 0: Material outline (blue)
  - Layer 1: Cut lines (red) - for laser cutting
- Set appropriate line weights and colors
- Units: millimeters
- DXF version: AC1015 (AutoCAD 2000) for compatibility

```python
def export_dxf(lines: List[LineSegment],
               params: KerfParameters,
               output_path: str) -> None:
    """Export pattern to DXF file."""
```

#### Image Preview Export
- Use `matplotlib`
- Color coding:
  - Black: Material outline
  - Red: Cut lines
  - Optional: Grid overlay for scale reference
- Include parameter annotations on image
- Support PNG and SVG formats

```python
def export_image(lines: List[LineSegment],
                 params: KerfParameters,
                 output_path: str,
                 format: str = 'png') -> None:
    """Export pattern preview image."""
```

### 5. High-Level API (__init__.py)
```python
def generate_living_hinge(params: KerfParameters,
                          dxf_output: Optional[str] = None,
                          image_output: Optional[str] = None) -> List[LineSegment]:
    """
    Main API function to generate and export living hinge pattern.

    Args:
        params: KerfParameters object with pattern specifications
        dxf_output: Path to save DXF file (optional)
        image_output: Path to save preview image (optional)

    Returns:
        List of LineSegment objects representing the pattern
    """
```

## Dependencies (to add to pyproject.toml)
- `ezdxf` - DXF file creation and manipulation
- `matplotlib` - Image preview generation
- `numpy` - Numerical calculations
- `pillow` - Additional image handling (optional)

**Development dependencies**:
- `pytest` - Testing framework
- `black` - Code formatting
- `mypy` - Type checking
- `ruff` - Linting

## Implementation Steps

### Phase 1: Core Infrastructure
- [x] Set up project structure with uv
- [x] Initialize git repository
- [ ] Add dependencies to pyproject.toml
- [ ] Create basic module structure with stubs
- [ ] Set up pytest configuration

### Phase 2: Mathematical Foundation
- [ ] Implement geometry calculations in geometry.py
  - [ ] Bend radius formula
  - [ ] Spacing calculations
  - [ ] Validation functions
- [ ] Create unit tests for geometry module
- [ ] Document formulas and assumptions

### Phase 3: Pattern Generation
- [ ] Implement KerfParameters dataclass with validation
- [ ] Create living hinge pattern generator
- [ ] Add tests for pattern generation
- [ ] Handle edge cases (boundaries, partial cuts)

### Phase 4: Export Functionality
- [ ] Implement DXF export with ezdxf
  - [ ] Layer management
  - [ ] Proper scaling and units
  - [ ] Test with Fusion 360 and Lightburn
- [ ] Implement image preview export
  - [ ] Matplotlib rendering
  - [ ] Parameter annotations
  - [ ] Multiple format support

### Phase 5: Integration & Examples
- [ ] Create high-level API in __init__.py
- [ ] Write example scripts in examples/
  - [ ] Basic rectangular pattern
  - [ ] Parameter sweep examples
  - [ ] Bend radius calculator example
- [ ] Add CLI interface (optional)

### Phase 6: Documentation & Polish
- [ ] Write comprehensive README.md
- [ ] Add docstrings to all functions
- [ ] Create usage guide in docs/
- [ ] Add type hints throughout
- [ ] Format code with black
- [ ] Run linting with ruff

### Phase 7: Testing & Validation
- [ ] Test outputs with actual laser cutter (Lightburn)
- [ ] Verify DXF import in Fusion 360
- [ ] Test various parameter combinations
- [ ] Document any limitations or gotchas

## Usage Example
```python
from kerf_generator import generate_living_hinge, KerfParameters

# Define parameters
params = KerfParameters(
    material_width=100,        # 100mm wide
    material_height=200,       # 200mm tall
    material_thickness=3,      # 3mm thick plywood
    kerf_width=0.2,           # 0.2mm laser kerf
    cut_spacing=5,            # 5mm between cuts
    cut_length=80,            # 80mm long cuts
    cut_offset=10,            # 10mm from edges
    pattern_direction='horizontal'
)

# Generate and export
lines = generate_living_hinge(
    params,
    dxf_output="output/living_hinge.dxf",
    image_output="output/living_hinge.png"
)

print(f"Generated {len(lines)} cut lines")
```

## Open Questions
- [ ] CLI tool in addition to importable module?
- [ ] Units: Confirm millimeters as default (can add conversion utilities)
- [ ] Calculator mode: Add utility to determine optimal parameters for target bend radius?
- [ ] Support for curved paths in future versions?
- [ ] Integration with CAD software APIs for direct export?

## Notes on Lightburn
- Lightburn **can** import images (JPG, PNG, BMP) but requires tracing to convert to vectors
- For precision cutting, vector formats (DXF, SVG, AI) are strongly preferred
- Lightburn supports layer colors for different operations (cut/engrave/score)
- Recommend using DXF as primary output format

## Future Enhancements (Post-MVP)
- Additional pattern types (lattice, crosshatch, custom geometries)
- Import existing DXF and apply patterns to shapes
- Web-based parameter calculator
- Material library with preset kerf widths
- Parametric pattern variations (tapering, varying density)
- 3D preview of bent result
