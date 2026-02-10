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
) -> float:
    """
    Calculate the minimum safe spacing between cuts.

    Spacing too close can result in material failure, poor structural integrity,
    or burns during cutting. This provides a conservative minimum.

    Args:
        material_thickness: Thickness of material in mm
        kerf_width: Width of laser cut in mm
        safety_factor: Multiplier for safety margin (default: 2.0)

    Returns:
        Minimum safe spacing in mm

    Notes:
        Rule of thumb: spacing should be at least 1.5-2x material thickness
        for structural integrity. Thinner spacing risks:
        - Material collapse during cutting
        - Excessive charring between cuts
        - Loss of structural strength
    """
    if material_thickness <= 0:
        raise ValueError("Material thickness must be positive")
    if kerf_width <= 0:
        raise ValueError("Kerf width must be positive")
    if safety_factor <= 0:
        raise ValueError("Safety factor must be positive")

    # Minimum spacing based on material thickness and kerf
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

    # Check spacing safety
    min_spacing = calculate_minimum_spacing(material_thickness, kerf_width)
    if cut_spacing < min_spacing:
        warnings.append(
            f"Cut spacing ({cut_spacing}mm) is below recommended minimum ({min_spacing:.2f}mm). "
            "Risk of structural failure."
        )
        # Don't set is_valid=False, just warn

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
