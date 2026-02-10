"""
Command-line interface for Kerf Generator.
"""

import sys
import click
from pathlib import Path
from typing import Optional

from . import (
    KerfParameters,
    generate_living_hinge,
    calculate_bend_radius,
    calculate_required_spacing,
    calculate_minimum_spacing,
    print_pattern_info,
    export_all,
)


@click.group()
@click.version_option(version="0.1.0", prog_name="kerf")
def cli():
    """
    Kerf Generator - Create living hinge patterns for laser cutting.

    Generate DXF files and previews for bendable kerf cutting patterns.
    """
    pass


@cli.command()
@click.option('--width', '-w', type=float, required=True,
              help='Material width in mm')
@click.option('--height', '-h', type=float, required=True,
              help='Material height in mm')
@click.option('--thickness', '-t', type=float, required=True,
              help='Material thickness in mm')
@click.option('--kerf', '-k', type=float, required=True,
              help='Laser kerf width in mm (typically 0.1-0.3)')
@click.option('--spacing', '-s', type=float, required=True,
              help='Distance between cuts in mm')
@click.option('--length', '-l', type=float, required=True,
              help='Length of each cut in mm')
@click.option('--offset', '-o', type=float, default=10,
              help='Edge offset in mm (default: 10)')
@click.option('--direction', '-d', type=click.Choice(['horizontal', 'vertical', 'h', 'v']),
              default='horizontal',
              help='Cut direction: horizontal (h) or vertical (v)')
@click.option('--material-name', '-m', type=str,
              help='Optional material name for documentation')
@click.option('--dxf', type=click.Path(),
              help='Output DXF file path')
@click.option('--png', type=click.Path(),
              help='Output PNG preview path')
@click.option('--svg', type=click.Path(),
              help='Output SVG file path')
@click.option('--output-dir', type=click.Path(),
              help='Output directory for all formats (use with --name)')
@click.option('--name', type=str,
              help='Base filename for outputs (use with --output-dir)')
@click.option('--show-info/--no-show-info', default=True,
              help='Show pattern information before generating')
def generate(width, height, thickness, kerf, spacing, length, offset,
             direction, material_name, dxf, png, svg, output_dir, name, show_info):
    """
    Generate a living hinge pattern.

    Example:
        kerf generate -w 100 -h 200 -t 3 -k 0.2 -s 5 -l 80 -o 10 \\
                      -d horizontal --dxf output.dxf --png output.png
    """
    # Normalize direction
    if direction in ('h', 'horizontal'):
        direction = 'horizontal'
    elif direction in ('v', 'vertical'):
        direction = 'vertical'

    # Create parameters
    try:
        params = KerfParameters(
            material_width=width,
            material_height=height,
            material_thickness=thickness,
            kerf_width=kerf,
            cut_spacing=spacing,
            cut_length=length,
            cut_offset=offset,
            pattern_direction=direction,
            material_name=material_name,
        )
    except ValueError as e:
        click.echo(f"❌ Invalid parameters:", err=True)
        click.echo(f"   {e}", err=True)
        sys.exit(1)

    # Show info if requested
    if show_info:
        click.echo()
        print_pattern_info(params)
        click.echo()

    # Determine outputs
    if output_dir and name:
        # Use export_all for directory + name
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        click.echo("Generating pattern...")
        lines = generate_living_hinge(params)

        files = export_all(lines, params, output_dir, name)

        click.echo(f"✓ Generated {len(lines)} cuts")
        click.echo(f"✓ Exported files:")
        for fmt, path in files.items():
            click.echo(f"  • {fmt.upper()}: {path}")
    else:
        # Individual file outputs
        if not any([dxf, png, svg]):
            click.echo("❌ Error: Specify at least one output (--dxf, --png, --svg)", err=True)
            click.echo("   Or use --output-dir with --name for all formats", err=True)
            sys.exit(1)

        click.echo("Generating pattern...")
        lines = generate_living_hinge(params, dxf, png, svg)

        click.echo(f"✓ Generated {len(lines)} cuts")
        if dxf:
            click.echo(f"✓ DXF saved to: {dxf}")
        if png:
            click.echo(f"✓ PNG saved to: {png}")
        if svg:
            click.echo(f"✓ SVG saved to: {svg}")


