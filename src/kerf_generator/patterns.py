"""
Pattern generation for kerf cutting.

This module generates the geometric patterns (arrays of line segments)
for various kerf cutting techniques.
"""

import math
from typing import List
from .parameters import KerfParameters, LineSegment


def generate_living_hinge(params: KerfParameters) -> List[LineSegment]:
    """
    Generate kerf pattern based on pattern_type.

    Dispatcher function that routes to the appropriate pattern generator based on
    the pattern_type in params.

    Args:
        params: KerfParameters defining the pattern

    Returns:
        List of LineSegment objects representing the cuts

    Raises:
        ValueError: If pattern_type is not recognized

    Example:
        >>> params = KerfParameters(
        ...     material_width=100, material_height=200,
        ...     material_thickness=3, kerf_width=0.2,
        ...     cut_spacing=5, cut_length=80, cut_offset=10,
        ...     pattern_direction='horizontal',
        ...     pattern_type='living_hinge'
        ... )
        >>> lines = generate_living_hinge(params)
        >>> len(lines)
        39
    """
    if params.pattern_type == "straight":
        return _generate_straight_cut_pattern(params)
    elif params.pattern_type == "diamond":
        return _generate_diamond_pattern(params)
    elif params.pattern_type == "oval":
        return _generate_oval_pattern(params)
    else:
        raise ValueError(f"Unknown pattern_type: {params.pattern_type}")


