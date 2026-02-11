#!/usr/bin/env python3
"""
Elongated oval pattern example for smooth horizontal bending.

This example creates columns of tall, narrow ovals alternating with
split ovals (top arc + gap + bottom arc) for smooth bending curves
without stress concentration points.
"""

from kerf_generator import KerfParameters, generate_living_hinge, print_pattern_info


def main():
    """Generate a pointed oval kerf pattern."""

    # Define pattern parameters
    # Elongated oval pattern on 150x200mm material
    params = KerfParameters(
        material_width=150,         # mm
        material_height=200,        # mm
        material_thickness=3,       # mm plywood
        kerf_width=0.2,            # mm (typical CO2 laser on wood)
        cut_spacing=9,             # mm horizontal spacing between columns
        cut_length=12,             # mm oval width
        cut_offset=10,             # mm from edges
        pattern_type='oval',       # Elongated oval pattern
        material_name="3mm Plywood",
        notes="Elongated vertical ovals for smooth horizontal bending",
    )

    # Print pattern information
    print("=" * 60)
    print("Generating Pointed Oval Pattern")
    print("=" * 60)
    print()
    print_pattern_info(params)
    print()
    print("Oval patterns provide:")
    print("  • Smooth bending curves with no stress concentration")
    print("  • Directional flexibility (easier bending along major axis)")
    print("  • Visually appealing organic appearance")
    print("  • Good balance of flexibility and strength")
    print()

    # Generate pattern and export to files
    print("Generating pattern and exporting...")
    lines = generate_living_hinge(
        params,
        dxf_output="output/oval_pattern.dxf",
        image_output="output/oval_pattern.png",
        svg_output="output/oval_pattern.svg",
    )

    print(f"\n✓ Successfully generated {len(lines)} line segments")
    print("✓ DXF file saved to: output/oval_pattern.dxf")
    print("✓ PNG preview saved to: output/oval_pattern.png")
    print("✓ SVG file saved to: output/oval_pattern.svg")
    print()
    print("You can now import the DXF file into Fusion 360 or Lightburn!")


if __name__ == "__main__":
    main()
