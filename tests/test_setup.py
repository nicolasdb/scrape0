"""Test that the project setup is working correctly."""


def test_imports():
    """Test that basic imports work."""
    import scraper

    assert scraper.__version__ == "0.1.0"


def test_pytest_working():
    """Verify pytest is functional."""
    assert True