@cli.command()
def interactive():
    """
    Interactive wizard for generating patterns.

    Asks questions and generates a pattern based on your answers.
    """
    click.echo("=" * 60)
    click.echo("Kerf Pattern Generator - Interactive Mode")
    click.echo("=" * 60)
    click.echo()

    # Gather parameters
    width = click.prompt("Material width (mm)", type=float)
    height = click.prompt("Material height (mm)", type=float)
    thickness = click.prompt("Material thickness (mm)", type=float)
    kerf = click.prompt("Laser kerf width (mm)", type=float, default=0.2)

    click.echo()
    click.echo("Cut pattern settings:")
    spacing = click.prompt("  Spacing between cuts (mm)", type=float)
    length = click.prompt("  Length of each cut (mm)", type=float)
    offset = click.prompt("  Edge offset (mm)", type=float, default=10)

    direction = click.prompt(
        "  Cut direction",
        type=click.Choice(['horizontal', 'vertical', 'h', 'v']),
        default='horizontal'
    )
    if direction in ('h', 'horizontal'):
        direction = 'horizontal'
    else:
        direction = 'vertical'

    click.echo()
    material_name = click.prompt("Material name (optional, press Enter to skip)",
                                 type=str, default="", show_default=False)

    # Create parameters
    try:
        params = KerfParameters(
            material_width=width,
            material_height=height,
            material_thickness=thickness,
            kerf_width=kerf,
            cut_spacing=spacing,
            cut_length=length,
            cut_offset=offset,
            pattern_direction=direction,
            material_name=material_name if material_name else None,
        )
    except ValueError as e:
        click.echo()
        click.echo(f"❌ Invalid parameters: {e}", err=True)
        sys.exit(1)

    # Show info
    click.echo()
    click.echo("=" * 60)
    print_pattern_info(params)
    click.echo("=" * 60)
    click.echo()

    # Confirm
    if not click.confirm("Generate pattern with these parameters?", default=True):
        click.echo("Cancelled.")
        return

    # Output files
    click.echo()
    base_name = click.prompt("Output filename (without extension)",
                            type=str, default="pattern")

    generate_preview = click.confirm("Generate PNG preview?", default=True)
    generate_svg = click.confirm("Generate SVG file?", default=False)

    # Generate
    click.echo()
    click.echo("Generating pattern...")

    dxf_path = f"{base_name}.dxf"
    png_path = f"{base_name}.png" if generate_preview else None
    svg_path = f"{base_name}.svg" if generate_svg else None

    lines = generate_living_hinge(params, dxf_path, png_path, svg_path)

    click.echo()
    click.echo(f"✓ Generated {len(lines)} cuts")
    click.echo(f"✓ DXF saved to: {dxf_path}")
    if png_path:
        click.echo(f"✓ PNG saved to: {png_path}")
    if svg_path:
        click.echo(f"✓ SVG saved to: {svg_path}")
    click.echo()
    click.echo("Done! Import the DXF into Lightburn or Fusion 360.")


@cli.command(name="calc-spacing")
@click.option('--radius', '-r', type=float, required=True,
              help='Target bend radius in mm')
@click.option('--thickness', '-t', type=float, required=True,
              help='Material thickness in mm')
@click.option('--kerf', '-k', type=float, required=True,
              help='Laser kerf width in mm')
def calc_spacing(radius, thickness, kerf):
    """
    Calculate required spacing for a target bend radius.

    Example:
        kerf calc-spacing --radius 30 --thickness 3 --kerf 0.2
    """
    spacing = calculate_required_spacing(radius, thickness, kerf)

    click.echo()
    click.echo(f"Target bend radius: {radius} mm")
    click.echo(f"Material thickness: {thickness} mm")
    click.echo(f"Laser kerf: {kerf} mm")
    click.echo()
    click.echo(f"→ Required cut spacing: {spacing:.2f} mm")
    click.echo()

    # Show min spacing warning if needed
    min_spacing = calculate_minimum_spacing(thickness, kerf)
    if spacing < min_spacing:
        click.echo(f"⚠️  Warning: This spacing is below the recommended minimum ({min_spacing:.2f} mm)")
        click.echo(f"   Risk of material failure during cutting or bending.")
    else:
        click.echo(f"✓ This spacing is safe (minimum: {min_spacing:.2f} mm)")


