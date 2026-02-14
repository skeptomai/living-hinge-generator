"""
Geometric calculations for kerf bending patterns.

This module contains the mathematical models for calculating kerf bending
properties, including bend radius, minimum spacing, and structural integrity
checks.
"""

import math
from typing import Optional
import numpy as np


def calculate_bend_radius(
    material_thickness: float,
    cut_spacing: float,
    kerf_width: float,
    cut_length: float,
) -> float:
    """
    Calculate the approximate bend radius for a living hinge pattern.

    Uses a simplified model based on the ratio of removed material to remaining
    material between cuts. The bend radius is determined by how much material
    remains to carry the bending stress.

    Args:
        material_thickness: Thickness of material in mm
        cut_spacing: Distance between parallel cuts in mm
        kerf_width: Width of laser cut in mm
        cut_length: Length of each cut in mm

    Returns:
        Approximate bend radius in mm

    Notes:
        This is an approximation. Actual bend radius depends on:
        - Material properties (elasticity, grain direction)
        - Hinge geometry (cut pattern, spacing uniformity)
        - Applied force and temperature

    Formula:
        bend_radius ≈ (material_thickness × cut_spacing) / (2 × kerf_width)

        This assumes the neutral axis remains at the material centerline and
        that bending occurs primarily through the rotation of material segments
        between cuts.
    """
    if cut_spacing <= 0:
        raise ValueError("Cut spacing must be positive")
    if kerf_width <= 0:
        raise ValueError("Kerf width must be positive")
    if material_thickness <= 0:
        raise ValueError("Material thickness must be positive")

    # Basic bend radius calculation
    # The radius is proportional to the "hinge" thickness between cuts
    radius = (material_thickness * cut_spacing) / (2 * kerf_width)

    return radius


def calculate_required_spacing(
    target_bend_radius: float,
    material_thickness: float,
    kerf_width: float,
) -> float:
    """
    Calculate the required cut spacing to achieve a target bend radius.

    This is the inverse of calculate_bend_radius(), useful for designing
    patterns with specific bending requirements.

    Args:
        target_bend_radius: Desired bend radius in mm
        material_thickness: Thickness of material in mm
        kerf_width: Width of laser cut in mm

    Returns:
        Required cut spacing in mm

    Formula:
        cut_spacing = (2 × kerf_width × target_bend_radius) / material_thickness
    """
    if target_bend_radius <= 0:
        raise ValueError("Target bend radius must be positive")
    if material_thickness <= 0:
        raise ValueError("Material thickness must be positive")
    if kerf_width <= 0:
        raise ValueError("Kerf width must be positive")

    spacing = (2 * kerf_width * target_bend_radius) / material_thickness

    return spacing


def calculate_max_bend_angle(
    material_thickness: float,
    cut_spacing: float,
    cut_length: float,
) -> float:
    """
    Calculate the maximum practical bend angle for a living hinge.

    The maximum bend angle is limited by the geometry of the cuts and the
    risk of material failure. This provides a conservative estimate.

    Args:
        material_thickness: Thickness of material in mm
        cut_spacing: Distance between parallel cuts in mm
        cut_length: Length of each cut in mm

    Returns:
        Maximum bend angle in degrees

    Notes:
        Maximum angle occurs when adjacent cuts would intersect if bent further.
        Real materials may fail before reaching this geometric limit due to
        stress concentration at cut tips.
    """
    if cut_spacing <= 0:
        raise ValueError("Cut spacing must be positive")
    if material_thickness <= 0:
        raise ValueError("Material thickness must be positive")

    # Simplified geometric limit: angle at which the kerf closes
    # This is when the material segments between cuts become parallel
    # Using small angle approximation: angle ≈ spacing / thickness (radians)

    # Conservative estimate: limit to 90 degrees or geometric limit, whichever is less
    geometric_limit_rad = cut_spacing / material_thickness
    geometric_limit_deg = math.degrees(geometric_limit_rad)

    # Cap at 90 degrees as practical maximum for most materials
    max_angle = min(geometric_limit_deg, 90.0)

    return max_angle


