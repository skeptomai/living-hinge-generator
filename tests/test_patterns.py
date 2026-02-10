"""
Tests for pattern generation.
"""

import pytest
from kerf_generator import KerfParameters
from kerf_generator.patterns import (
    generate_living_hinge,
    generate_outline,
    pattern_statistics,
)


class TestGenerateLivingHinge:
    """Tests for living hinge pattern generation."""

    def test_horizontal_pattern(self):
        """Test generating horizontal pattern."""
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
        lines = generate_living_hinge(params)

        assert len(lines) > 0
        # All lines should be horizontal (y1 == y2)
        for line in lines:
            assert line.y1 == line.y2

    def test_vertical_pattern(self):
        """Test generating vertical pattern."""
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
        lines = generate_living_hinge(params)

        assert len(lines) > 0
        # All lines should be vertical (x1 == x2)
        for line in lines:
            assert line.x1 == line.x2

    def test_cut_count_matches_estimate(self):
        """Test that actual cut count matches estimate."""
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
        lines = generate_living_hinge(params)
        estimated = params.num_cuts

        # Should be close (might differ by 1 due to rounding)
        assert abs(len(lines) - estimated) <= 1

    def test_cuts_within_bounds(self):
        """Test that all cuts are within material bounds."""
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
        lines = generate_living_hinge(params)

        for line in lines:
            assert 0 <= line.x1 <= params.material_width
            assert 0 <= line.x2 <= params.material_width
            assert 0 <= line.y1 <= params.material_height
            assert 0 <= line.y2 <= params.material_height

    def test_respects_offset(self):
        """Test that cuts respect the specified offset."""
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
        lines = generate_living_hinge(params)

        for line in lines:
            # Horizontal cuts: check x boundaries respect offset
            assert line.x1 >= params.cut_offset
            assert line.x2 <= params.material_width - params.cut_offset
            # Check y values respect offset
            assert line.y1 >= params.cut_offset
            assert line.y1 <= params.material_height - params.cut_offset


class TestGenerateOutline:
    """Tests for outline generation."""

    def test_generates_rectangle(self):
        """Test that outline generates 4 lines forming a rectangle."""
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
        outline = generate_outline(params)

        assert len(outline) == 4
        # All should be on outline layer
        for line in outline:
            assert line.layer == "outline"


class TestPatternStatistics:
    """Tests for pattern statistics."""

    def test_statistics_calculation(self):
        """Test that statistics are calculated correctly."""
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
        lines = generate_living_hinge(params)
        stats = pattern_statistics(lines)

        assert stats['num_cuts'] == len(lines)
        assert stats['total_cut_length'] > 0
        assert stats['avg_cut_length'] > 0
        assert len(stats['bounds']) == 4

    def test_empty_pattern(self):
        """Test statistics for empty pattern."""
        stats = pattern_statistics([])

        assert stats['num_cuts'] == 0
        assert stats['total_cut_length'] == 0
        assert stats['avg_cut_length'] == 0
