#!/usr/bin/env python3
"""
Example of generating a vertical living hinge pattern.

This demonstrates vertical cuts (running top-bottom, spaced left-right).
"""

from kerf_generator import KerfParameters, generate_living_hinge


def main():
    """Generate a vertical living hinge pattern."""

    params = KerfParameters(
        material_width=200,         # mm - wider material
        material_height=100,        # mm - shorter material
        material_thickness=3,       # mm
        kerf_width=0.2,            # mm
        cut_spacing=6,             # mm between cuts
        cut_length=70,             # mm long cuts
        cut_offset=15,             # mm from edges
        pattern_direction='vertical',  # Vertical cuts
        material_name="3mm MDF",
        notes="Vertical pattern for cross-grain bending",
    )

    print(f"Generating vertical pattern...")
    print(f"  Material: {params.material_width}×{params.material_height}mm")
    print(f"  Cuts: {params.num_cuts} vertical cuts, {params.cut_length}mm long")
    print(f"  Bend radius: {params.bend_radius:.1f}mm")
    print()

    lines = generate_living_hinge(
        params,
        dxf_output="output/vertical_pattern.dxf",
        image_output="output/vertical_pattern.png",
    )

    print(f"✓ Generated {len(lines)} cuts")
    print("✓ Files saved to output/")


if __name__ == "__main__":
    main()
