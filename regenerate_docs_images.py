#!/usr/bin/env python3
"""
Regenerate all documentation images in docs/images/
"""
from kerf_generator import KerfParameters, generate_living_hinge

# Ensure output directory exists
import os
os.makedirs("docs/images", exist_ok=True)

print("Regenerating documentation images...")

# 1. Diamond Pattern - Single Row (100mm x 140mm)
print("\n1. Generating diamond_single_row...")
params = KerfParameters(
    material_width=100,
    material_height=140,
    material_thickness=3,
    kerf_width=0.2,
    cut_spacing=6.5,
    cut_length=12,
    cut_offset=8,
    pattern_type='diamond',
    num_vertical_rows=1
)
generate_living_hinge(
    params,
    dxf_output="docs/images/diamond_single_row.dxf",
    image_output="docs/images/diamond_single_row.png"
)
print(f"   Dimensions: {params.material_width}mm x {params.material_height}mm")

# 2. Tall Diamond - Auto Stacking (100mm x 320mm)
print("\n2. Generating tall_diamond_auto...")
params = KerfParameters(
    material_width=100,
    material_height=320,
    material_thickness=3,
    kerf_width=0.2,
    cut_spacing=6.5,
    cut_length=12,
    cut_offset=8,
    pattern_type='diamond',
    num_vertical_rows=None  # Auto-calculate
)
generate_living_hinge(
    params,
    dxf_output="docs/images/tall_diamond_auto.dxf",
    image_output="docs/images/tall_diamond_auto.png"
)
print(f"   Dimensions: {params.material_width}mm x {params.material_height}mm (auto: {params.effective_num_rows} rows)")

# 3. Short Material - 2 Rows Override (100mm x 120mm)
print("\n3. Generating short_material_2rows_override...")
params = KerfParameters(
    material_width=100,
    material_height=120,
    material_thickness=3,
    kerf_width=0.2,
    cut_spacing=6.5,
    cut_length=12,
    cut_offset=8,
    pattern_type='diamond',
    num_vertical_rows=2  # Manual override
)
generate_living_hinge(
    params,
    dxf_output="docs/images/short_material_2rows_override.dxf",
    image_output="docs/images/short_material_2rows_override.png"
)
print(f"   Dimensions: {params.material_width}mm x {params.material_height}mm (manual: {params.effective_num_rows} rows)")

# 4. Oval Pattern - Single Row (100mm x 140mm)
print("\n4. Generating oval_single_row...")
params = KerfParameters(
    material_width=100,
    material_height=140,
    material_thickness=3,
    kerf_width=0.2,
    cut_spacing=6.5,
    cut_length=12,
    cut_offset=8,
    pattern_type='oval',
    num_vertical_rows=1
)
generate_living_hinge(
    params,
    dxf_output="docs/images/oval_single_row.dxf",
    image_output="docs/images/oval_single_row.png"
)
print(f"   Dimensions: {params.material_width}mm x {params.material_height}mm")

# 5. Tall Oval - Auto Stacking (100mm x 320mm)
print("\n5. Generating tall_oval_auto...")
params = KerfParameters(
    material_width=100,
    material_height=320,
    material_thickness=3,
    kerf_width=0.2,
    cut_spacing=6.5,
    cut_length=12,
    cut_offset=8,
    pattern_type='oval',
    num_vertical_rows=None  # Auto-calculate
)
generate_living_hinge(
    params,
    dxf_output="docs/images/tall_oval_auto.dxf",
    image_output="docs/images/tall_oval_auto.png"
)
print(f"   Dimensions: {params.material_width}mm x {params.material_height}mm (auto: {params.effective_num_rows} rows)")

# 6. Short Material Oval - 2 Rows Override (100mm x 120mm)
print("\n6. Generating short_material_2rows_oval_override...")
params = KerfParameters(
    material_width=100,
    material_height=120,
    material_thickness=3,
    kerf_width=0.2,
    cut_spacing=6.5,
    cut_length=12,
    cut_offset=8,
    pattern_type='oval',
    num_vertical_rows=2  # Manual override
)
generate_living_hinge(
    params,
    dxf_output="docs/images/short_material_2rows_oval_override.dxf",
    image_output="docs/images/short_material_2rows_oval_override.png"
)
print(f"   Dimensions: {params.material_width}mm x {params.material_height}mm (manual: {params.effective_num_rows} rows)")

print("\n✅ All documentation images regenerated!")
