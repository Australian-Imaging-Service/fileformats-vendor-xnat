from pathlib import Path

import pytest
from fileformats.extras.vendor.xnat import write_snapshots
from fileformats.extras.vendor.xnat.medimage import SnapshotPngs
from fileformats.generic import SetOf
from fileformats.image import Png
from fileformats.vendor.xnat import Snapshots
from PIL import Image

SIZES = [(40, 20), (30, 30), (20, 40), (40, 40), (10, 10)]
COLOURS = ["red", "green", "blue", "yellow", "white"]


def _pngs(work_dir: Path) -> SetOf[Png]:
    fspaths = []
    for i, (size, colour) in enumerate(zip(SIZES, COLOURS)):
        fspath = work_dir / f"image{i}.png"
        Image.new("RGB", size, colour).save(fspath)
        fspaths.append(fspath)
    return SetOf[Png](fspaths)


def test_snapshots_converter_is_registered() -> None:
    converter = Snapshots.get_converter(SetOf[Png])
    assert converter is not None
    assert isinstance(converter.task, SnapshotPngs)


def test_snapshots_tile_pngs_without_distortion(work_dir: Path) -> None:
    snapshots = Snapshots.convert(_pngs(work_dir))
    assert snapshots.original_file.fspath.name == "snapshot_qc.gif"
    assert snapshots.thumbnail_file.fspath.name == "snapshot_qc_t.gif"
    with Image.open(snapshots.original_file.fspath) as grid:
        # 5 images -> 3 columns x 2 rows of 40x40 cells
        assert grid.size == (120, 80)
        grid = grid.convert("RGB")
        # Each image is centred in its cell at its own size, so the cell around
        # the 40x20 first image is only filled in its middle 20 rows
        assert grid.getpixel((20, 20)) == (255, 0, 0)
        assert grid.getpixel((20, 5)) == (0, 0, 0)
        assert grid.getpixel((40 + 20, 20)) == (0, 128, 0)
        assert grid.getpixel((80 + 20, 20)) == (0, 0, 255)
        assert grid.getpixel((80 + 5, 20)) == (0, 0, 0)
        assert grid.getpixel((20, 40 + 20)) == (255, 255, 0)
        assert grid.getpixel((40 + 20, 40 + 20)) == (255, 255, 255)
        assert grid.getpixel((40 + 10, 40 + 10)) == (0, 0, 0)
        # The unused last cell is left empty
        assert grid.getpixel((80 + 20, 40 + 20)) == (0, 0, 0)


def test_snapshots_thumbnail_keeps_aspect_ratio(work_dir: Path) -> None:
    outputs = SnapshotPngs(in_file=_pngs(work_dir), thumbnail_size=60)(
        cache_root=work_dir / "cache"
    )
    snapshots = Snapshots(outputs.out_file)
    with Image.open(snapshots.thumbnail_file.fspath) as thumbnail:
        assert thumbnail.size == (60, 40)


def test_snapshots_tile_pngs_in_file_name_order(work_dir: Path) -> None:
    """The tiles follow the file names, not the order the paths were given in or
    their directories (merged resources can come from different directories)"""
    fspaths = []
    for dir_name, name, colour in [
        ("a", "c.png", "blue"),
        ("b", "a.png", "red"),
        ("c", "b.png", "green"),
    ]:
        (work_dir / dir_name).mkdir()
        fspath = work_dir / dir_name / name
        Image.new("RGB", (10, 10), colour).save(fspath)
        fspaths.append(fspath)
    snapshots = Snapshots.convert(SetOf[Png](fspaths))
    with Image.open(snapshots.original_file.fspath) as grid:
        # 3 images -> 2 columns x 2 rows
        grid = grid.convert("RGB")
        assert grid.getpixel((5, 5)) == (255, 0, 0)
        assert grid.getpixel((15, 5)) == (0, 128, 0)
        assert grid.getpixel((5, 15)) == (0, 0, 255)


def test_write_snapshots_tiles_in_given_order(work_dir: Path) -> None:
    images = [
        Image.new("RGB", (10, 10), "blue"),
        Image.new("L", (10, 10), 255),
        # Fully transparent, so flattened onto the black background
        Image.new("RGBA", (10, 10), (255, 0, 0, 0)),
    ]
    snapshots = write_snapshots(images, out_dir=work_dir / "out", stem="test")
    assert snapshots.original_file.fspath == work_dir / "out" / "test_qc.gif"
    with Image.open(snapshots.original_file.fspath) as grid:
        grid = grid.convert("RGB")
        assert grid.getpixel((5, 5)) == (0, 0, 255)
        assert grid.getpixel((15, 5)) == (255, 255, 255)
        assert grid.getpixel((5, 15)) == (0, 0, 0)


def test_write_snapshots_requires_images(work_dir: Path) -> None:
    with pytest.raises(ValueError, match="At least one image"):
        write_snapshots([], out_dir=work_dir)
