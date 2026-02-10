# CLI Usage Guide

The `kerf` command-line tool makes it easy to generate kerf cutting patterns without writing Python code.

## Installation

The CLI is installed automatically with the package:

```bash
cd kerf-burning
uv sync  # Install package with CLI
```

Now the `kerf` command is available via `uv run`:

```bash
uv run kerf --help
```

## Commands

### `kerf generate` - Generate Patterns

Generate a living hinge pattern with all parameters specified.

**Basic usage:**
```bash
uv run kerf generate \
  --width 100 \
  --height 200 \
  --thickness 3 \
  --kerf 0.2 \
  --spacing 5 \
  --length 80 \
  --offset 10 \
  --direction horizontal \
  --output-dir output \
  --name my_pattern
```

**Short form:**
```bash
uv run kerf generate -w 100 -h 200 -t 3 -k 0.2 -s 5 -l 80 -o 10 -d h \
  --output-dir output --name my_pattern
```

This creates:
- `output/my_pattern.dxf` - For laser cutting
- `output/my_pattern.png` - Preview image
- `output/my_pattern.svg` - Vector preview

**Individual outputs:**
```bash
uv run kerf generate -w 100 -h 200 -t 3 -k 0.2 -s 5 -l 80 \
  --dxf pattern.dxf \
  --png preview.png
```

**Options:**
- `-w, --width` - Material width (mm) *required*
- `-h, --height` - Material height (mm) *required*
- `-t, --thickness` - Material thickness (mm) *required*
- `-k, --kerf` - Laser kerf width (mm) *required*
- `-s, --spacing` - Cut spacing (mm) *required*
- `-l, --length` - Cut length (mm) *required*
- `-o, --offset` - Edge offset (mm) *default: 10*
- `-d, --direction` - Cut direction: `horizontal`, `vertical`, `h`, `v` *default: horizontal*
- `-m, --material-name` - Optional material name for documentation
- `--dxf PATH` - Output DXF file
- `--png PATH` - Output PNG preview
- `--svg PATH` - Output SVG file
- `--output-dir DIR` - Directory for all formats (use with `--name`)
- `--name NAME` - Base filename (use with `--output-dir`)
- `--no-show-info` - Skip showing pattern info before generating

---

### `kerf interactive` - Interactive Wizard

Guided wizard that asks questions and generates a pattern.

```bash
uv run kerf interactive
```

**Example session:**
```
============================================================
Kerf Pattern Generator - Interactive Mode
============================================================

Material width (mm): 100
Material height (mm): 200
Material thickness (mm): 3
Laser kerf width (mm) [0.2]: 0.2

Cut pattern settings:
  Spacing between cuts (mm): 5
  Length of each cut (mm): 80
  Edge offset (mm) [10]: 10
  Cut direction [horizontal/vertical/h/v] (horizontal): h

Material name (optional, press Enter to skip): 3mm Plywood

[Shows pattern info and preview]

Generate pattern with these parameters? [Y/n]: y

Output filename (without extension) [pattern]: box_hinge
Generate PNG preview? [Y/n]: y
Generate SVG file? [y/N]: n

Generating pattern...

✓ Generated 37 cuts
✓ DXF saved to: box_hinge.dxf
✓ PNG saved to: box_hinge.png

Done! Import the DXF into Lightburn or Fusion 360.
```

---

### `kerf calc-spacing` - Calculate Spacing

Calculate the cut spacing needed for a target bend radius.

```bash
uv run kerf calc-spacing --radius 30 --thickness 3 --kerf 0.2
```

**Output:**
```
Target bend radius: 30.0 mm
Material thickness: 3.0 mm
Laser kerf: 0.2 mm

→ Required cut spacing: 4.00 mm

⚠️  Warning: This spacing is below the recommended minimum (9.00 mm)
   Risk of material failure during cutting or bending.
```

**Options:**
- `-r, --radius` - Target bend radius (mm) *required*
- `-t, --thickness` - Material thickness (mm) *required*
- `-k, --kerf` - Laser kerf width (mm) *required*

---

### `kerf calc-radius` - Calculate Bend Radius

Calculate the bend radius from cut spacing.

```bash
uv run kerf calc-radius --spacing 5 --thickness 3 --kerf 0.2
```

**Output:**
```
Cut spacing: 5.0 mm
Material thickness: 3.0 mm
Laser kerf: 0.2 mm

→ Estimated bend radius: 37.50 mm

⚠️  Warning: This spacing is below the recommended minimum (9.00 mm)
```

