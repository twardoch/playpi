"""Test suite for playpi."""


def test_version():
    """Verify package exposes version."""
    import playpi

    assert playpi.__version__
