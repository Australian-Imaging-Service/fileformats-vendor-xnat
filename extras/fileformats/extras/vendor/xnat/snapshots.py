import math
import typing as ty
from pathlib import Path

from PIL import Image

from fileformats.vendor.xnat.medimage import Snapshots


def write_snapshots(
    images: ty.Sequence[Image.Image],
    out_dir: ty.Optional[Path] = None,
    stem: str = "snapshot",
    thumbnail_size: int = 256,
) -> Snapshots:
    """Tile images into a roughly square grid and save it as the original and
    thumbnail GIFs of XNAT snapshots. Converters to ``Snapshots`` from other formats
    only need to render their data as a list of images and pass it here.

    The images are tiled in the order given, row by row, each centred in a cell the
    size of the largest image so none of them is resized or distorted. Any
    transparency is flattened onto the black background of the grid. The thumbnail
    is the grid shrunk, keeping its aspect ratio, so its longest side is at most
    ``thumbnail_size`` pixels.

    Parameters
    ----------
    images : Sequence[PIL.Image.Image]
        the images to tile, in the order they should appear
    out_dir : Path, optional
        the directory to save the GIFs in, by default the current working directory
    stem : str, optional
        the stem of the GIF file names, '<stem>_qc.gif' and '<stem>_qc_t.gif'
    thumbnail_size : int, optional
        the maximum width and height of the thumbnail in pixels

    Returns
    -------
    Snapshots
        the original and thumbnail GIFs
    """
    if not images:
        raise ValueError("At least one image is needed to create snapshots")
    flattened = []
    for image in images:
        rgba = image.convert("RGBA")
        rgb = Image.new("RGB", rgba.size)
        rgb.paste(rgba, mask=rgba)
        flattened.append(rgb)
    n_cols = math.ceil(math.sqrt(len(flattened)))
    n_rows = math.ceil(len(flattened) / n_cols)
    cell_width = max(i.width for i in flattened)
    cell_height = max(i.height for i in flattened)
    grid = Image.new("RGB", (n_cols * cell_width, n_rows * cell_height))
    for index, image in enumerate(flattened):
        row, col = divmod(index, n_cols)
        grid.paste(
            image,
            (
                col * cell_width + (cell_width - image.width) // 2,
                row * cell_height + (cell_height - image.height) // 2,
            ),
        )
    thumbnail = grid.copy()
    thumbnail.thumbnail((thumbnail_size, thumbnail_size))
    if out_dir is None:
        out_dir = Path.cwd()
    out_dir = out_dir.absolute()
    out_dir.mkdir(parents=True, exist_ok=True)
    original_path = out_dir / f"{stem}_qc.gif"
    thumbnail_path = out_dir / f"{stem}_qc_t.gif"
    grid.quantize().save(original_path)
    thumbnail.quantize().save(thumbnail_path)
    return Snapshots([original_path, thumbnail_path])
