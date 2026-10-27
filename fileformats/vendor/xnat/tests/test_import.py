def test_pkg_import():

    import fileformats.vendor.xnat

    assert fileformats.vendor.xnat.__name__ == "fileformats.vendor.xnat"