def calculate_minimum_spacing(
    material_thickness: float,
    kerf_width: float,
    safety_factor: float = 2.0,
    pattern_type: str = "structural",
) -> float:
    """
    Calculate the minimum safe spacing between cuts.

    Different pattern types have different spacing requirements:
    - Living hinges (straight/diamond/oval): Tight spacing (2-5mm) for flexibility
    - Structural cuts: Wide spacing (1.5-2x thickness) for strength

    Args:
        material_thickness: Thickness of material in mm
        kerf_width: Width of laser cut in mm
        safety_factor: Multiplier for safety margin (default: 2.0)
        pattern_type: Type of pattern - "straight", "diamond", "oval", or "structural"

    Returns:
        Minimum safe spacing in mm

    Notes:
        Living Hinges (straight/diamond/oval):
            - Target: 3-5mm for good flexibility in wood
            - Minimum: 2mm (tighter risks warping)
            - Based on industry best practices for laser-cut wood living hinges

        Structural Cuts:
            - Rule of thumb: 1.5-2x material thickness for integrity
            - Prevents material collapse, charring, and loss of strength
    """
    if material_thickness <= 0:
        raise ValueError("Material thickness must be positive")
    if kerf_width <= 0:
        raise ValueError("Kerf width must be positive")
    if safety_factor <= 0:
        raise ValueError("Safety factor must be positive")

    # Different rules for living hinges vs structural cuts
    is_living_hinge = pattern_type in ("straight", "diamond", "oval")

    if is_living_hinge:
        # Living hinges need TIGHT spacing for flexibility
        # Based on industry research: 2-5mm range is optimal for 3mm wood
        min_spacing = max(
            2.0,                # Absolute minimum (below this risks warping)
            kerf_width * 10.0,  # Ensure enough material between cuts
        )
    else:
        # Structural cuts need WIDE spacing for strength
        min_spacing = max(
            material_thickness * 1.5,  # Structural minimum
            kerf_width * 3.0,          # Practical cutting minimum
        ) * safety_factor

    return min_spacing


def calculate_hinge_length(
    desired_bend_length: float,
    bend_angle: float,
    bend_radius: float,
) -> float:
    """
    Calculate the flat pattern length needed to achieve a desired bent length.

    When material bends, the outer surface stretches. This calculates how much
    flat material is needed to achieve a specific arc length.

    Args:
        desired_bend_length: Target length of the bent section in mm
        bend_angle: Bend angle in degrees
        bend_radius: Bend radius in mm

    Returns:
        Required flat pattern length in mm

    Formula:
        arc_length = radius × angle (in radians)
    """
    if desired_bend_length <= 0:
        raise ValueError("Desired bend length must be positive")
    if bend_angle <= 0:
        raise ValueError("Bend angle must be positive")
    if bend_radius <= 0:
        raise ValueError("Bend radius must be positive")

    # Convert angle to radians
    angle_rad = math.radians(bend_angle)

    # Arc length formula
    arc_length = bend_radius * angle_rad

    return arc_length


def validate_pattern_parameters(
    material_width: float,
    material_height: float,
    material_thickness: float,
    kerf_width: float,
    cut_spacing: float,
    cut_length: float,
    cut_offset: float,
    pattern_type: str = "structural",
) -> tuple[bool, list[str]]:
    """
    Validate that pattern parameters are physically reasonable and safe.

    Args:
        material_width: Width of material in mm
        material_height: Height of material in mm
        material_thickness: Thickness of material in mm
        kerf_width: Width of laser cut in mm
        cut_spacing: Distance between cuts in mm
        cut_length: Length of each cut in mm
        cut_offset: Offset from edge in mm
        pattern_type: Type of pattern - "straight", "diamond", "oval", or "structural"

    Returns:
        Tuple of (is_valid, list_of_warnings)
        is_valid: True if parameters are acceptable
        warnings: List of warning messages (may be empty even if valid)
    """
    warnings = []
    is_valid = True

    # Check all positive
    if material_width <= 0 or material_height <= 0 or material_thickness <= 0:
        warnings.append("Material dimensions must be positive")
        is_valid = False

    if kerf_width <= 0:
        warnings.append("Kerf width must be positive")
        is_valid = False

    if cut_spacing <= 0:
        warnings.append("Cut spacing must be positive")
        is_valid = False

    if cut_length <= 0:
        warnings.append("Cut length must be positive")
        is_valid = False

    if cut_offset < 0:
        warnings.append("Cut offset cannot be negative")
        is_valid = False

    # Check geometric constraints
    if cut_length >= material_height:
        warnings.append(
            f"Cut length ({cut_length}mm) must be less than material height ({material_height}mm)"
        )
        is_valid = False

    if cut_length >= material_width:
        warnings.append(
            f"Cut length ({cut_length}mm) must be less than material width ({material_width}mm)"
        )
        is_valid = False

    # Check spacing safety (pattern-type aware)
    is_living_hinge = pattern_type in ("straight", "diamond", "oval")
    min_spacing = calculate_minimum_spacing(material_thickness, kerf_width, pattern_type=pattern_type)

    if cut_spacing < min_spacing:
        if is_living_hinge:
            warnings.append(
                f"Cut spacing ({cut_spacing}mm) is below recommended minimum ({min_spacing:.2f}mm). "
                "Risk of warping or unreliable cuts. For living hinges, 3-5mm spacing is optimal."
            )
        else:
            warnings.append(
                f"Cut spacing ({cut_spacing}mm) is below recommended minimum ({min_spacing:.2f}mm). "
                "Risk of structural failure."
            )
        # Don't set is_valid=False, just warn

    # Living hinge specific guidance: warn if spacing is too wide for good flexibility
    if is_living_hinge and cut_spacing > 8.0:
        warnings.append(
            f"Cut spacing ({cut_spacing}mm) is quite wide for a living hinge. "
            "Consider 3-5mm for better flexibility. Wider spacing = stiffer hinge."
        )

    # Check that cuts fit within material
    if cut_offset * 2 + cut_length > material_height:
        warnings.append(
            f"Cut length + offsets ({cut_offset * 2 + cut_length}mm) exceeds material height"
        )
        is_valid = False

    if cut_offset * 2 + cut_length > material_width:
        warnings.append(
            f"Cut length + offsets ({cut_offset * 2 + cut_length}mm) exceeds material width"
        )
        is_valid = False

    # Check kerf width reasonableness
    if kerf_width > material_thickness:
        warnings.append(
            f"Kerf width ({kerf_width}mm) is larger than material thickness ({material_thickness}mm). "
            "This is unusual - verify your kerf width."
        )

    if kerf_width < 0.05:
        warnings.append(
            f"Kerf width ({kerf_width}mm) is very small. Typical laser kerf is 0.1-0.3mm."
        )

    return is_valid, warnings


