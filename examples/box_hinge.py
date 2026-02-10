#!/usr/bin/env python3
"""
Box hinge example - pattern for creating a hinged box lid.

This creates a pattern suitable for a box lid that needs to
bend 90-180 degrees.
"""

from kerf_generator import (
    KerfParameters,
    generate_living_hinge,
    print_pattern_info,
)


def main():
    """Generate a box hinge pattern."""

    # Box hinge specifications
    # - Box width: 150mm
    # - Material: 3mm plywood
    # - Target: Smooth 90° bend
    # - Calculate spacing for ~40mm bend radius

    params = KerfParameters(
        material_width=150,        # Box width
        material_height=80,        # Hinge height
        material_thickness=3,      # 3mm plywood
        kerf_width=0.2,           # Standard CO2 laser
        cut_spacing=6,            # Safe spacing for smooth bending
        cut_length=60,            # Length of each cut (leaves margins)
        cut_offset=10,            # Edge margin
        pattern_direction='horizontal',
        material_name="3mm Birch Plywood",
        notes="Box lid hinge - 90° bend capability"
    )

    print("=" * 70)
    print("BOX HINGE PATTERN GENERATOR")
    print("=" * 70)
    print()
    print_pattern_info(params)
    print()

    print("Design notes:")
    print(f"  • Pattern will allow ~{params.max_bend_angle:.0f}° maximum bend")
    print(f"  • Bend radius: {params.bend_radius:.1f}mm")
    print(f"  • Suitable for box lids and hinged panels")
    print(f"  • Apply pattern to the connection between lid and box body")
    print()

    # Generate and export
    lines = generate_living_hinge(
        params,
        dxf_output="output/box_hinge.dxf",
        image_output="output/box_hinge.png",
        svg_output="output/box_hinge.svg",
    )

    print(f"✓ Generated {len(lines)} cuts")
    print("✓ Exported: DXF, PNG, SVG")
    print()
    print("Usage instructions:")
    print("  1. Import DXF into Lightburn")
    print("  2. Position at the box lid/body junction")
    print("  3. Cuts should run perpendicular to the fold line")
    print("  4. Test bend before gluing box together!")


if __name__ == "__main__":
    main()
