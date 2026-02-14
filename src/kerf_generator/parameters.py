"""
Parameter definitions and validation for kerf cutting patterns.
"""

from dataclasses import dataclass, field
from typing import Optional, Literal
from .geometry import (
    validate_pattern_parameters,
    calculate_bend_radius,
    calculate_max_bend_angle,
    estimate_number_of_cuts,
    estimate_shape_count,
    calculate_num_rows,
)


PatternDirection = Literal["horizontal", "vertical"]
PatternType = Literal["straight", "diamond", "oval"]


@dataclass
class KerfParameters:
    """
    Parameters defining a kerf cutting pattern.

    All dimensions are in millimeters.

    Attributes:
        material_width: Width of material sheet (mm)
        material_height: Height of material sheet (mm)
        material_thickness: Thickness of material (mm)
        kerf_width: Width of laser cut, depends on laser power and material (mm)
        cut_spacing: Distance between parallel cuts (mm)
        cut_length: Length of each individual cut (mm)
        cut_offset: Distance from edges where cuts should not be placed (mm)
        pattern_direction: Orientation of cuts - 'horizontal' or 'vertical' (used for straight cuts only)
        pattern_type: Type of pattern - 'straight', 'diamond', or 'oval'

    Computed Properties:
        bend_radius: Estimated bend radius for this pattern (mm)
        max_bend_angle: Maximum safe bend angle (degrees)
        num_cuts: Estimated number of cuts in the pattern
    """

    # Required parameters
    material_width: float
    material_height: float
    material_thickness: float
    kerf_width: float
    cut_spacing: float
    cut_length: float
    cut_offset: float
    pattern_direction: PatternDirection = "horizontal"
    pattern_type: PatternType = "straight"

    # Optional pattern configuration
    num_vertical_rows: Optional[int] = None  # None = auto-calculate based on height

    # Optional metadata
    material_name: Optional[str] = None
    notes: Optional[str] = None

    def __post_init__(self):
        """Validate parameters after initialization."""
        self.validate()

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate parameters and return validation status.

        Returns:
            Tuple of (is_valid, warnings)
            is_valid: True if parameters are acceptable
            warnings: List of warning/error messages

        Raises:
            ValueError: If parameters are invalid
        """
        is_valid, warnings = validate_pattern_parameters(
            material_width=self.material_width,
            material_height=self.material_height,
            material_thickness=self.material_thickness,
            kerf_width=self.kerf_width,
            cut_spacing=self.cut_spacing,
            cut_length=self.cut_length,
            cut_offset=self.cut_offset,
            pattern_type=self.pattern_type,
        )

        # Check pattern type
        if self.pattern_type not in ("straight", "diamond", "oval"):
            warnings.append(
                f"Pattern type must be 'straight', 'diamond', or 'oval', got '{self.pattern_type}'"
            )
            is_valid = False

        # Check pattern direction
        if self.pattern_direction not in ("horizontal", "vertical"):
            warnings.append(
                f"Pattern direction must be 'horizontal' or 'vertical', got '{self.pattern_direction}'"
            )
            is_valid = False

        # Warn if pattern_direction is non-default for diamond/oval (it's ignored)
        if self.pattern_type in ("diamond", "oval") and self.pattern_direction != "horizontal":
            warnings.append(
                f"Pattern direction is ignored for '{self.pattern_type}' patterns (2D layouts have no direction)"
            )

        if not is_valid:
            error_msg = "Invalid parameters:\n" + "\n".join(f"  - {w}" for w in warnings)
            raise ValueError(error_msg)

        # Print warnings even if valid
        if warnings:
            import warnings as warn_module
            for warning in warnings:
                warn_module.warn(warning, UserWarning)

        return is_valid, warnings

    @property
    def bend_radius(self) -> float:
        """Calculate the approximate bend radius for this pattern."""
        return calculate_bend_radius(
            material_thickness=self.material_thickness,
            cut_spacing=self.cut_spacing,
            kerf_width=self.kerf_width,
            cut_length=self.cut_length,
        )

    @property
    def max_bend_angle(self) -> float:
        """Calculate the maximum practical bend angle in degrees."""
        return calculate_max_bend_angle(
            material_thickness=self.material_thickness,
            cut_spacing=self.cut_spacing,
            cut_length=self.cut_length,
        )

    @property
    def effective_num_rows(self) -> int:
        """
        Get the effective number of vertical rows for diamond/oval patterns.

        Returns:
            Number of rows (1 for straight cuts, auto-calculated or manual for diamond/oval)
        """
        if self.pattern_type == "straight":
            return 1  # Straight cuts don't use row stacking

        if self.num_vertical_rows is not None:
            # User specified explicit number of rows
            return max(1, self.num_vertical_rows)

        # Auto-calculate based on material height
        return calculate_num_rows(self.material_height)

    @property
    def num_cuts(self) -> int:
        """
        Estimate the number of cuts/shapes in this pattern.

        For straight cuts: Returns number of cut lines
        For diamond/oval: Returns number of shapes (not individual line segments)
        """
        if self.pattern_type == "straight":
            # Determine which dimension to use based on pattern direction
            if self.pattern_direction == "horizontal":
                # Horizontal cuts span across the width, multiple cuts down the height
                dimension = self.material_height
            else:
                # Vertical cuts span down the height, multiple cuts across the width
                dimension = self.material_width

            return estimate_number_of_cuts(
                material_dimension=dimension,
                cut_spacing=self.cut_spacing,
                cut_offset=self.cut_offset,
            )
        else:
            # For diamond/oval patterns, count shapes in 2D grid
            # Multiply by number of rows since each row has its own set of shapes
            shapes_per_row = estimate_shape_count(
                material_width=self.material_width,
                material_height=self.material_height,
                shape_size=self.cut_length,
                spacing=self.cut_spacing,
                offset=self.cut_offset,
            )
            return shapes_per_row * self.effective_num_rows

    def summary(self) -> str:
        """
        Generate a human-readable summary of the parameters.

        Returns:
            Multi-line string describing the pattern
        """
        lines = [
            "Kerf Pattern Parameters",
            "=" * 50,
            f"Material: {self.material_width} × {self.material_height} × {self.material_thickness} mm",
        ]

        if self.material_name:
            lines.append(f"Material Type: {self.material_name}")

        lines.extend([
            f"Kerf Width: {self.kerf_width} mm",
            f"Cut Spacing: {self.cut_spacing} mm",
            f"Cut Length: {self.cut_length} mm",
            f"Cut Offset: {self.cut_offset} mm",
            f"Pattern Type: {self.pattern_type}",
        ])

        # Only show pattern direction for straight cuts
        if self.pattern_type == "straight":
            lines.append(f"Pattern Direction: {self.pattern_direction}")

        lines.extend([
            "",
            "Calculated Properties:",
            f"  Estimated {'Shapes' if self.pattern_type in ('diamond', 'oval') else 'Cuts'}: {self.num_cuts}",
        ])

        # Show number of rows for diamond/oval patterns
        if self.pattern_type in ("diamond", "oval"):
            rows = self.effective_num_rows
            auto_calc = " (auto)" if self.num_vertical_rows is None else ""
            lines.append(f"  Vertical Rows: {rows}{auto_calc}")

        lines.extend([
            f"  Bend Radius: {self.bend_radius:.2f} mm",
            f"  Max Bend Angle: {self.max_bend_angle:.1f}°",
        ])

        if self.notes:
            lines.extend(["", f"Notes: {self.notes}"])

        return "\n".join(lines)

    def __str__(self) -> str:
        """String representation of parameters."""
        return (
            f"KerfParameters({self.material_width}×{self.material_height}×{self.material_thickness}mm, "
            f"spacing={self.cut_spacing}mm, {self.pattern_direction})"
        )

    def __repr__(self) -> str:
        """Detailed representation of parameters."""
        return (
            f"KerfParameters("
            f"material_width={self.material_width}, "
            f"material_height={self.material_height}, "
            f"material_thickness={self.material_thickness}, "
            f"kerf_width={self.kerf_width}, "
            f"cut_spacing={self.cut_spacing}, "
            f"cut_length={self.cut_length}, "
            f"cut_offset={self.cut_offset}, "
            f"pattern_direction='{self.pattern_direction}'"
            f")"
        )


@dataclass
class LineSegment:
    """
    Represents a single line segment (cut) in the pattern.

    Attributes:
        x1, y1: Start point coordinates (mm)
        x2, y2: End point coordinates (mm)
        layer: Optional layer name for DXF export
    """

    x1: float
    y1: float
    x2: float
    y2: float
    layer: str = "cuts"

    @property
    def length(self) -> float:
        """Calculate the length of this line segment."""
        import math
        return math.sqrt((self.x2 - self.x1) ** 2 + (self.y2 - self.y1) ** 2)

    @property
    def midpoint(self) -> tuple[float, float]:
        """Calculate the midpoint of this line segment."""
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)

    def __str__(self) -> str:
        """String representation of line segment."""
        return f"Line[({self.x1:.2f}, {self.y1:.2f}) -> ({self.x2:.2f}, {self.y2:.2f})]"