@cli.command(name="calc-radius")
@click.option('--spacing', '-s', type=float, required=True,
              help='Cut spacing in mm')
@click.option('--thickness', '-t', type=float, required=True,
              help='Material thickness in mm')
@click.option('--kerf', '-k', type=float, required=True,
              help='Laser kerf width in mm')
@click.option('--length', '-l', type=float, default=100,
              help='Cut length in mm (default: 100)')
def calc_radius(spacing, thickness, kerf, length):
    """
    Calculate bend radius from cut spacing.

    Example:
        kerf calc-radius --spacing 5 --thickness 3 --kerf 0.2
    """
    radius = calculate_bend_radius(thickness, spacing, kerf, length)

    click.echo()
    click.echo(f"Cut spacing: {spacing} mm")
    click.echo(f"Material thickness: {thickness} mm")
    click.echo(f"Laser kerf: {kerf} mm")
    click.echo()
    click.echo(f"→ Estimated bend radius: {radius:.2f} mm")
    click.echo()

    # Show min spacing info
    min_spacing = calculate_minimum_spacing(thickness, kerf)
    if spacing < min_spacing:
        click.echo(f"⚠️  Warning: This spacing is below the recommended minimum ({min_spacing:.2f} mm)")
    else:
        click.echo(f"✓ Spacing is safe (minimum: {min_spacing:.2f} mm)")


@cli.command()
@click.argument('params_file', type=click.Path(exists=True), required=False)
@click.option('--width', '-w', type=float, help='Material width in mm')
@click.option('--height', '-h', type=float, help='Material height in mm')
@click.option('--thickness', '-t', type=float, help='Material thickness in mm')
@click.option('--kerf', '-k', type=float, help='Laser kerf width in mm')
@click.option('--spacing', '-s', type=float, help='Cut spacing in mm')
@click.option('--length', '-l', type=float, help='Cut length in mm')
@click.option('--offset', '-o', type=float, help='Edge offset in mm')
@click.option('--direction', '-d', type=click.Choice(['horizontal', 'vertical']),
              help='Cut direction')
def info(params_file, width, height, thickness, kerf, spacing, length, offset, direction):
    """
    Show information about pattern parameters.

    Can read from parameters or calculate on-the-fly.

    Example:
        kerf info --spacing 5 --thickness 3 --kerf 0.2
    """
    if params_file:
        click.echo(f"Reading parameters from: {params_file}")
        # TODO: Implement reading from saved params file
        click.echo("(File reading not yet implemented)")
        return

    # Need at least some parameters
    if not all([width, height, thickness, kerf, spacing, length]):
        # Partial info - just show calculations
        if thickness and kerf and spacing:
            radius = calculate_bend_radius(thickness, spacing, kerf, length or 100)
            min_spacing = calculate_minimum_spacing(thickness, kerf)

            click.echo()
            click.echo(f"Material thickness: {thickness} mm")
            click.echo(f"Cut spacing: {spacing} mm")
            click.echo(f"Laser kerf: {kerf} mm")
            click.echo()
            click.echo(f"→ Bend radius: {radius:.2f} mm")
            click.echo(f"→ Minimum safe spacing: {min_spacing:.2f} mm")
            if spacing < min_spacing:
                click.echo(f"   ⚠️  Current spacing is below minimum!")
            click.echo()
        else:
            click.echo("❌ Error: Not enough parameters provided", err=True)
            click.echo("   Need at least: --thickness, --kerf, --spacing", err=True)
            click.echo("   Or provide all parameters for full info", err=True)
            sys.exit(1)
        return

    # Full parameters - create and show full info
    direction = direction or 'horizontal'
    offset = offset or 10

    try:
        params = KerfParameters(
            material_width=width,
            material_height=height,
            material_thickness=thickness,
            kerf_width=kerf,
            cut_spacing=spacing,
            cut_length=length,
            cut_offset=offset,
            pattern_direction=direction,
        )
    except ValueError as e:
        click.echo(f"❌ Invalid parameters: {e}", err=True)
        sys.exit(1)

    click.echo()
    print_pattern_info(params)
    click.echo()


def main():
    """Entry point for CLI."""
    cli()


if __name__ == '__main__':
    main()
