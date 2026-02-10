#!/usr/bin/env python3
"""
Example showing tighter bend radius with closer spacing.

This demonstrates how reducing cut spacing allows tighter bending.
"""

from kerf_generator import (
    KerfParameters,
    generate_living_hinge,
    calculate_required_spacing,
)


def main():
    """Generate patterns with different bend radii."""

    # Material properties
    material_thickness = 3.0  # mm
    kerf_width = 0.25  # mm (slightly wider kerf)

    # Example 1: Tight bend (20mm radius)
    target_radius_1 = 20.0
    spacing_1 = calculate_required_spacing(target_radius_1, material_thickness, kerf_width)

    print(f"Target bend radius: {target_radius_1}mm")
    print(f"Required cut spacing: {spacing_1:.2f}mm")
    print()

    params_tight = KerfParameters(
        material_width=150,
        material_height=150,
        material_thickness=material_thickness,
        kerf_width=kerf_width,
        cut_spacing=spacing_1,
        cut_length=120,
        cut_offset=15,
        pattern_direction='horizontal',
        material_name="3mm Acrylic",
        notes=f"Tight radius: {target_radius_1}mm",
    )

    print(params_tight.summary())
    print()

    lines = generate_living_hinge(
        params_tight,
        dxf_output="output/tight_radius_20mm.dxf",
        image_output="output/tight_radius_20mm.png",
    )

    print(f"✓ Generated {len(lines)} cuts for {target_radius_1}mm radius")
    print(f"  Actual bend radius: {params_tight.bend_radius:.2f}mm")
    print()

    # Example 2: Larger bend (50mm radius)
    target_radius_2 = 50.0
    spacing_2 = calculate_required_spacing(target_radius_2, material_thickness, kerf_width)

    params_gentle = KerfParameters(
        material_width=150,
        material_height=150,
        material_thickness=material_thickness,
        kerf_width=kerf_width,
        cut_spacing=spacing_2,
        cut_length=120,
        cut_offset=15,
        pattern_direction='horizontal',
        material_name="3mm Acrylic",
        notes=f"Gentle radius: {target_radius_2}mm",
    )

    lines = generate_living_hinge(
        params_gentle,
        dxf_output="output/gentle_radius_50mm.dxf",
        image_output="output/gentle_radius_50mm.png",
    )

    print(f"✓ Generated {len(lines)} cuts for {target_radius_2}mm radius")
    print(f"  Actual bend radius: {params_gentle.bend_radius:.2f}mm")
    print()
    print("Compare the two PNG files to see the difference in cut density!")


if __name__ == "__main__":
    main()
