# Implement 'extras' for the formats defined in
# fileformats.vendor.xnat.medimage here, see
# https://arcanaframework.github.io/fileformats/developer/extras.html

import shutil
import typing as ty
from pathlib import Path

from fileformats.core import converter
from fileformats.generic import SetOf
from fileformats.image import Bitmap, Gif, Jpeg, Png, Tiff
from fileformats.medimage import DicomCollection
from fileformats.medimage.dicom import dicom_sort_key
from PIL import Image
from pydra.compose import python

from fileformats.vendor.xnat.medimage import (
    DicomSample,
    Snapshots,
)

from .snapshots import write_snapshots


@converter
@python.define(outputs=["out_file"])  # type: ignore[untyped-decorator]
def SampleDicomDir(
    in_file: DicomCollection,
    out_file: ty.Optional[Path] = None,
) -> DicomSample:
    """Copy one image of a DICOM collection: the instance with the lowest
    SOPInstanceUID, so the same collection gives the same sample every time.

    Packaging invokes the generic ZIP and sample converters from the same
    deidentified source, so the sampled bytes also occur in the archive.
    """
    # Not contents[0]: the collection's own order is not reliable. It comes
    # from a set of paths, and a reader of the base class can leave it cached
    # unsorted, so the first entry changed from one process to the next.
    sample = min(in_file.contents, key=dicom_sort_key)
    if out_file is None:
        out_file = Path.cwd() / f"{sample.stem}-sample"
    out_file = out_file.absolute()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(sample, out_file)
    return DicomSample(out_file)


@converter(source_format=Bitmap, target_format=Snapshots)  # type: ignore[untyped-decorator]
@converter(source_format=Gif, target_format=Snapshots)  # type: ignore[untyped-decorator]
@converter(source_format=Jpeg, target_format=Snapshots)  # type: ignore[untyped-decorator]
@converter(source_format=Png, target_format=Snapshots)  # type: ignore[untyped-decorator]
@converter(source_format=Tiff, target_format=Snapshots)  # type: ignore[untyped-decorator]
@converter(source_format=SetOf[Bitmap], target_format=Snapshots)  # type: ignore[untyped-decorator,misc]
@converter(source_format=SetOf[Gif], target_format=Snapshots)  # type: ignore[untyped-decorator,misc]
@converter(source_format=SetOf[Jpeg], target_format=Snapshots)  # type: ignore[untyped-decorator,misc]
@converter(source_format=SetOf[Png], target_format=Snapshots)  # type: ignore[untyped-decorator,misc]
@converter(source_format=SetOf[Tiff], target_format=Snapshots)  # type: ignore[untyped-decorator,misc]
@python.define(outputs=["out_file"])  # type: ignore[untyped-decorator]
def SnapshotImages(
    # On one line because mypy versions report the SetOf errors on different lines
    in_file: Bitmap | Gif | Jpeg | Png | Tiff | SetOf[Bitmap] | SetOf[Gif] | SetOf[Jpeg] | SetOf[Png] | SetOf[Tiff],  # type: ignore[type-arg]  # fmt: skip
    out_dir: ty.Optional[Path] = None,
    stem: str = "snapshot",
    thumbnail_size: int = 256,
) -> Snapshots:
    """Tile an image, or the images of a set in file-name order, into XNAT snapshots
    (see :func:`write_snapshots`)"""
    images = []
    for fspath in sorted(in_file.fspaths, key=lambda p: p.name):
        with Image.open(fspath) as image:
            image.load()
            images.append(image)
    return write_snapshots(
        images, out_dir=out_dir, stem=stem, thumbnail_size=thumbnail_size
    )
