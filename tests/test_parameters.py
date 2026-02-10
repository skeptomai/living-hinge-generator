"""
Tests for parameter classes.
"""

import pytest
from kerf_generator import KerfParameters, LineSegment


class TestKerfParameters:
    """Tests for KerfParameters dataclass."""

    def test_valid_parameters(self):
        """Test creating valid parameters."""
        params = KerfParameters(
            material_width=100,
            material_height=200,
            material_thickness=3,
            kerf_width=0.2,
            cut_spacing=10,
            cut_length=80,
            cut_offset=10,
            pattern_direction='horizontal',
        )
        assert params.material_width == 100
        assert params.material_height == 200
        assert params.pattern_direction == 'horizontal'

    def test_invalid_parameters_raise_error(self):
        """Test that invalid parameters raise ValueError."""
        with pytest.raises(ValueError):
            KerfParameters(
                material_width=-100,  # Invalid!
                material_height=200,
                material_thickness=3,
                kerf_width=0.2,
                cut_spacing=5,
                cut_length=80,
                cut_offset=10,
                pattern_direction='horizontal',
            )

    def test_bend_radius_property(self):
        """Test that bend_radius property works."""
        params = KerfParameters(
            material_width=100,
            material_height=200,
            material_thickness=3,
            kerf_width=0.2,
            cut_spacing=10,
            cut_length=80,
            cut_offset=10,
            pattern_direction='horizontal',
        )
        radius = params.bend_radius
        assert radius > 0
        assert isinstance(radius, float)

    def test_num_cuts_horizontal(self):
        """Test num_cuts property for horizontal pattern."""
        params = KerfParameters(
            material_width=100,
            material_height=100,
            material_thickness=3,
            kerf_width=0.2,
            cut_spacing=10,
            cut_length=80,
            cut_offset=10,
            pattern_direction='horizontal',
        )
        # For horizontal: uses height dimension
        # Available: 100 - 20 = 80, spacing 10 -> 9 cuts
        assert params.num_cuts == 9

    def test_num_cuts_vertical(self):
        """Test num_cuts property for vertical pattern."""
        params = KerfParameters(
            material_width=100,
            material_height=100,
            material_thickness=3,
            kerf_width=0.2,
            cut_spacing=10,
            cut_length=80,
            cut_offset=10,
            pattern_direction='vertical',
        )
        # For vertical: uses width dimension
        assert params.num_cuts == 9

    def test_summary_method(self):
        """Test that summary method returns string."""
        params = KerfParameters(
            material_width=100,
            material_height=200,
            material_thickness=3,
            kerf_width=0.2,
            cut_spacing=10,
            cut_length=80,
            cut_offset=10,
            pattern_direction='horizontal',
        )
        summary = params.summary()
        assert isinstance(summary, str)
        assert "100" in summary
        assert "horizontal" in summary


class TestLineSegment:
    """Tests for LineSegment dataclass."""

    def test_create_line_segment(self):
        """Test creating a line segment."""
        line = LineSegment(0, 0, 10, 0)
        assert line.x1 == 0
        assert line.y1 == 0
        assert line.x2 == 10
        assert line.y2 == 0

    def test_length_property(self):
        """Test length calculation."""
        line = LineSegment(0, 0, 3, 4)
        # 3-4-5 triangle
        assert line.length == 5.0

    def test_midpoint_property(self):
        """Test midpoint calculation."""
        line = LineSegment(0, 0, 10, 20)
        midpoint = line.midpoint
        assert midpoint == (5.0, 10.0)

    def test_horizontal_line_length(self):
        """Test length of horizontal line."""
        line = LineSegment(10, 5, 90, 5)
        assert line.length == 80.0

    def test_vertical_line_length(self):
        """Test length of vertical line."""
        line = LineSegment(5, 10, 5, 90)
        assert line.length == 80.0
