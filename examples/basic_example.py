#!/usr/bin/env python3
"""
Basic example of generating a living hinge pattern.

This example creates a simple horizontal living hinge pattern
and exports it to DXF and PNG formats.
"""

from kerf_generator import KerfParameters, generate_living_hinge, print_pattern_info


def main():
    """Generate a basic living hinge pattern."""

    # Define pattern parameters
    # This creates a pattern on 100x200mm material, 3mm thick
    params = KerfParameters(
        material_width=100,         # mm
        material_height=200,        # mm
        material_thickness=3,       # mm plywood
        kerf_width=0.2,            # mm (typical CO2 laser on wood)
        cut_spacing=5,             # mm between cuts
        cut_length=80,             # mm long cuts
        cut_offset=10,             # mm from edges
        pattern_direction='horizontal',
        material_name="3mm Plywood",
        notes="Basic test pattern",
    )

    # Print pattern information
    print("=" * 60)
    print("Generating Living Hinge Pattern")
    print("=" * 60)
    print()
    print_pattern_info(params)
    print()

    # Generate pattern and export to files
    print("Generating pattern and exporting...")
    lines = generate_living_hinge(
        params,
        dxf_output="output/basic_example.dxf",
        image_output="output/basic_example.png",
        svg_output="output/basic_example.svg",
    )

    print(f"\n✓ Successfully generated {len(lines)} cuts")
    print("✓ DXF file saved to: output/basic_example.dxf")
    print("✓ PNG preview saved to: output/basic_example.png")
    print("✓ SVG file saved to: output/basic_example.svg")
    print()
    print("You can now import the DXF file into Fusion 360 or Lightburn!")


if __name__ == "__main__":
    main()