def estimate_number_of_cuts(
    material_dimension: float,
    cut_spacing: float,
    cut_offset: float,
) -> int:
    """
    Estimate how many cuts will fit in the pattern area.

    Args:
        material_dimension: Width or height of material in mm (depending on cut direction)
        cut_spacing: Distance between cuts in mm
        cut_offset: Offset from edges in mm

    Returns:
        Number of cuts that will fit
    """
    if material_dimension <= 0 or cut_spacing <= 0:
        return 0

    # Available space for cuts
    available_space = material_dimension - (2 * cut_offset)

    if available_space <= 0:
        return 0

    # Number of cuts that fit
    num_cuts = int(available_space / cut_spacing) + 1

    return max(0, num_cuts)


def estimate_shape_count(
    material_width: float,
    material_height: float,
    shape_size: float,
    spacing: float,
    offset: float,
) -> int:
    """
    Estimate how many diamond/oval shapes fit in the material using column-based layout.

    For elongated vertical patterns, this calculates the number of columns that fit
    horizontally. Each column contains either one full shape or one split shape (which
    counts as one shape).

    Args:
        material_width: Width of material in mm
        material_height: Height of material in mm (not used for column count, but kept for compatibility)
        shape_size: Width of each shape in mm
        spacing: Horizontal spacing between columns in mm
        offset: Offset from material edges in mm

    Returns:
        Number of shapes (columns) that will fit
    """
    if material_width <= 0 or shape_size <= 0 or spacing <= 0:
        return 0

    # Available space after accounting for offsets
    available_width = material_width - (2 * offset)

    if available_width <= 0:
        return 0

    # Calculate number of columns (each column is one shape)
    # Shapes are spaced horizontally by 'spacing'
    num_columns = int(available_width / spacing) + 1

    return max(0, num_columns)


def calculate_num_rows(
    material_height: float,
    height_threshold: float = 150.0,
) -> int:
    """
    Calculate the number of vertical rows for diamond/oval patterns.

    For tall materials, stacking multiple rows of patterns vertically provides better
    flexibility control and structural integrity than single very elongated shapes.

    Args:
        material_height: Height of material in mm
        height_threshold: Maximum height per row in mm (default: 150mm)

    Returns:
        Number of rows to use (minimum 1)

    Notes:
        - Materials ≤ threshold: 1 row (single pattern spanning full height)
        - Materials > threshold: Divided into ~threshold-sized rows
        - Example: 300mm material with 150mm threshold → 2 rows of ~150mm each
    """
    if material_height <= 0:
        return 1

    if material_height <= height_threshold:
        return 1

    # Calculate how many rows are needed to keep each row at or below threshold
    num_rows = int(material_height / height_threshold)

    # If the division leaves a very small remainder, keep the same number of rows
    # Otherwise add one more row
    remainder = material_height % height_threshold
    if remainder > height_threshold * 0.3:  # If remainder is >30% of threshold
        num_rows += 1

    return max(1, num_rows)
