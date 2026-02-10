"""
Tests for geometry calculations.
"""

import pytest
import math
from kerf_generator.geometry import (
    calculate_bend_radius,
    calculate_required_spacing,
    calculate_max_bend_angle,
    calculate_minimum_spacing,
    validate_pattern_parameters,
    estimate_number_of_cuts,
)


class TestBendRadius:
    """Tests for bend radius calculations."""

    def test_basic_calculation(self):
        """Test basic bend radius calculation."""
        radius = calculate_bend_radius(
            material_thickness=3.0,
            cut_spacing=5.0,
            kerf_width=0.2,
            cut_length=80.0,
        )
        # Expected: (3.0 * 5.0) / (2 * 0.2) = 15 / 0.4 = 37.5
        assert radius == 37.5

    def test_smaller_kerf_larger_radius(self):
        """Smaller kerf width should result in larger bend radius."""
        radius1 = calculate_bend_radius(3.0, 5.0, 0.2, 80.0)
        radius2 = calculate_bend_radius(3.0, 5.0, 0.1, 80.0)
        assert radius2 > radius1

    def test_invalid_parameters(self):
        """Test that invalid parameters raise ValueError."""
        with pytest.raises(ValueError):
            calculate_bend_radius(-3.0, 5.0, 0.2, 80.0)

        with pytest.raises(ValueError):
            calculate_bend_radius(3.0, 0, 0.2, 80.0)

        with pytest.raises(ValueError):
            calculate_bend_radius(3.0, 5.0, -0.2, 80.0)


class TestRequiredSpacing:
    """Tests for required spacing calculations."""

    def test_basic_calculation(self):
        """Test basic required spacing calculation."""
        spacing = calculate_required_spacing(
            target_bend_radius=37.5,
            material_thickness=3.0,
            kerf_width=0.2,
        )
        # Expected: (2 * 0.2 * 37.5) / 3.0 = 15 / 3 = 5.0
        assert spacing == 5.0

    def test_inverse_of_bend_radius(self):
        """Test that this is the inverse of calculate_bend_radius."""
        thickness = 3.0
        kerf = 0.25
        target_radius = 50.0

        spacing = calculate_required_spacing(target_radius, thickness, kerf)
        actual_radius = calculate_bend_radius(thickness, spacing, kerf, 100.0)

        assert abs(actual_radius - target_radius) < 0.01

    def test_invalid_parameters(self):
        """Test that invalid parameters raise ValueError."""
        with pytest.raises(ValueError):
            calculate_required_spacing(0, 3.0, 0.2)

        with pytest.raises(ValueError):
            calculate_required_spacing(50.0, -3.0, 0.2)


class TestMaxBendAngle:
    """Tests for maximum bend angle calculations."""

    def test_returns_reasonable_values(self):
        """Test that max angle is reasonable."""
        angle = calculate_max_bend_angle(
            material_thickness=3.0,
            cut_spacing=5.0,
            cut_length=80.0,
        )
        assert 0 < angle <= 90.0

    def test_larger_spacing_larger_angle(self):
        """Larger spacing should allow larger bend angle."""
        # Use smaller spacing values that won't hit the 90° cap
        angle1 = calculate_max_bend_angle(3.0, 2.0, 80.0)
        angle2 = calculate_max_bend_angle(3.0, 4.0, 80.0)
        assert angle2 > angle1


class TestMinimumSpacing:
    """Tests for minimum spacing calculations."""

    def test_basic_calculation(self):
        """Test basic minimum spacing calculation."""
        min_spacing = calculate_minimum_spacing(
            material_thickness=3.0,
            kerf_width=0.2,
            safety_factor=2.0,
        )
        # Should be at least 1.5 * thickness * safety_factor
        expected_min = 1.5 * 3.0 * 2.0
        assert min_spacing >= expected_min

    def test_thicker_material_larger_spacing(self):
        """Thicker material should require larger minimum spacing."""
        spacing1 = calculate_minimum_spacing(3.0, 0.2)
        spacing2 = calculate_minimum_spacing(6.0, 0.2)
        assert spacing2 > spacing1


class TestValidateParameters:
    """Tests for parameter validation."""

    def test_valid_parameters(self):
        """Test that valid parameters pass validation."""
        is_valid, warnings = validate_pattern_parameters(
            material_width=100,
            material_height=200,
            material_thickness=3,
            kerf_width=0.2,
            cut_spacing=10,  # Safe spacing
            cut_length=80,
            cut_offset=10,
        )
        assert is_valid is True

    def test_negative_dimensions(self):
        """Test that negative dimensions are rejected."""
        is_valid, warnings = validate_pattern_parameters(
            material_width=-100,
            material_height=200,
            material_thickness=3,
            kerf_width=0.2,
            cut_spacing=5,
            cut_length=80,
            cut_offset=10,
        )
        assert is_valid is False
        assert len(warnings) > 0

    def test_cut_too_long(self):
        """Test that cuts longer than material are rejected."""
        is_valid, warnings = validate_pattern_parameters(
            material_width=100,
            material_height=200,
            material_thickness=3,
            kerf_width=0.2,
            cut_spacing=5,
            cut_length=250,  # Longer than height!
            cut_offset=10,
        )
        assert is_valid is False

    def test_warns_on_tight_spacing(self):
        """Test that tight spacing generates a warning."""
        is_valid, warnings = validate_pattern_parameters(
            material_width=100,
            material_height=200,
            material_thickness=3,
            kerf_width=0.2,
            cut_spacing=2,  # Very tight spacing
            cut_length=80,
            cut_offset=10,
        )
        # Should still be valid but with warnings
        assert len(warnings) > 0
        assert any("spacing" in w.lower() for w in warnings)


class TestEstimateNumberOfCuts:
    """Tests for cut estimation."""

    def test_basic_estimation(self):
        """Test basic cut count estimation."""
        num_cuts = estimate_number_of_cuts(
            material_dimension=100,
            cut_spacing=5,
            cut_offset=10,
        )
        # Available space: 100 - 20 = 80
        # Cuts at: 10, 15, 20, ..., 90 = 17 cuts
        assert num_cuts == 17

    def test_no_space_returns_zero(self):
        """Test that no available space returns zero cuts."""
        num_cuts = estimate_number_of_cuts(
            material_dimension=10,
            cut_spacing=5,
            cut_offset=10,  # Offset equals half the dimension
        )
        assert num_cuts == 0
