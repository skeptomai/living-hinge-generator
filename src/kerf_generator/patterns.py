"""
Pattern generation for kerf cutting.

This module generates the geometric patterns (arrays of line segments)
for various kerf cutting techniques.
"""

from typing import List
from .parameters import KerfParameters, LineSegment


def generate_living_hinge(params: KerfParameters) -> List[LineSegment]:
    """
    Generate a living hinge pattern with parallel cuts.

    Creates an array of parallel cuts oriented according to pattern_direction.
    - Horizontal: cuts run horizontally (left-right), spaced vertically
    - Vertical: cuts run vertically (top-bottom), spaced horizontally

    Args:
        params: KerfParameters defining the pattern

    Returns:
        List of LineSegment objects representing the cuts

    Example:
        >>> params = KerfParameters(
        ...     material_width=100, material_height=200,
        ...     material_thickness=3, kerf_width=0.2,
        ...     cut_spacing=5, cut_length=80, cut_offset=10,
        ...     pattern_direction='horizontal'
        ... )
        >>> lines = generate_living_hinge(params)
        >>> len(lines)
        39
    """
    lines: List[LineSegment] = []

    if params.pattern_direction == "horizontal":
        lines = _generate_horizontal_cuts(params)
    elif params.pattern_direction == "vertical":
        lines = _generate_vertical_cuts(params)
    else:
        raise ValueError(
            f"Invalid pattern direction: {params.pattern_direction}. "
            "Must be 'horizontal' or 'vertical'."
        )

    return lines


def _generate_horizontal_cuts(params: KerfParameters) -> List[LineSegment]:
    """
    Generate horizontal cuts (left-right orientation, spaced top-bottom).

    Cuts are centered horizontally on the material with cut_offset on left and right.
    Cuts are spaced vertically starting from cut_offset from the top.

    Args:
        params: KerfParameters defining the pattern

    Returns:
        List of LineSegment objects
    """
    lines: List[LineSegment] = []

    # Calculate horizontal positioning (where cuts start and end)
    # Cuts are centered on the material width
    available_width = params.material_width - (2 * params.cut_offset)
    cut_start_x = params.cut_offset + (available_width - params.cut_length) / 2
    cut_end_x = cut_start_x + params.cut_length

    # Calculate how many cuts fit vertically
    available_height = params.material_height - (2 * params.cut_offset)
    num_cuts = int(available_height / params.cut_spacing) + 1

    # Generate cuts from top to bottom
    for i in range(num_cuts):
        y = params.cut_offset + (i * params.cut_spacing)

        # Don't create cuts that extend beyond material bounds
        if y > params.material_height - params.cut_offset:
            break

        line = LineSegment(
            x1=cut_start_x,
            y1=y,
            x2=cut_end_x,
            y2=y,
            layer="cuts",
        )
        lines.append(line)

    return lines


def _generate_vertical_cuts(params: KerfParameters) -> List[LineSegment]:
    """
    Generate vertical cuts (top-bottom orientation, spaced left-right).

    Cuts are centered vertically on the material with cut_offset on top and bottom.
    Cuts are spaced horizontally starting from cut_offset from the left.

    Args:
        params: KerfParameters defining the pattern

    Returns:
        List of LineSegment objects
    """
    lines: List[LineSegment] = []

    # Calculate vertical positioning (where cuts start and end)
    # Cuts are centered on the material height
    available_height = params.material_height - (2 * params.cut_offset)
    cut_start_y = params.cut_offset + (available_height - params.cut_length) / 2
    cut_end_y = cut_start_y + params.cut_length

    # Calculate how many cuts fit horizontally
    available_width = params.material_width - (2 * params.cut_offset)
    num_cuts = int(available_width / params.cut_spacing) + 1

    # Generate cuts from left to right
    for i in range(num_cuts):
        x = params.cut_offset + (i * params.cut_spacing)

        # Don't create cuts that extend beyond material bounds
        if x > params.material_width - params.cut_offset:
            break

        line = LineSegment(
            x1=x,
            y1=cut_start_y,
            x2=x,
            y2=cut_end_y,
            layer="cuts",
        )
        lines.append(line)

    return lines


def generate_outline(params: KerfParameters) -> List[LineSegment]:
    """
    Generate outline rectangle for the material boundary.

    Creates a closed rectangle representing the material edges.
    Useful for DXF export and preview visualization.

    Args:
        params: KerfParameters defining the material dimensions

    Returns:
        List of 4 LineSegment objects forming a rectangle
    """
    outline = [
        # Bottom edge
        LineSegment(0, 0, params.material_width, 0, layer="outline"),
        # Right edge
        LineSegment(params.material_width, 0, params.material_width, params.material_height, layer="outline"),
        # Top edge
        LineSegment(params.material_width, params.material_height, 0, params.material_height, layer="outline"),
        # Left edge
        LineSegment(0, params.material_height, 0, 0, layer="outline"),
    ]

    return outline


def get_pattern_bounds(lines: List[LineSegment]) -> tuple[float, float, float, float]:
    """
    Calculate the bounding box of a pattern.

    Args:
        lines: List of LineSegment objects

    Returns:
        Tuple of (min_x, min_y, max_x, max_y)
    """
    if not lines:
        return (0.0, 0.0, 0.0, 0.0)

    min_x = min(min(line.x1, line.x2) for line in lines)
    max_x = max(max(line.x1, line.x2) for line in lines)
    min_y = min(min(line.y1, line.y2) for line in lines)
    max_y = max(max(line.y1, line.y2) for line in lines)

    return (min_x, min_y, max_x, max_y)


def pattern_statistics(lines: List[LineSegment]) -> dict:
    """
    Calculate statistics about a generated pattern.

    Args:
        lines: List of LineSegment objects

    Returns:
        Dictionary with pattern statistics
    """
    if not lines:
        return {
            "num_cuts": 0,
            "total_cut_length": 0.0,
            "avg_cut_length": 0.0,
            "bounds": (0, 0, 0, 0),
        }

    total_length = sum(line.length for line in lines)
    avg_length = total_length / len(lines) if lines else 0.0
    bounds = get_pattern_bounds(lines)

    return {
        "num_cuts": len(lines),
        "total_cut_length": total_length,
        "avg_cut_length": avg_length,
        "bounds": bounds,
    }
