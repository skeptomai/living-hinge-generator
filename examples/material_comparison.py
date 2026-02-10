#!/usr/bin/env python3
"""
Material comparison - generate test patterns for different materials.

This creates test patterns with various spacing to help determine
the best parameters for your specific material and laser setup.
"""

from kerf_generator import KerfParameters, generate_living_hinge


def generate_test_strip(material_name, thickness, kerf, spacing_list):
    """Generate multiple test patterns with different spacing."""

    print(f"\n{'='*60}")
    print(f"Test patterns for: {material_name} ({thickness}mm)")
    print(f"{'='*60}")

    for i, spacing in enumerate(spacing_list, 1):
        params = KerfParameters(
            material_width=80,         # Small test strips
            material_height=50,
            material_thickness=thickness,
            kerf_width=kerf,
            cut_spacing=spacing,
            cut_length=60,
            cut_offset=10,
            pattern_direction='horizontal',
            material_name=material_name,
            notes=f"Test strip {i}: {spacing}mm spacing"
        )

        base_name = f"test_{material_name.lower().replace(' ', '_')}_spacing_{spacing}mm"
        lines = generate_living_hinge(
            params,
            dxf_output=f"output/{base_name}.dxf",
            image_output=f"output/{base_name}.png",
        )

        print(f"  Test {i}: {spacing}mm spacing → {params.bend_radius:.1f}mm radius ({len(lines)} cuts)")


def main():
    """Generate test patterns for common materials."""

    print("\n" + "="*60)
    print("MATERIAL TEST PATTERN GENERATOR")
    print("="*60)
    print("\nGenerating test strips for material calibration...")
    print("Cut these and test the flexibility to find optimal spacing.")

    # 3mm Plywood test
    generate_test_strip(
        material_name="3mm Plywood",
        thickness=3.0,
        kerf=0.2,
        spacing_list=[4, 5, 6, 8]  # Range from tight to gentle
    )

    # 3mm Acrylic test
    generate_test_strip(
        material_name="3mm Acrylic",
        thickness=3.0,
        kerf=0.25,  # Acrylic often has wider kerf
        spacing_list=[3, 4, 5, 6]
    )

    # 6mm MDF test
    generate_test_strip(
        material_name="6mm MDF",
        thickness=6.0,
        kerf=0.3,
        spacing_list=[8, 10, 12, 15]  # Wider spacing for thicker material
    )

    print("\n" + "="*60)
    print("TEST PATTERN GENERATION COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("  1. Load all test DXF files into Lightburn")
    print("  2. Arrange on your material sheet")
    print("  3. Cut all test strips")
    print("  4. Test flexibility and strength of each")
    print("  5. Note which spacing works best for your needs")
    print("  6. Use that spacing in your final designs!")
    print()


if __name__ == "__main__":
    main()
