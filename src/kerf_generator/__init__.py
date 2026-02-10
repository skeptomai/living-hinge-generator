"""
Kerf Generator - Python library for generating kerf cutting patterns.

This library generates living hinge patterns for laser cutting, with export
to DXF (for CAD/Lightburn) and image formats (for preview).

Basic usage:
    >>> from kerf_generator import KerfParameters, generate_living_hinge
    >>> params = KerfParameters(
    ...     material_width=100,
    ...     material_height=200,
    ...     material_thickness=3,
    ...     kerf_width=0.2,
    ...     cut_spacing=5,
    ...     cut_length=80,
    ...     cut_offset=10,
    ...     pattern_direction='horizontal'
    ... )
    >>> lines = generate_living_hinge(
    ...     params,
    ...     dxf_output="pattern.dxf",
    ...     image_output="pattern.png"
    ... )
"""

from pathlib import Path
from typing import List, Optional

from .parameters import KerfParameters, LineSegment
from .patterns import (
    generate_living_hinge as _generate_pattern,
    generate_outline,
    pattern_statistics,
)
from .exporters import export_dxf, export_image, export_svg, export_all
from .geometry import (
    calculate_bend_radius,
    calculate_required_spacing,
    calculate_max_bend_angle,
    calculate_minimum_spacing,
)

__version__ = "0.1.0"

__all__ = [
    # Main API
    "generate_living_hinge",
    "KerfParameters",
    "LineSegment",
    # Export functions
    "export_dxf",
    "export_image",
    "export_svg",
    "export_all",
    # Pattern utilities
    "generate_outline",
    "pattern_statistics",
    # Geometry calculations
    "calculate_bend_radius",
    "calculate_required_spacing",
    "calculate_max_bend_angle",
    "calculate_minimum_spacing",
]


def generate_living_hinge(
    params: KerfParameters,
    dxf_output: Optional[str | Path] = None,
    image_output: Optional[str | Path] = None,
    svg_output: Optional[str | Path] = None,
) -> List[LineSegment]:
    """
    Generate a living hinge pattern and optionally export to files.

    This is the main high-level API function. It generates the pattern
    and can automatically export to DXF, image, and/or SVG formats.

    Args:
        params: KerfParameters object defining the pattern
        dxf_output: Optional path to save DXF file
        image_output: Optional path to save PNG/image preview
        svg_output: Optional path to save SVG file

    Returns:
        List of LineSegment objects representing the generated cuts

    Example:
        >>> params = KerfParameters(
        ...     material_width=100, material_height=200,
        ...     material_thickness=3, kerf_width=0.2,
        ...     cut_spacing=5, cut_length=80, cut_offset=10,
        ...     pattern_direction='horizontal'
        ... )
        >>> lines = generate_living_hinge(
        ...     params,
        ...     dxf_output="output/pattern.dxf",
        ...     image_output="output/pattern.png"
        ... )
        >>> print(f"Generated {len(lines)} cuts")
    """
    # Generate the pattern
    lines = _generate_pattern(params)

    # Export if output paths provided
    if dxf_output:
        export_dxf(lines, params, dxf_output)

    if image_output:
        export_image(lines, params, image_output)

    if svg_output:
        export_svg(lines, params, svg_output)

    return lines


def print_pattern_info(params: KerfParameters, lines: Optional[List[LineSegment]] = None) -> None:
    """
    Print detailed information about a pattern.

    Args:
        params: KerfParameters object
        lines: Optional list of generated LineSegments (will generate if not provided)

    Example:
        >>> params = KerfParameters(...)
        >>> print_pattern_info(params)
    """
    print(params.summary())

    if lines is None:
        lines = _generate_pattern(params)

    print("\nPattern Statistics:")
    stats = pattern_statistics(lines)
    print(f"  Actual number of cuts: {stats['num_cuts']}")
    print(f"  Total cut length: {stats['total_cut_length']:.2f} mm")
    print(f"  Average cut length: {stats['avg_cut_length']:.2f} mm")
    print(f"  Pattern bounds: {stats['bounds']}")
