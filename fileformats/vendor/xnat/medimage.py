from fileformats.core import validated_property
from fileformats.image import Gif
from fileformats.medimage import DicomImage, MedicalImage


class DicomSample(DicomImage):
    """An extracted DICOM slice to be stored alongside a DICOM zip
    archive so its metadata can be extracted"""

    ext = None


class Snapshots(MedicalImage):
    """Snapshot images stored alongside a XNAT scan resource"""

    @validated_property
    def original_file(self) -> Gif:
        """The original snapshot file"""
        fspaths = [f for f in self.fspaths if f.name.endswith("_qc.gif")]
        if not fspaths:
            raise FileNotFoundError("No snapshot file ending with '_qc.gif' found")
        elif len(fspaths) > 1:
            raise FileExistsError(
                f"Multiple snapshot files ending with '_qc.gif' found: {fspaths}"
            )
        return Gif(fspaths[0])

    @property
    def content_labels(self) -> dict[str, str]:
        """The content XNAT catalogues each file under, by file name. XNAT serves a
        scan's snapshot and thumbnail from the files with ORIGINAL and THUMBNAIL
        content in its SNAPSHOTS resource"""
        return {
            self.original_file.fspath.name: "ORIGINAL",
            self.thumbnail_file.fspath.name: "THUMBNAIL",
        }

    @validated_property
    def thumbnail_file(self) -> Gif:
        """The thumbnail snapshot file"""
        fspaths = [f for f in self.fspaths if f.name.endswith("_qc_t.gif")]
        if not fspaths:
            raise FileNotFoundError("No snapshot file ending with '_qc_t.gif' found")
        elif len(fspaths) > 1:
            raise FileExistsError(
                f"Multiple snapshot files ending with '_qc_t.gif' found: {fspaths}"
            )
        return Gif(fspaths[0])
