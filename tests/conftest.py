"""Shared test fixtures and configuration."""

import pytest
from pathlib import Path
import tempfile
import json


@pytest.fixture
def temp_dir():
    """Provide temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config_toml():
    """Provide sample configuration TOML content."""
    return """
[scraper]
primary_library = "scrapling"
timeout_seconds = 30
max_retries = 3
retry_backoff_factor = 2.0

[[sites]]
id = "example-fablab"
url_pattern = "example-fablab.com"
site_type = "fablab"
description = "Example Fablab for testing"

[sites.fields.priority]
name = "h1.name"
location = "span.location"
expertise = "div.expertise"
url = "a.website"
contact = "span.contact"

[sites.fields.extra]
operating_hours = "div.hours"

[output]
format = "toml"
include_metadata = true
directory = "./output"
"""


@pytest.fixture
def sample_html():
    """Provide sample HTML for extraction testing."""
    return """
<html>
<head><title>Example Fablab</title></head>
<body>
    <h1 class="name">Example Fablab</h1>
    <span class="location">San Francisco, CA</span>
    <div class="expertise">3D printing, electronics, woodworking</div>
    <a class="website" href="https://example-fablab.com">Visit Website</a>
    <span class="contact">contact@example-fablab.com</span>
    <div class="hours">Mon-Fri 9am-6pm, Sat 10am-4pm</div>
</body>
</html>
"""


@pytest.fixture
def valid_url():
    """Provide a valid URL for testing."""
    return "https://example-fablab.com/about"


@pytest.fixture
def invalid_urls():
    """Provide invalid URLs for testing."""
    return [
        "not-a-url",
        "ftp://example.com",  # Invalid scheme
        "http://",  # Incomplete
        "",  # Empty
        "   ",  # Whitespace
    ]
