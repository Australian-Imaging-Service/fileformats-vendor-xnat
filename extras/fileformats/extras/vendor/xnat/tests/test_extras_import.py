def test_extras_pkg_import():

    import fileformats.extras.vendor.xnat

    assert fileformats.extras.vendor.xnat.__name__ == "fileformats.extras.vendor.xnat"
