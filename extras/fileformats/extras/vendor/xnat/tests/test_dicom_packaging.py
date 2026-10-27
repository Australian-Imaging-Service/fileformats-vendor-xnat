from pathlib import Path

import pydicom
import pytest
from fileformats.application import Zip
from fileformats.extras.vendor.xnat.medimage import (
    SampleDicomDir,
)
from fileformats.medimage import DicomDir, DicomImage, DicomSeries
from fileformats.vendor.xnat import DicomSample
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian


def test_directory_uses_generic_zip_and_vendor_sample() -> None:
    assert issubclass(DicomSample, DicomImage)
    zip_converter = Zip[DicomDir].get_converter(DicomDir)
    assert zip_converter is not None
    assert type(zip_converter.task).__name__ == "create_zip"
    sample_converter = DicomSample.get_converter(DicomDir)
    assert sample_converter is not None
    assert isinstance(sample_converter.task, SampleDicomDir)


def _dicom(path: Path, sop_instance_uid: str) -> None:
    meta = FileMetaDataset()
    meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.7"
    meta.MediaStorageSOPInstanceUID = sop_instance_uid
    meta.TransferSyntaxUID = ExplicitVRLittleEndian
    ds = Dataset()
    ds.file_meta = meta
    ds.SOPClassUID = meta.MediaStorageSOPClassUID
    ds.SOPInstanceUID = sop_instance_uid
    ds.StudyInstanceUID = "1.2.3"
    ds.SeriesInstanceUID = "1.2.3.4"
    ds.Modality = "OT"
    ds.is_little_endian = True
    ds.is_implicit_VR = False
    ds.save_as(path, write_like_original=False)


def test_sample_is_the_lowest_sop_instance_uid(
    work_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The sample is the same instance whatever order the collection gives its
    contents. The order is pinned to a wrong one here: in the field it came
    from a cache slot that the base class shares with the sorted DICOM
    properties (fixed in fileformats core), which made the natural
    reproduction depend on file times and the hash seed."""
    uids = {"a.dcm": "1.2.3.4.3", "b.dcm": "1.2.3.4.2", "c.dcm": "1.2.3.4.1"}
    for name, uid in uids.items():
        _dicom(work_dir / name, uid)
    wrong_order = [work_dir / name for name in ("b.dcm", "a.dcm", "c.dcm")]
    unsorted = property(lambda self: [DicomImage(path) for path in wrong_order])
    monkeypatch.setattr(DicomSeries, "contents", unsorted)
    monkeypatch.setattr(DicomDir, "contents", unsorted)

    for collection in (DicomSeries(wrong_order), DicomDir(work_dir)):
        assert collection.contents[0].fspath.name == "b.dcm"
        sample = DicomSample.convert(collection)
        assert sample.fspath.name == "c-sample"
        assert pydicom.dcmread(sample.fspath).SOPInstanceUID == "1.2.3.4.1"
