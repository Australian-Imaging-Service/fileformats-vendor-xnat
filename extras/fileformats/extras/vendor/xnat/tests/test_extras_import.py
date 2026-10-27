def test_extras_pkg_import():

    import fileformats.extras.vendor.australianimagingservice

    assert (
        fileformats.extras.vendor.australianimagingservice.__name__
        == "fileformats.extras.vendor.australianimagingservice"
    )
