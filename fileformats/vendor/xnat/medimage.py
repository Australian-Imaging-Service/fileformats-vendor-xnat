from fileformats.medimage import DicomImage


class DicomSample(DicomImage):
    """An extracted DICOM slice to be stored alongside a DICOM zip
    archive so its metadata can be extracted"""

    ext = None
