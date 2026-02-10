#!/usr/bin/env python3
"""
Lamp shade example - create a bendable panel for cylindrical lamp shade.

This pattern allows flat material to wrap into a cylinder,
useful for lamp shades, curved panels, etc.
"""

from kerf_generator import (
    KerfParameters,
    generate_living_hinge,
    calculate_required_spacing,
)
import math


def main():
    """Generate a lamp shade pattern."""

    # Lamp shade specifications
    target_diameter = 100  # mm - desired lamp diameter
    target_radius = target_diameter / 2
    material_thickness = 3  # mm
    kerf_width = 0.25  # mm (acrylic typically has wider kerf)

    # Calculate required spacing for this radius
    spacing = calculate_required_spacing(
        target_bend_radius=target_radius,
        material_thickness=material_thickness,
        kerf_width=kerf_width
    )

    # Calculate circumference
    circumference = 2 * math.pi * target_radius
    height = 150  # mm

    print("=" * 70)
    print("LAMP SHADE PATTERN GENERATOR")
    print("=" * 70)
    print()
    print(f"Target diameter: {target_diameter}mm")
    print(f"Bend radius: {target_radius}mm")
    print(f"Calculated spacing: {spacing:.2f}mm")
    print(f"Material circumference needed: {circumference:.1f}mm")
    print(f"Height: {height}mm")
    print()

    params = KerfParameters(
        material_width=int(circumference) + 20,  # Add margin for overlap
        material_height=height,
        material_thickness=material_thickness,
        kerf_width=kerf_width,
        cut_spacing=spacing,
        cut_length=height - 30,  # Leave margins
        cut_offset=15,
        pattern_direction='vertical',  # Vertical cuts for cylindrical wrapping
        material_name="3mm Clear Acrylic",
        notes=f"Lamp shade for {target_diameter}mm diameter"
    )

    print(f"Pattern properties:")
    print(f"  Material size: {params.material_width} × {params.material_height}mm")
    print(f"  Number of cuts: {params.num_cuts}")
    print(f"  Actual bend radius: {params.bend_radius:.1f}mm")
    print()

    lines = generate_living_hinge(
        params,
        dxf_output="output/lamp_shade.dxf",
        image_output="output/lamp_shade.png",
    )

    print(f"✓ Generated {len(lines)} cuts")
    print(f"✓ Total cut length: {sum(line.length for line in lines):.0f}mm")
    print()
    print("Assembly instructions:")
    print("  1. Cut the pattern from clear or translucent acrylic")
    print("  2. Gently bend into cylinder shape")
    print("  3. Overlap the ends and glue/tape together")
    print("  4. Add LED strip or bulb holder inside")
    print("  5. The kerf cuts will create interesting light patterns!")


if __name__ == "__main__":
    main()
