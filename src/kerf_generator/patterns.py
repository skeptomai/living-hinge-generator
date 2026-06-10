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
        lines = _generate_straight_cut_pattern(params)
    elif params.pattern_type == "diamond":
        lines = _generate_diamond_pattern(params)
    elif params.pattern_type == "oval":
        lines = _generate_oval_pattern(params)
    else:
        raise ValueError(f"Unknown pattern_type: {params.pattern_type}")

    return _clip_lines_to_bounds(lines, 0, 0, params.material_width, params.material_height)


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
    Generate staggered horizontal cut pattern producing diamond-shaped voids.

    Creates rows of horizontal rhombus cuts. Adjacent rows are offset by half the
    period. Even rows begin with a half-diamond clipped at the left edge (x=0),
    ensuring cuts reach the bending edge. Odd rows start at period/2 (a small tab
    from the left). Both even and odd rows clip at the right edge as needed.

    Layout:
        Row 0 (even): half-diamond at x=0, full diamonds, [half at x=W]
        Row 1 (odd):  full diamonds from x=period/2, [half at x=W]
        Row 2 (even): same as row 0, etc.

    Where:
        period = cut_length + cut_spacing

    Args:
        params: KerfParameters defining the pattern
            - cut_length:  horizontal span of each diamond (mm)
            - cut_spacing: row pitch AND horizontal tab width (mm)

    Returns:
        List of LineSegment objects representing the cut lines
    """
    lines: List[LineSegment] = []

    cut_len = params.cut_length
    tab_width = params.cut_spacing
    period = cut_len + tab_width

    W = params.material_width
    H = params.material_height

    num_rows = max(1, round(H / params.effective_row_spacing))
    row_spacing = H / num_rows
    diamond_height = row_spacing * 0.90

    # Center the grid: split leftover space equally on both sides so left and
    # right edge clips are symmetric.
    offset = (W % period) / 2

    # Don't place rows so close to the top/bottom that they'd produce tiny slivers.
    y_margin = diamond_height / 4

    for row_idx in range(num_rows + 1):
        y = row_idx * row_spacing
        if y > H + 1e-9:
            break
        y = min(y, H)

        if y < y_margin or y > H - y_margin:
            continue  # skip — would be clipped to less than quarter-height

        # Even rows anchor at offset; odd rows shift by half a period.
        anchor = offset if row_idx % 2 == 0 else offset + period / 2

        # Walk back far enough to catch any diamond that clips the left edge.
        n_back = math.ceil((anchor + cut_len / 2) / period)
        cx = anchor - n_back * period

        while True:
            x_left = cx - cut_len / 2
            x_right = cx + cut_len / 2

            if x_left >= W + 1e-9:
                break
            if x_right <= -1e-9:
                cx += period
                continue

            clips_left = x_left < -1e-9
            clips_right = x_right > W + 1e-9

            # Skip slivers narrower than 25% of a full diamond — only draw
            # meaningful partial shapes at the edges.
            min_partial = cut_len * 0.25

            if clips_left and clips_right:
                pass
            elif clips_left and x_right >= min_partial:
                lines.extend(_create_half_diamond_open_left(y, diamond_height, x_right))
            elif clips_right and (W - x_left) >= min_partial:
                lines.extend(_create_half_diamond_open_right(y, diamond_height, x_left, W))
            elif not clips_left and not clips_right:
                lines.extend(_create_diamond_cut(x_left, x_right, y, diamond_height))

            cx += period

    return lines


def _create_diamond_cut(x_start: float, x_end: float, y: float, height: float) -> List[LineSegment]:
    """
    Create a single diamond (rhombus) cut shape.

    4 straight line segments of equal length meeting at sharp pointed corners:
        Left tip → Top tip → Right tip → Bottom tip → Left tip

    Args:
        x_start: Left tip x-coordinate
        x_end:   Right tip x-coordinate
        y:       Center y-coordinate (left and right tips sit at this y)
        height:  Total height of diamond (top tip to bottom tip distance)

    Returns:
        List of 4 LineSegment objects forming a closed rhombus
    """
    cx = (x_start + x_end) / 2
    half_h = height / 2

    left   = (x_start, y)
    top    = (cx, y + half_h)
    right  = (x_end,   y)
    bottom = (cx, y - half_h)

    return [
        LineSegment(left[0],   left[1],   top[0],    top[1],    layer="cuts"),
        LineSegment(top[0],    top[1],    right[0],  right[1],  layer="cuts"),
        LineSegment(right[0],  right[1],  bottom[0], bottom[1], layer="cuts"),
        LineSegment(bottom[0], bottom[1], left[0],   left[1],   layer="cuts"),
    ]


def _create_half_diamond_open_left(center_y: float, height: float, right_tip_x: float) -> List[LineSegment]:
    """
    Right-facing half-diamond at the left material edge (x=0).

    Two segments forming a '>' shape: endpoints on the left edge, tip at right_tip_x.

    Args:
        center_y:    y-coordinate of the tip
        height:      Diamond height (endpoints at center_y ± height/2)
        right_tip_x: x of the inward tip (= cx + cut_len/2 of the clipped diamond)
    """
    b = height / 2
    return [
        LineSegment(0, center_y + b, right_tip_x, center_y, layer="cuts"),
        LineSegment(right_tip_x, center_y, 0, center_y - b, layer="cuts"),
    ]


def _create_half_diamond_open_right(center_y: float, height: float, left_tip_x: float, W: float) -> List[LineSegment]:
    """
    Left-facing half-diamond at the right material edge (x=W).

    Two segments forming a '<' shape: endpoints on the right edge, tip at left_tip_x.

    Args:
        center_y:   y-coordinate of the tip
        height:     Diamond height (endpoints at center_y ± height/2)
        left_tip_x: x of the inward tip (= cx - cut_len/2 of the clipped diamond)
        W:          Material width
    """
    b = height / 2
    return [
        LineSegment(W, center_y + b, left_tip_x, center_y, layer="cuts"),
        LineSegment(left_tip_x, center_y, W, center_y - b, layer="cuts"),
    ]


def _generate_oval_pattern(params: KerfParameters) -> List[LineSegment]:
    """
    Generate staggered horizontal lens-cut pattern producing pointed-ellipse voids.

    Same row/stagger layout as the diamond pattern. Even rows begin with a half-oval
    clipped at the left edge (x=0) so cuts reach the bending edge. Odd rows start
    at period/2 (small tab from left). Both row types clip at the right edge.

    Args:
        params: KerfParameters defining the pattern
            - cut_length:  horizontal span of each lens cut (mm)
            - cut_spacing: row pitch AND horizontal tab width (mm)

    Returns:
        List of LineSegment objects representing the lens-shaped cuts
    """
    lines: List[LineSegment] = []

    cut_len = params.cut_length
    tab_width = params.cut_spacing            # horizontal gap between ovals
    row_spacing = params.effective_row_spacing  # vertical pitch (may differ from tab_width)
    period = cut_len + tab_width             # x-period stays tied to cut_spacing
    W = params.material_width
    H = params.material_height
    lens_height = row_spacing * 0.75

    if period <= 0 or W <= 0 or H <= 0:
        return lines

    # Center the grid so both edge clips are symmetric.
    offset = (W % period) / 2

    # Don't place rows so close to the top/bottom that they'd produce tiny slivers.
    y_margin = lens_height / 4

    row = 0
    y = 0.0
    while y <= H + 1e-9:

        if y < y_margin or y > H - y_margin:
            y += row_spacing
            row += 1
            continue  # skip — would be clipped to less than quarter-height

        anchor = offset if row % 2 == 0 else offset + period / 2
        n_back = math.ceil((anchor + cut_len / 2) / period)
        cx = anchor - n_back * period

        while True:
            x_left = cx - cut_len / 2
            x_right = cx + cut_len / 2

            if x_left >= W + 1e-9:
                break
            if x_right <= -1e-9:
                cx += period
                continue

            clips_left = x_left < -1e-9
            clips_right = x_right > W + 1e-9

            min_partial = cut_len * 0.25

            if clips_left and clips_right:
                pass
            elif clips_left and x_right >= min_partial:
                lines.extend(_create_half_lens_open_left(y, lens_height, cx, cut_len))
            elif clips_right and (W - x_left) >= min_partial:
                lines.extend(_create_half_lens_open_right(y, lens_height, cx, cut_len, W))
            elif not clips_left and not clips_right:
                lines.extend(_create_lens_cut(x_left, x_right, y, lens_height))

            cx += period

        y += row_spacing
        row += 1

    return lines


def _create_lens_cut(x_start: float, x_end: float, y: float, height: float, num_segments: int = 12) -> List[LineSegment]:
    """
    Create a lens/eye shaped cut (closed pointed ellipse) approximated with line segments.

    The lens is pointed at both ends (x_start, y) and (x_end, y), with the top arc
    bulging upward and the bottom arc bulging downward.

    Args:
        x_start: Left tip of lens
        x_end:   Right tip of lens
        y:       Center y-coordinate (the lens is symmetric about this y)
        height:  Total height of lens (top to bottom, so each arc bulges by height/2)
        num_segments: Segments per arc half (default: 12)

    Returns:
        List of LineSegment objects forming the closed lens outline
    """
    lines = []
    a = (x_end - x_start) / 2   # semi-major axis (horizontal)
    b = height / 2               # semi-minor axis (vertical)
    cx = x_start + a
    cy = y

    # Top arc: theta 0 → π  (sin is positive → curves upward)
    # Bottom arc: theta π → 2π  (sin is negative → curves downward)
    num_pts = num_segments * 2
    points = []
    for i in range(num_pts):
        theta = (2 * math.pi * i) / num_pts
        px = cx + a * math.cos(theta)
        py = cy + b * math.sin(theta)
        points.append((px, py))

    for i in range(num_pts):
        p1 = points[i]
        p2 = points[(i + 1) % num_pts]
        lines.append(LineSegment(p1[0], p1[1], p2[0], p2[1], layer="cuts"))

    return lines


def _create_half_lens_open_left(center_y: float, height: float, cx: float, cut_len: float, num_segments: int = 8) -> List[LineSegment]:
    """
    Visible arc of a lens centred at (cx, center_y) clipped at the left edge (x=0).

    Traces from (0, center_y-b_clip) → right tip → (0, center_y+b_clip) using the
    angular range where the ellipse is within x ≥ 0.

    Args:
        center_y:     y-coordinate of the ellipse centre
        height:       Full lens height (semi-minor axis b = height/2)
        cx:           x-coordinate of the ellipse centre (< cut_len/2, so it clips at x=0)
        cut_len:      Full lens width (semi-major axis a = cut_len/2)
        num_segments: Line-segment count for the arc
    """
    a = cut_len / 2
    b = height / 2
    # Angle where ellipse crosses x=0: cx + a*cos(θ) = 0 → cos(θ) = -cx/a
    cos_theta = max(-1.0, min(1.0, -cx / a))
    theta_cross = math.acos(cos_theta)  # in [0, π]; right arc spans [-theta_cross, theta_cross]
    points = []
    for i in range(num_segments + 1):
        theta = -theta_cross + 2 * theta_cross * i / num_segments
        points.append((cx + a * math.cos(theta), center_y + b * math.sin(theta)))
    return [
        LineSegment(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1], layer="cuts")
        for i in range(len(points) - 1)
    ]


def _create_half_lens_open_right(center_y: float, height: float, cx: float, cut_len: float, W: float, num_segments: int = 8) -> List[LineSegment]:
    """
    Visible arc of a lens centred at (cx, center_y) clipped at the right edge (x=W).

    Traces from (W, center_y+b_clip) → left tip → (W, center_y-b_clip).
    Arc spans [theta_cross, 2π-theta_cross] so both endpoints land exactly on x=W.

    Args:
        center_y:     y-coordinate of the ellipse centre
        height:       Full lens height (semi-minor axis b = height/2)
        cx:           x-coordinate of the ellipse centre (> W - cut_len/2, so it clips at x=W)
        cut_len:      Full lens width (semi-major axis a = cut_len/2)
        W:            Material width
        num_segments: Line-segment count for the arc
    """
    a = cut_len / 2
    b = height / 2
    # Crossing angle: cx + a*cos(θ) = W → cos(θ) = (W-cx)/a
    cos_theta = max(-1.0, min(1.0, (W - cx) / a))
    theta_cross = math.acos(cos_theta)  # in [π/2, π] since cx > W-a
    # Left portion: theta from theta_cross → 2π-theta_cross (through π).
    # At theta=theta_cross: px=W (top crossing). At theta=π: px=cx-a (left tip). At theta=2π-theta_cross: px=W (bottom crossing).
    arc_span = 2 * math.pi - 2 * theta_cross
    points = []
    for i in range(num_segments + 1):
        theta = theta_cross + arc_span * i / num_segments
        points.append((cx + a * math.cos(theta), center_y + b * math.sin(theta)))
    return [
        LineSegment(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1], layer="cuts")
        for i in range(len(points) - 1)
    ]


def _liang_barsky(
    x1: float, y1: float, x2: float, y2: float,
    xmin: float, ymin: float, xmax: float, ymax: float,
) -> tuple[float, float, float, float] | None:
    """
    Clip segment (x1,y1)→(x2,y2) to axis-aligned box using Liang-Barsky.

    Returns clipped (x1, y1, x2, y2) or None if the segment is fully outside.
    """
    dx, dy = x2 - x1, y2 - y1
    p = (-dx, dx, -dy, dy)
    q = (x1 - xmin, xmax - x1, y1 - ymin, ymax - y1)
    t0, t1 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if pi == 0.0:
            if qi < 0.0:
                return None
        elif pi < 0.0:
            t0 = max(t0, qi / pi)
        else:
            t1 = min(t1, qi / pi)
    if t0 > t1:
        return None
    return x1 + t0 * dx, y1 + t0 * dy, x1 + t1 * dx, y1 + t1 * dy


def _clip_lines_to_bounds(
    lines: List[LineSegment],
    xmin: float, ymin: float, xmax: float, ymax: float,
) -> List[LineSegment]:
    """Clip all segments to the given bounding box, discarding those fully outside."""
    result: List[LineSegment] = []
    for seg in lines:
        clipped = _liang_barsky(seg.x1, seg.y1, seg.x2, seg.y2, xmin, ymin, xmax, ymax)
        if clipped:
            x1, y1, x2, y2 = clipped
            result.append(LineSegment(x1, y1, x2, y2, layer=seg.layer))
    return result


def generate_outline(params: KerfParameters) -> List[LineSegment]:
    """
    Generate outline rectangle for the material boundary.

    Creates a closed rectangle representing the material edges on the outline layer.

    Args:
        params: KerfParameters defining the material dimensions

    Returns:
        List of 4 LineSegment objects forming a rectangle
    """
    return [
        LineSegment(0, 0, params.material_width, 0, layer="outline"),
        LineSegment(params.material_width, 0, params.material_width, params.material_height, layer="outline"),
        LineSegment(params.material_width, params.material_height, 0, params.material_height, layer="outline"),
        LineSegment(0, params.material_height, 0, 0, layer="outline"),
    ]


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