**Options:**
- `-s, --spacing` - Cut spacing (mm) *required*
- `-t, --thickness` - Material thickness (mm) *required*
- `-k, --kerf` - Laser kerf width (mm) *required*
- `-l, --length` - Cut length (mm) *default: 100*

---

### `kerf info` - Show Pattern Info

Display information about pattern parameters without generating files.

**Quick calculation:**
```bash
uv run kerf info --spacing 5 --thickness 3 --kerf 0.2
```

**Full pattern info:**
```bash
uv run kerf info -w 100 -h 200 -t 3 -k 0.2 -s 5 -l 80 -o 10 -d horizontal
```

Shows calculated bend radius, number of cuts, and safety warnings.

---

## Common Workflows

### Quick Pattern Generation

```bash
# 1. Calculate spacing for your target radius
uv run kerf calc-spacing --radius 40 --thickness 3 --kerf 0.2

# 2. Use that spacing to generate pattern
uv run kerf generate -w 150 -h 100 -t 3 -k 0.2 -s 5.33 -l 80 \
  --output-dir output --name box_hinge
```

### Test Multiple Spacings

```bash
# Generate test patterns with different spacing
for spacing in 4 5 6 7 8; do
  uv run kerf generate -w 80 -h 50 -t 3 -k 0.2 -s $spacing -l 60 \
    --output-dir tests --name "test_${spacing}mm" --no-show-info
done
```

### Material Calibration

```bash
# Create test strips for finding optimal kerf width
for kerf in 0.15 0.20 0.25 0.30; do
  uv run kerf generate -w 80 -h 50 -t 3 -k $kerf -s 6 -l 60 \
    --output-dir calibration --name "kerf_${kerf}mm" --no-show-info
done
```

---

## Tips

### Short Option Names

Use short options for faster typing:
- `-w` width
- `-h` height
- `-t` thickness
- `-k` kerf
- `-s` spacing
- `-l` length
- `-o` offset
- `-d` direction

### Direction Shortcuts

- `h` = `horizontal`
- `v` = `vertical`

### Suppressing Info

Add `--no-show-info` to skip the parameter display:
```bash
uv run kerf generate ... --no-show-info
```

### Batch Processing

Use shell loops or scripts to generate multiple patterns:
```bash
#!/bin/bash
# generate_patterns.sh

materials=("plywood:0.2" "acrylic:0.25" "mdf:0.3")

for mat in "${materials[@]}"; do
  name="${mat%:*}"
  kerf="${mat#*:}"

  uv run kerf generate -w 100 -h 200 -t 3 -k "$kerf" -s 6 -l 80 \
    --output-dir "output_$name" --name "$name" --no-show-info
done
```

---

## Getting Help

```bash
# Main help
uv run kerf --help

# Command-specific help
uv run kerf generate --help
uv run kerf interactive --help
uv run kerf calc-spacing --help
```

---

## Examples

### Box Hinge
```bash
uv run kerf generate -w 150 -h 80 -t 3 -k 0.2 -s 6 -l 60 -d h \
  --material-name "3mm Plywood" \
  --output-dir output --name box_hinge
```

### Lamp Shade
```bash
# Calculate for 100mm diameter (50mm radius)
uv run kerf calc-spacing --radius 50 --thickness 3 --kerf 0.25
# Use the result: 8.33mm spacing

uv run kerf generate -w 315 -h 150 -t 3 -k 0.25 -s 8.33 -l 120 -d v \
  --material-name "3mm Acrylic" \
  --output-dir output --name lamp_shade
```

### Vertical Pattern
```bash
uv run kerf generate -w 200 -h 100 -t 3 -k 0.2 -s 6 -l 70 -d v \
  --output-dir output --name vertical_hinge
```

---

## Troubleshooting

**Command not found:**
```bash
# Use uv run to execute
uv run kerf --help
```

**Invalid parameters error:**
- Check that cut length fits within material dimensions
- Verify spacing is reasonable for material thickness
- Ensure all required parameters are provided

**Warnings about spacing:**
- Below minimum: Increase spacing or use thicker material
- Pattern validation warnings are advisory, not errors

---

## Next Steps

- Import DXF files into Lightburn or Fusion 360
- Cut test patterns to verify kerf width
- Experiment with spacing to find optimal flexibility
- See `docs/USER_GUIDE.md` for detailed parameter explanations
