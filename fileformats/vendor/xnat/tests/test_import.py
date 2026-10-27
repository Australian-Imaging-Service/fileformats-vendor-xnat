def test_pkg_import():

    import fileformats.vendor.australianimagingservice

    assert (
        fileformats.vendor.australianimagingservice.__name__
        == "fileformats.vendor.australianimagingservice"
    )
