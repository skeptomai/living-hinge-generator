# Kerf Cutting Pattern Generator - Status

## Project Overview
Python tool for generating kerf cutting and bending patterns for laser cutting. Outputs DXF files (for Fusion 360 and Lightburn) and preview images for verification.

## ✅ COMPLETED - Core Implementation

### Pattern Types Implemented
- [x] **Living Hinge** - Traditional parallel cuts for unidirectional bending
- [x] **Diamond Pattern** - Elongated vertical diamonds with split halves for horizontal bending
- [x] **Oval Pattern** - Elongated vertical ovals with split halves for smooth bending

### Core Modules
- [x] `geometry.py` - Mathematical calculations for bend radius, spacing, validation
- [x] `parameters.py` - KerfParameters dataclass with PatternType support
- [x] `patterns.py` - Pattern generation for all three pattern types
- [x] `exporters.py` - DXF, PNG, and SVG export with optimized layouts
- [x] `cli.py` - Full command-line interface with interactive mode

### Features
- [x] DXF export (compatible with Fusion 360 and Lightburn)
- [x] PNG/SVG preview generation
- [x] Parameter validation and safety warnings
- [x] Bend radius and angle calculations
- [x] Interactive and command-line modes
- [x] Multiple example scripts

### Pattern Details

#### Diamond Pattern
- Elongated vertical diamonds alternating with split diamonds
- Split diamonds: top V (apex down) + bottom inverted V (apex up)
- Full diamonds: narrow elongated shapes with minimal top/bottom inset
- Optimized for horizontal bending with 10% gap between split halves
- Horizontal fill optimization with minimal side margins

#### Oval Pattern
- Elongated vertical ovals alternating with split ovals
- Smooth elliptical curves approximated with line segments
- Similar layout to diamond pattern but with curved shapes
- Better for applications requiring smooth stress distribution

### Export Quality
- [x] Large canvas with proper margins for legends
- [x] Clean parameter annotation box
- [x] Optimized legend placement (material/cuts legend removed per user preference)
- [x] High-resolution output (300 DPI)

## Implementation Phases - Summary

### Phase 1: Core Infrastructure ✅
- [x] Project structure with uv
- [x] Git repository initialized
- [x] Dependencies added (ezdxf, matplotlib, numpy, click)
- [x] Module structure created
- [x] Pytest configuration

### Phase 2: Mathematical Foundation ✅
- [x] Bend radius calculations
- [x] Spacing validation
- [x] Shape counting for 2D patterns
- [x] Parameter validation
- [x] Safety warnings for spacing below recommended minimum

### Phase 3: Pattern Generation ✅
- [x] KerfParameters dataclass with full validation
- [x] Living hinge generator (horizontal/vertical)
- [x] Diamond pattern generator (elongated vertical)
- [x] Oval pattern generator (elongated vertical)
- [x] Pattern dispatcher based on pattern_type

### Phase 4: Export Functionality ✅
- [x] DXF export with layer management
- [x] Tested with Fusion 360 and Lightburn
- [x] Image preview with matplotlib
- [x] SVG export support
- [x] Optimized canvas layout with configurable margins

### Phase 5: Integration & Examples ✅
- [x] High-level API in __init__.py
- [x] Example scripts:
  - [x] basic_example.py
  - [x] vertical_pattern.py
  - [x] tight_radius.py
  - [x] lamp_shade.py
  - [x] material_comparison.py
  - [x] box_hinge.py
  - [x] diamond_pattern.py
  - [x] oval_pattern.py
  - [x] pattern_comparison.py
- [x] CLI interface with full options
- [x] Interactive mode

### Phase 6: Documentation & Polish ✅
- [x] Comprehensive README.md
- [x] CLAUDE.md for AI assistant context
- [x] Docstrings on all functions
- [x] Type hints throughout
- [x] Example outputs in output/ directory

### Phase 7: Testing & Validation ✅
- [x] DXF verified to import into Fusion 360
- [x] DXF verified to work with Lightburn
- [x] Multiple parameter combinations tested
- [x] Safety validations in place

## Recent Updates (Current Session)

### Diamond & Oval Pattern Refinement
- [x] Corrected pattern orientation (elongated vertical instead of 2D grid)
- [x] Implemented split diamond geometry (top V + gap + bottom inverted V)
- [x] Matched widths between full and split diamonds
- [x] Optimized gap sizes (10% for split diamonds, 1% inset for full)
- [x] Improved horizontal fill (minimal side margins, better density)
- [x] Fine-tuned density (6.5mm spacing for tighter fill)

### Image Export Improvements
- [x] Larger canvas (50% wider, 20% taller)
- [x] Removed redundant material/cuts legend
- [x] Repositioned parameter stats box
- [x] Better margin allocation (top margin for annotations)
- [x] Cleaner, more professional layout

## File Format Support

| Format | Lightburn | Fusion 360 | Notes |
|--------|-----------|------------|-------|
| DXF | ✅ Best | ✅ Best | Precision CAD format, preserves layers |
| SVG | ✅ Good | ✅ Good | Vector format, converted to sketches |
| PNG | ❌ Trace only | ❌ No | Preview only, not for precision work |

**Recommendation**: Use DXF for both Lightburn and Fusion 360

## Usage

### Command Line
```bash
# Generate diamond pattern
kerf generate -w 100 -h 100 -t 3 -k 0.2 -s 6.5 -l 8 -o 8 -p diamond \\
  --dxf output/pattern.dxf --png output/pattern.png

# Interactive mode
kerf interactive

# Calculate bend radius
kerf calc-radius -s 5 -t 3 -k 0.2
```

### Python API
```python
from kerf_generator import KerfParameters, generate_living_hinge

params = KerfParameters(
    material_width=100,
    material_height=100,
    material_thickness=3,
    kerf_width=0.2,
    cut_spacing=6.5,
    cut_length=8,
    cut_offset=8,
    pattern_type='diamond'
)

lines = generate_living_hinge(
    params,
    dxf_output="output/pattern.dxf",
    image_output="output/pattern.png"
)
```

## Future Enhancements

- [ ] Additional pattern types (hexagonal, crosshatch)
- [ ] Variable density patterns (gradients)
- [ ] Import DXF shapes and apply patterns
- [ ] 3D preview of bent result
- [ ] Web-based parameter calculator
- [ ] Material library with presets
- [ ] Pattern rotation/orientation options
- [ ] Automated test suite expansion

## Notes

- All dimensions in millimeters
- Pattern coordinates: origin at bottom-left
- DXF uses layers: "outline" (blue) and "cuts" (red)
- Minimum spacing validation based on material thickness and kerf width
- Pattern types are mutually exclusive (can't mix in single generation)
