#!/usr/bin/env python3
"""
Pattern comparison example showing all three pattern types side-by-side.

This example generates living hinge, diamond, and oval patterns with
identical base parameters to demonstrate the visual and structural
differences between pattern types.
"""

from kerf_generator import KerfParameters, generate_living_hinge, print_pattern_info


def main():
    """Generate all three pattern types for comparison."""

    print("=" * 60)
    print("Generating Pattern Comparison")
    print("=" * 60)
    print()
    print("Creating three patterns with identical parameters:")
    print("  • Living Hinge (parallel cuts)")
    print("  • Diamond (interlocking diamonds)")
    print("  • Oval (interlocking ovals)")
    print()

    # Base parameters that will be used for all three patterns
    base_params = {
        'material_width': 150,
        'material_height': 200,
        'material_thickness': 3,
        'kerf_width': 0.2,
        'cut_spacing': 5,
        'cut_length': 10,
        'cut_offset': 10,
        'material_name': "3mm Plywood",
    }

    # Generate Living Hinge Pattern
    print("-" * 60)
    print("1. Living Hinge Pattern (Horizontal)")
    print("-" * 60)
    params_lh = KerfParameters(
        **base_params,
        pattern_type='living_hinge',
        pattern_direction='horizontal',
        notes="Traditional parallel cut pattern",
    )
    print_pattern_info(params_lh)
    print()

    lines_lh = generate_living_hinge(
        params_lh,
        dxf_output="output/comparison_living_hinge.dxf",
        image_output="output/comparison_living_hinge.png",
    )
    print(f"✓ Living hinge generated: {len(lines_lh)} line segments")
    print()

    # Generate Diamond Pattern
    print("-" * 60)
    print("2. Diamond Pattern")
    print("-" * 60)
    params_diamond = KerfParameters(
        **base_params,
        pattern_type='diamond',
        notes="Interlocking diamond pattern",
    )
    print_pattern_info(params_diamond)
    print()

    lines_diamond = generate_living_hinge(
        params_diamond,
        dxf_output="output/comparison_diamond.dxf",
        image_output="output/comparison_diamond.png",
    )
    print(f"✓ Diamond pattern generated: {len(lines_diamond)} line segments")
    print()

    # Generate Oval Pattern
    print("-" * 60)
    print("3. Oval Pattern")
    print("-" * 60)
    params_oval = KerfParameters(
        **base_params,
        pattern_type='oval',
        notes="Interlocking oval pattern",
    )
    print_pattern_info(params_oval)
    print()

    lines_oval = generate_living_hinge(
        params_oval,
        dxf_output="output/comparison_oval.dxf",
        image_output="output/comparison_oval.png",
    )
    print(f"✓ Oval pattern generated: {len(lines_oval)} line segments")
    print()

    # Summary
    print("=" * 60)
    print("Comparison Summary")
    print("=" * 60)
    print()
    print("Pattern Type       | Line Segments | Characteristics")
    print("-" * 60)
    print(f"Living Hinge      | {len(lines_lh):13d} | Unidirectional bending")
    print(f"Diamond           | {len(lines_diamond):13d} | Omnidirectional, durable")
    print(f"Oval              | {len(lines_oval):13d} | Smooth curves, aesthetic")
    print()
    print("Files saved to output/ directory with 'comparison_' prefix")
    print("Compare the PNG previews to see the visual differences!")
    print()
    print("Key differences:")
    print("  • Living Hinge: Best for single-axis bending (cylinders, tubes)")
    print("  • Diamond: Best for complex 3D shapes requiring multi-axis bending")
    print("  • Oval: Best for organic curves and aesthetic applications")


if __name__ == "__main__":
    main()