def _generate_straight_cut_pattern(params: KerfParameters) -> List[LineSegment]:
    """
    Generate a straight cut pattern with parallel cuts.

    Creates an array of parallel cuts oriented according to pattern_direction.
    - Horizontal: cuts run horizontally (left-right), spaced vertically
    - Vertical: cuts run vertically (top-bottom), spaced horizontally

    Args:
        params: KerfParameters defining the pattern

    Returns:
        List of LineSegment objects representing the cuts
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


def _generate_diamond_pattern(params: KerfParameters) -> List[LineSegment]:
    """
    Generate elongated vertical diamond pattern in columns.

    Creates alternating columns of:
    - Even columns: Full elongated diamonds (tall, narrow, nearly full height)
    - Odd columns: Split diamonds (top V + gap + bottom inverted V)

    For tall materials, patterns can be stacked vertically in multiple rows
    for better flexibility control and structural integrity.

    Args:
        params: KerfParameters defining the pattern
            - cut_length: Width of diamonds
            - cut_spacing: Horizontal spacing between columns
            - material_height: Determines diamond height (uses ~80% of available height per row)
            - num_vertical_rows: Number of rows to stack (None = auto-calculate)

    Returns:
        List of LineSegment objects representing the diamond cuts
    """
    lines: List[LineSegment] = []

    diamond_width = params.cut_length
    spacing = params.cut_spacing
    offset = params.cut_offset

    # Available space
    # For horizontal fill, use minimal horizontal offset (just a small margin)
    horizontal_margin = diamond_width * 0.15  # Small margin on sides
    available_width = params.material_width - (2 * horizontal_margin)
    total_available_height = params.material_height - (2 * offset)

    if available_width <= 0 or total_available_height <= 0:
        return lines

    # Determine number of vertical rows
    num_rows = params.effective_num_rows

    # Calculate row configuration
    row_gap = 2.0  # Small gap between rows (mm)
    total_gap_height = (num_rows - 1) * row_gap if num_rows > 1 else 0
    row_height = (total_available_height - total_gap_height) / num_rows

    # Calculate number of columns
    num_cols = int(available_width / spacing) + 1

    # Generate pattern for each row
    for row_idx in range(num_rows):
        # Calculate this row's vertical position
        # First row starts at 0 (bottom edge), last row ends at material_height (top edge)
        is_first_row = (row_idx == 0)
        is_last_row = (row_idx == num_rows - 1)

        if is_first_row:
            row_y_start = 0  # Start at material bottom edge
        else:
            row_y_start = offset + (row_idx * (row_height + row_gap))

        # Calculate actual row height for this row
        if is_first_row and is_last_row:
            # Single row: use full material height
            actual_row_height = params.material_height
        elif is_first_row:
            # First row: extend to bottom edge
            actual_row_height = offset + row_height
        elif is_last_row:
            # Last row: extend to top edge
            actual_row_height = params.material_height - row_y_start
        else:
            # Middle rows: use calculated row height
            actual_row_height = row_height

        # Calculate diamond heights for this row
        # Full diamonds: almost no inset from top/bottom of row (~1%)
        full_diamond_height = actual_row_height * 0.98
        full_diamond_inset = actual_row_height * 0.01

        # Split diamonds: extend to actual row edges
        # Very narrow gap in middle (10%) for tight pattern
        split_gap_ratio = 0.10  # 10% gap
        split_total_height = actual_row_height
        split_gap = split_total_height * split_gap_ratio
        split_v_height = (split_total_height - split_gap) / 2

        # Generate columns for this row
        for col in range(num_cols):
            col_x = horizontal_margin + (col * spacing)

            # Stop if we exceed material bounds (with small margin)
            if col_x + diamond_width > params.material_width - horizontal_margin:
                break

            # Use same narrow width for both types
            narrow_width = diamond_width * 0.35  # 35% width for both

            if col % 2 == 0:
                # Even column: Split diamond extending to actual row edges
                lines.extend(_create_split_diamond_with_gap(
                    col_x + (diamond_width - narrow_width) / 2,
                    row_y_start,
                    narrow_width,
                    split_total_height,
                    split_v_height,
                    split_gap
                ))
            else:
                # Odd column: Full elongated diamond (very narrow, minimal inset)
                lines.extend(_create_full_elongated_diamond(
                    col_x + (diamond_width - narrow_width) / 2,
                    row_y_start + full_diamond_inset,
                    narrow_width,
                    full_diamond_height
                ))

    return lines


def _create_full_elongated_diamond(x: float, y: float, width: float, height: float) -> List[LineSegment]:
    """
    Create a full elongated diamond shape (tall and narrow).

    Creates a diamond that stretches vertically with acute angles at top and bottom.

    Args:
        x: Left x-coordinate of diamond
        y: Bottom y-coordinate (starting point)
        width: Width of diamond at its widest point
        height: Total height of diamond

    Returns:
        List of 4 LineSegment objects forming an elongated diamond
    """
    # Diamond vertices (very tall and narrow)
    center_x = x + width / 2
    mid_y = y + height / 2

    top = (center_x, y + height)      # Top point
    right = (x + width, mid_y)        # Right widest point (middle)
    bottom = (center_x, y)            # Bottom point
    left = (x, mid_y)                 # Left widest point (middle)

    return [
        LineSegment(bottom[0], bottom[1], left[0], left[1], layer="cuts"),    # Bottom to left
        LineSegment(left[0], left[1], top[0], top[1], layer="cuts"),          # Left to top
        LineSegment(top[0], top[1], right[0], right[1], layer="cuts"),        # Top to right
        LineSegment(right[0], right[1], bottom[0], bottom[1], layer="cuts"),  # Right to bottom
    ]


def _create_split_diamond(x: float, y: float, width: float, height: float, gap: float) -> List[LineSegment]:
    """
    Create a split diamond with top V (apex down) and bottom inverted V (apex up).

    Each V is approximately half the total height with a gap in the middle for stability.

    Args:
        x: Left x-coordinate of diamond
        y: Bottom y-coordinate (starting point)
        width: Width of diamond at its widest point
        height: Total height that would be occupied if it were a full diamond
        gap: Size of gap between the two V shapes

    Returns:
        List of 4 LineSegment objects (2 for top V, 2 for bottom inverted V)
    """
    center_x = x + width / 2

    # Each V shape occupies half the total height
    v_height = height / 2

    # Top V shape (apex pointing DOWN)
    # Wide at the top, narrows to a point going downward
    top_left = (x, y + height)  # Left point at very top
    top_right = (x + width, y + height)  # Right point at very top
    top_apex = (center_x, y + height - v_height)  # Apex points down

    # Bottom inverted V shape (apex pointing UP)
    # Starts at a point, widens going downward
    bottom_apex = (center_x, y + v_height)  # Apex points up
    bottom_left = (x, y)  # Left point at very bottom
    bottom_right = (x + width, y)  # Right point at very bottom

    return [
        # Top V (apex pointing down) - left to apex, apex to right
        LineSegment(top_left[0], top_left[1], top_apex[0], top_apex[1], layer="cuts"),
        LineSegment(top_apex[0], top_apex[1], top_right[0], top_right[1], layer="cuts"),
        # Bottom inverted V (apex pointing up) - left to apex, apex to right
        LineSegment(bottom_left[0], bottom_left[1], bottom_apex[0], bottom_apex[1], layer="cuts"),
        LineSegment(bottom_apex[0], bottom_apex[1], bottom_right[0], bottom_right[1], layer="cuts"),
    ]


def _create_split_diamond_with_gap(x: float, y: float, width: float, total_height: float, v_height: float, gap: float) -> List[LineSegment]:
    """
    Create a split diamond with specified V heights and gap.

    Top V opens at the very top, bottom inverted V opens at the very bottom,
    with a gap in the middle for stability.

    Args:
        x: Left x-coordinate of diamond
        y: Bottom y-coordinate (starting point)
        width: Width of diamond at its widest point
        total_height: Total height of the material region
        v_height: Height of each V shape
        gap: Size of gap between the two V shapes

    Returns:
        List of 4 LineSegment objects (2 for top V, 2 for bottom inverted V)
    """
    center_x = x + width / 2

    # Top V shape (apex pointing DOWN)
    # Opens wide at the very top of material region
    top_left = (x, y + total_height)  # Left point at very top
    top_right = (x + width, y + total_height)  # Right point at very top
    top_apex = (center_x, y + total_height - v_height)  # Apex points down

    # Bottom inverted V shape (apex pointing UP)
    # Opens wide at the very bottom of material region
    bottom_apex = (center_x, y + v_height)  # Apex points up
    bottom_left = (x, y)  # Left point at very bottom
    bottom_right = (x + width, y)  # Right point at very bottom

    return [
        # Top V (apex pointing down) - left to apex, apex to right
        LineSegment(top_left[0], top_left[1], top_apex[0], top_apex[1], layer="cuts"),
        LineSegment(top_apex[0], top_apex[1], top_right[0], top_right[1], layer="cuts"),
        # Bottom inverted V (apex pointing up) - left to apex, apex to right
        LineSegment(bottom_left[0], bottom_left[1], bottom_apex[0], bottom_apex[1], layer="cuts"),
        LineSegment(bottom_apex[0], bottom_apex[1], bottom_right[0], bottom_right[1], layer="cuts"),
    ]


def _generate_oval_pattern(params: KerfParameters) -> List[LineSegment]:
    """
    Generate elongated vertical oval pattern in columns.

    Creates alternating columns of:
    - Even columns: Full elongated ovals (tall, narrow, nearly full height)
    - Odd columns: Split ovals (top arc + gap + bottom arc)

    For tall materials, patterns can be stacked vertically in multiple rows
    for better flexibility control and structural integrity.

    This pattern allows the material to bend horizontally while providing
    smooth curves that distribute stress better than straight cuts.

    Args:
        params: KerfParameters defining the pattern
            - cut_length: Width of ovals
            - cut_spacing: Horizontal spacing between columns
            - material_height: Determines oval height (uses ~80% of available height per row)
            - num_vertical_rows: Number of rows to stack (None = auto-calculate)

    Returns:
        List of LineSegment objects representing the oval cuts
    """
    lines: List[LineSegment] = []

    oval_width = params.cut_length
    spacing = params.cut_spacing
    offset = params.cut_offset

    # Available space
    available_width = params.material_width - (2 * offset)
    total_available_height = params.material_height - (2 * offset)

    if available_width <= 0 or total_available_height <= 0:
        return lines

    # Determine number of vertical rows
    num_rows = params.effective_num_rows

    # Calculate row configuration
    row_gap = 2.0  # Small gap between rows (mm)
    total_gap_height = (num_rows - 1) * row_gap if num_rows > 1 else 0
    row_height = (total_available_height - total_gap_height) / num_rows

    # Calculate number of columns
    num_cols = int(available_width / spacing) + 1

    # Generate pattern for each row
    for row_idx in range(num_rows):
        # Calculate this row's vertical position
        # First row starts at 0 (bottom edge), last row ends at material_height (top edge)
        is_first_row = (row_idx == 0)
        is_last_row = (row_idx == num_rows - 1)

        if is_first_row:
            row_y_start = 0  # Start at material bottom edge
        else:
            row_y_start = offset + (row_idx * (row_height + row_gap))

        # Calculate actual row height for this row
        if is_first_row and is_last_row:
            # Single row: use full material height
            actual_row_height = params.material_height
        elif is_first_row:
            # First row: extend to bottom edge
            actual_row_height = offset + row_height
        elif is_last_row:
            # Last row: extend to top edge
            actual_row_height = params.material_height - row_y_start
        else:
            # Middle rows: use calculated row height
            actual_row_height = row_height

        # Calculate oval height for this row (use ~80% of row height)
        oval_height = actual_row_height * 0.8

        # Gap for split ovals (space between top arc and bottom arc)
        split_gap = oval_height * 0.3

        # Generate columns for this row
        for col in range(num_cols):
            col_x = offset + (col * spacing)

            # Stop if we exceed material bounds
            if col_x + oval_width > params.material_width - offset:
                break

            # Center x position for oval
            center_x = col_x + oval_width / 2

            if col % 2 == 0:
                # Even column: Full elongated oval
                lines.extend(_create_full_elongated_oval(
                    center_x, row_y_start, oval_width, oval_height
                ))
            else:
                # Odd column: Split oval (top arc + bottom arc)
                lines.extend(_create_split_oval(
                    center_x, row_y_start, oval_width, oval_height, split_gap
                ))

    return lines


def _create_full_elongated_oval(center_x: float, y: float, width: float, height: float, num_segments: int = 20) -> List[LineSegment]:
    """
    Create a full elongated oval shape (tall and narrow).

    Uses parametric ellipse equation with vertical major axis.

    Args:
        center_x: X-coordinate of oval center (horizontal)
        y: Bottom y-coordinate (starting point)
        width: Width of oval (minor axis, horizontal)
        height: Height of oval (major axis, vertical)
        num_segments: Number of line segments to approximate the oval (default: 20)

    Returns:
        List of LineSegment objects forming an elongated oval
    """
    lines = []
    a = width / 2   # Semi-minor axis (horizontal)
    b = height / 2  # Semi-major axis (vertical)
    center_y = y + height / 2

    # Generate points around the ellipse
    points = []
    for i in range(num_segments):
        theta = (2 * math.pi * i) / num_segments
        x = center_x + a * math.cos(theta)
        y_point = center_y + b * math.sin(theta)
        points.append((x, y_point))

    # Connect consecutive points
    for i in range(num_segments):
        p1 = points[i]
        p2 = points[(i + 1) % num_segments]  # Wrap around to close the shape
        lines.append(LineSegment(p1[0], p1[1], p2[0], p2[1], layer="cuts"))

    return lines


def _create_split_oval(center_x: float, y: float, width: float, height: float, gap: float, num_segments: int = 10) -> List[LineSegment]:
    """
    Create a split oval with top arc and bottom arc separated by a gap.

    Args:
        center_x: X-coordinate of oval center (horizontal)
        y: Bottom y-coordinate (starting point)
        width: Width of oval (minor axis, horizontal)
        height: Total height that would be occupied if it were a full oval
        gap: Size of gap between top arc and bottom arc
        num_segments: Number of line segments for each arc (default: 10)

    Returns:
        List of LineSegment objects forming split oval (top arc + bottom arc)
    """
    lines = []
    a = width / 2   # Semi-minor axis (horizontal)

    # Top arc parameters
    top_arc_height = (height - gap) / 2
    b_top = top_arc_height / 2
    center_y_top = y + height - top_arc_height / 2

    # Generate points along top arc (from π to 2π, creating top curve)
    points_top = []
    for i in range(num_segments + 1):
        theta = math.pi + (math.pi * i) / num_segments
        x = center_x + a * math.cos(theta)
        y_point = center_y_top + b_top * math.sin(theta)
        points_top.append((x, y_point))

    # Connect consecutive points for top arc
    for i in range(len(points_top) - 1):
        p1 = points_top[i]
        p2 = points_top[i + 1]
        lines.append(LineSegment(p1[0], p1[1], p2[0], p2[1], layer="cuts"))

    # Bottom arc parameters
    bottom_arc_height = (height - gap) / 2
    b_bottom = bottom_arc_height / 2
    center_y_bottom = y + bottom_arc_height / 2

    # Generate points along bottom arc (from 0 to π, creating bottom curve)
    points_bottom = []
    for i in range(num_segments + 1):
        theta = (math.pi * i) / num_segments
        x = center_x + a * math.cos(theta)
        y_point = center_y_bottom + b_bottom * math.sin(theta)
        points_bottom.append((x, y_point))

    # Connect consecutive points for bottom arc
    for i in range(len(points_bottom) - 1):
        p1 = points_bottom[i]
        p2 = points_bottom[i + 1]
        lines.append(LineSegment(p1[0], p1[1], p2[0], p2[1], layer="cuts"))

    return lines


def generate_outline(params: KerfParameters) -> List[LineSegment]:
    """
    Generate outline rectangle for the material boundary.

    Creates a closed rectangle representing the material edges.
    For diamond/oval patterns, top and bottom edges use "cuts" layer
    to cut through the open ends of split shapes at the material edges.

    Args:
        params: KerfParameters defining the material dimensions

    Returns:
        List of 4 LineSegment objects forming a rectangle
    """
    # For diamond/oval patterns, top and bottom edges need to cut through split shapes
    needs_cutting_edges = params.pattern_type in ["diamond", "oval"]
    horizontal_layer = "cuts" if needs_cutting_edges else "outline"

    outline = [
        # Bottom edge (cuts layer for diamond/oval to close split shapes)
        LineSegment(0, 0, params.material_width, 0, layer=horizontal_layer),
        # Right edge (outline layer)
        LineSegment(params.material_width, 0, params.material_width, params.material_height, layer="outline"),
        # Top edge (cuts layer for diamond/oval to close split shapes)
        LineSegment(params.material_width, params.material_height, 0, params.material_height, layer=horizontal_layer),
        # Left edge (outline layer)
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
