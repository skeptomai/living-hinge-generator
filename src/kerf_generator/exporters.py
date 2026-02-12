"""
Export functions for kerf patterns.

Supports exporting to DXF (for CAD/laser cutting) and images (for preview).
"""

from pathlib import Path
from typing import List, Optional, Literal
import ezdxf
from ezdxf import colors
from ezdxf.enums import TextEntityAlignment
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.figure import Figure

from .parameters import KerfParameters, LineSegment


def export_dxf(
    lines: List[LineSegment],
    params: KerfParameters,
    output_path: str | Path,
    include_outline: bool = True,
) -> None:
    """
    Export pattern to DXF file format.

    Creates a DXF file compatible with Fusion 360, Lightburn, and other CAD software.
    Uses layers to separate cuts from outline/reference geometry.

    Layers:
        - "cuts": Cut lines (red, 0.13mm weight) - for laser cutting
        - "outline": Material boundary (blue, 0.25mm weight) - reference only

    Args:
        lines: List of LineSegment objects to export
        params: KerfParameters used to generate the pattern
        output_path: Path to save DXF file
        include_outline: Whether to include material outline (default: True)

    Example:
        >>> lines = generate_living_hinge(params)
        >>> export_dxf(lines, params, "output/pattern.dxf")
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create new DXF document (AutoCAD 2000 format for compatibility)
    doc = ezdxf.new("R2000")
    msp = doc.modelspace()

    # Set units to millimeters (4 = mm, default is 6 = meters)
    doc.header['$INSUNITS'] = 4
    doc.header['$MEASUREMENT'] = 1  # Metric

    # Create layers with appropriate colors and line weights
    # Layer for cuts (red - standard laser cutting color)
    doc.layers.add(
        name="cuts",
        color=colors.RED,
        linetype="CONTINUOUS",
    )

    # Layer for outline (blue - reference geometry)
    doc.layers.add(
        name="outline",
        color=colors.BLUE,
        linetype="CONTINUOUS",
    )

    # Add cut lines
    for line in lines:
        msp.add_line(
            start=(line.x1, line.y1),
            end=(line.x2, line.y2),
            dxfattribs={"layer": line.layer},
        )

    # Add outline if requested
    if include_outline:
        # Material boundary rectangle
        # For diamond/oval patterns, top and bottom edges need to be on "cuts" layer
        # to cut through the open ends of split shapes
        needs_cutting_edges = params.pattern_type in ["diamond", "oval"]

        # Bottom edge (y=0)
        msp.add_line(
            start=(0, 0),
            end=(params.material_width, 0),
            dxfattribs={"layer": "cuts" if needs_cutting_edges else "outline"},
        )

        # Right edge
        msp.add_line(
            start=(params.material_width, 0),
            end=(params.material_width, params.material_height),
            dxfattribs={"layer": "outline"},
        )

        # Top edge (y=material_height)
        msp.add_line(
            start=(params.material_width, params.material_height),
            end=(0, params.material_height),
            dxfattribs={"layer": "cuts" if needs_cutting_edges else "outline"},
        )

        # Left edge
        msp.add_line(
            start=(0, params.material_height),
            end=(0, 0),
            dxfattribs={"layer": "outline"},
        )

    # Add text annotation with parameters
    text_y = params.material_height + 5
    text_content = (
        f"Kerf Pattern: {params.cut_spacing}mm spacing, "
        f"{params.cut_length}mm cuts, {params.kerf_width}mm kerf"
    )

    msp.add_text(
        text_content,
        dxfattribs={
            "layer": "outline",
            "height": 3,  # Text height in mm
            "insert": (0, text_y),
        },
    )

    # Save DXF file
    doc.saveas(output_path)


def export_image(
    lines: List[LineSegment],
    params: KerfParameters,
    output_path: str | Path,
    format: Literal["png", "svg", "pdf"] = "png",
    dpi: int = 300,
    show_grid: bool = True,
    show_annotations: bool = True,
) -> None:
    """
    Export pattern as an image for preview and verification.

    Creates a visual representation with color coding and optional annotations.

    Color scheme:
        - Red: Cut lines (what the laser will cut)
        - Blue: Material outline (reference)
        - Gray: Grid (if enabled)

    Args:
        lines: List of LineSegment objects to export
        params: KerfParameters used to generate the pattern
        output_path: Path to save image file
        format: Output format - 'png', 'svg', or 'pdf' (default: 'png')
        dpi: Resolution for raster formats (default: 300)
        show_grid: Whether to show grid overlay (default: True)
        show_annotations: Whether to show parameter annotations (default: True)

    Example:
        >>> lines = generate_living_hinge(params)
        >>> export_image(lines, params, "output/pattern.png", show_grid=True)
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create figure with appropriate size
    # Size based on material dimensions with larger margins for legend space
    side_margin = max(params.material_width, params.material_height) * 0.18  # Even wider side margins
    top_margin = max(params.material_width, params.material_height) * 0.40  # More space for legend
    bottom_margin = max(params.material_width, params.material_height) * 0.10

    fig_width = (params.material_width + 2 * side_margin) / 25.4 * 1.5  # Make 50% wider
    fig_height = (params.material_height + top_margin + bottom_margin) / 25.4 * 1.2  # 20% taller

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    # Set up coordinate system (origin at bottom-left)
    ax.set_xlim(-side_margin, params.material_width + side_margin)
    ax.set_ylim(-bottom_margin, params.material_height + top_margin)
    ax.set_aspect("equal")

    # Draw material outline
    outline_rect = patches.Rectangle(
        (0, 0),
        params.material_width,
        params.material_height,
        linewidth=2,
        edgecolor="blue",
        facecolor="none",
        label="Material outline",
    )
    ax.add_patch(outline_rect)

    # Draw cut lines
    for line in lines:
        ax.plot(
            [line.x1, line.x2],
            [line.y1, line.y2],
            color="red",
            linewidth=1,
            label="Cuts" if line == lines[0] else "",
        )

    # Add grid if requested
    if show_grid:
        ax.grid(True, alpha=0.3, linestyle="--", linewidth=0.5, color="gray")
        ax.set_axisbelow(True)

    # Add annotations if requested
    if show_annotations:
        # Parameter text box
        param_text = (
            f"Material: {params.material_width} × {params.material_height} × {params.material_thickness} mm\n"
            f"Cuts: {len(lines)} × {params.cut_length} mm, spacing {params.cut_spacing} mm\n"
            f"Kerf: {params.kerf_width} mm, Direction: {params.pattern_direction}\n"
            f"Bend radius: {params.bend_radius:.1f} mm, Max angle: {params.max_bend_angle:.1f}°"
        )

        # Place text annotation above the pattern in the top margin area
        # Moved left 10% and up 10% from original position
        ax.text(
            params.material_width * 0.10,
            params.material_height + top_margin * 0.70,
            param_text,
            fontsize=9,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.9),
            family="monospace",
        )

    # Labels and title
    ax.set_xlabel("Width (mm)")
    ax.set_ylabel("Height (mm)")
    ax.set_title(f"Kerf Pattern Preview - {params.pattern_direction.capitalize()} Cuts", pad=20)

    # Legend disabled - only showing parameter stats box
    # handles, labels = ax.get_legend_handles_labels()
    # if handles:
    #     # Remove duplicate labels
    #     by_label = dict(zip(labels, handles))
    #     ax.legend(
    #         by_label.values(),
    #         by_label.keys(),
    #         loc="upper right",
    #         bbox_to_anchor=(0.85, 1.20),
    #         framealpha=0.95,
    #         ncol=1,
    #         fontsize=10,
    #         labelspacing=1.2,
    #         borderpad=1.0,
    #         handlelength=2.5,
    #     )

    # Tight layout
    plt.tight_layout()

    # Save figure
    plt.savefig(output_path, dpi=dpi, format=format, bbox_inches="tight")
    plt.close(fig)


