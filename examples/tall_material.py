#!/usr/bin/env python3
"""
Example: Tall Material with Stacked Pattern Rows

Demonstrates how diamond and oval patterns automatically stack into multiple
rows for tall materials. This provides better flexibility control and structural
integrity compared to single very elongated shapes.

For materials taller than 150mm, patterns are automatically divided into
multiple horizontal bands, each with its own complete pattern sequence.
"""

from kerf_generator import KerfParameters, generate_living_hinge, export_all
from pathlib import Path

# Output directory
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

# Tall material: 100mm wide × 320mm tall
# This will automatically create 3 rows (each ~106mm tall)
tall_diamond_params = KerfParameters(
    material_width=100,
    material_height=320,
    material_thickness=3,
    kerf_width=0.2,
    cut_spacing=6.5,
    cut_length=12,
    cut_offset=8,
    pattern_type='diamond',
    num_vertical_rows=None,  # Auto-calculate (will result in 3 rows)
    material_name="Tall Birch Plywood"
)

print("=" * 70)
print("Example: Tall Material with Stacked Rows")
print("=" * 70)
print()
print("Generating tall diamond pattern (auto-stacked rows)...")
print(f"Material: {tall_diamond_params.material_width} × {tall_diamond_params.material_height} mm")
print(f"Will auto-stack into {tall_diamond_params.effective_num_rows} rows")
print()

# Generate and export
lines = generate_living_hinge(tall_diamond_params)
files = export_all(lines, tall_diamond_params, output_dir, "tall_diamond_auto")

print(f"✓ Generated {len(lines)} line segments")
print(f"✓ Exported files:")
for fmt, path in files.items():
    print(f"  • {fmt.upper()}: {path}")
print()

# Example with manual override: Force 2 rows instead of auto-calculated 3
tall_diamond_manual = KerfParameters(
    material_width=100,
    material_height=320,
    material_thickness=3,
    kerf_width=0.2,
    cut_spacing=6.5,
    cut_length=12,
    cut_offset=8,
    pattern_type='diamond',
    num_vertical_rows=2,  # Manual override: force 2 rows
    material_name="Tall Birch Plywood (2 rows)"
)

print("Generating tall diamond pattern (manual 2 rows)...")
print(f"Will use {tall_diamond_manual.effective_num_rows} rows (manually specified)")
print()

lines = generate_living_hinge(tall_diamond_manual)
files = export_all(lines, tall_diamond_manual, output_dir, "tall_diamond_2rows")

print(f"✓ Generated {len(lines)} line segments")
print(f"✓ Exported files:")
for fmt, path in files.items():
    print(f"  • {fmt.upper()}: {path}")
print()

# Oval pattern example
tall_oval_params = KerfParameters(
    material_width=100,
    material_height=320,
    material_thickness=3,
    kerf_width=0.2,
    cut_spacing=6.5,
    cut_length=12,
    cut_offset=8,
    pattern_type='oval',
    num_vertical_rows=None,  # Auto-calculate
    material_name="Tall Birch Plywood (Oval)"
)

print("Generating tall oval pattern (auto-stacked rows)...")
print(f"Will auto-stack into {tall_oval_params.effective_num_rows} rows")
print()

lines = generate_living_hinge(tall_oval_params)
files = export_all(lines, tall_oval_params, output_dir, "tall_oval_auto")

print(f"✓ Generated {len(lines)} line segments")
print(f"✓ Exported files:")
for fmt, path in files.items():
    print(f"  • {fmt.upper()}: {path}")
print()

print("=" * 70)
print("Key Insights:")
print("=" * 70)
print(f"• Auto-calculation threshold: 150mm")
print(f"• Materials ≤ 150mm: 1 row (full height pattern)")
print(f"• Materials > 150mm: Divided into ~150mm rows")
print(f"• 320mm material → {tall_diamond_params.effective_num_rows} rows of ~{320 / tall_diamond_params.effective_num_rows:.1f}mm each")
print(f"• Manual override available via num_vertical_rows parameter")
print()
print("Benefits of stacked rows:")
print("  - Better flexibility control (multiple hinge zones)")
print("  - Improved structural integrity")
print("  - Enables compound curves")
print("  - Better stress distribution")
print()
print("Done! Open the DXF files in Lightburn or Fusion 360.")
