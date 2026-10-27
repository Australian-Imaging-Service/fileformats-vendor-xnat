# Implement 'extras' for the formats defined in
# fileformats.vendor.australianimagingservice.medimage here, see
# https://arcanaframework.github.io/fileformats/developer/extras.html

import shutil
import typing as ty
from pathlib import Path

from fileformats.core import converter
from fileformats.medimage import DicomCollection
from fileformats.medimage.dicom import dicom_sort_key
from pydra.compose import python

from fileformats.vendor.australianimagingservice.medimage import (
    DicomSample,
)


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