def export_svg(
    lines: List[LineSegment],
    params: KerfParameters,
    output_path: str | Path,
    include_outline: bool = True,
) -> None:
    """
    Export pattern as SVG file.

    SVG is a vector format that can be imported into Lightburn and other software.
    This is a convenience wrapper around export_image() with SVG format.

    Args:
        lines: List of LineSegment objects to export
        params: KerfParameters used to generate the pattern
        output_path: Path to save SVG file
        include_outline: Whether to show material outline (default: True)
    """
    export_image(
        lines=lines,
        params=params,
        output_path=output_path,
        format="svg",
        show_grid=False,  # SVG typically used for cutting, don't need grid
        show_annotations=False,  # Keep it clean for import into CAD
    )


def export_all(
    lines: List[LineSegment],
    params: KerfParameters,
    output_dir: str | Path,
    base_name: str = "pattern",
) -> dict[str, Path]:
    """
    Export pattern in all supported formats.

    Creates DXF, PNG, and SVG files in the specified directory.

    Args:
        lines: List of LineSegment objects to export
        params: KerfParameters used to generate the pattern
        output_dir: Directory to save output files
        base_name: Base filename without extension (default: "pattern")

    Returns:
        Dictionary mapping format names to output file paths

    Example:
        >>> lines = generate_living_hinge(params)
        >>> files = export_all(lines, params, "output", "living_hinge_5mm")
        >>> print(files["dxf"])
        output/living_hinge_5mm.dxf
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_files = {}

    # Export DXF
    dxf_path = output_dir / f"{base_name}.dxf"
    export_dxf(lines, params, dxf_path)
    output_files["dxf"] = dxf_path

    # Export PNG preview
    png_path = output_dir / f"{base_name}.png"
    export_image(lines, params, png_path, format="png")
    output_files["png"] = png_path

    # Export SVG
    svg_path = output_dir / f"{base_name}.svg"
    export_svg(lines, params, svg_path)
    output_files["svg"] = svg_path

    return output_files
