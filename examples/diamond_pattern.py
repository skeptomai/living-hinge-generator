#!/usr/bin/env python3
"""
Elongated diamond pattern example for horizontal bending.

This example creates columns of tall, narrow diamonds alternating with
split diamonds (top V + gap + bottom inverted V) for superior stress
distribution compared to traditional straight cuts.
"""

from kerf_generator import KerfParameters, generate_living_hinge, print_pattern_info


def main():
    """Generate a diamond kerf pattern."""

    # Define pattern parameters
    # Elongated diamond pattern on 150x200mm material
    params = KerfParameters(
        material_width=150,         # mm
        material_height=200,        # mm
        material_thickness=3,       # mm plywood
        kerf_width=0.2,            # mm (typical CO2 laser on wood)
        cut_spacing=9,             # mm horizontal spacing between columns
        cut_length=12,             # mm diamond width
        cut_offset=10,             # mm from edges
        pattern_type='diamond',    # Elongated diamond pattern
        material_name="3mm Plywood",
        notes="Elongated vertical diamonds for horizontal bending",
    )

    # Print pattern information
    print("=" * 60)
    print("Generating Diamond Pattern")
    print("=" * 60)
    print()
    print_pattern_info(params)
    print()
    print("Elongated diamond patterns provide:")
    print("  • Horizontal bending flexibility (bends left-right)")
    print("  • Better stress distribution than straight cuts")
    print("  • Acute angles at top/bottom create defined hinge points")
    print("  • More durable under repeated bending")
    print()

    # Generate pattern and export to files
    print("Generating pattern and exporting...")
    lines = generate_living_hinge(
        params,
        dxf_output="output/diamond_pattern.dxf",
        image_output="output/diamond_pattern.png",
        svg_output="output/diamond_pattern.svg",
    )

    print(f"\n✓ Successfully generated {len(lines)} line segments")
    print("✓ DXF file saved to: output/diamond_pattern.dxf")
    print("✓ PNG preview saved to: output/diamond_pattern.png")
    print("✓ SVG file saved to: output/diamond_pattern.svg")
    print()
    print("You can now import the DXF file into Fusion 360 or Lightburn!")


if __name__ == "__main__":
    main()
