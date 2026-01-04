"""Tests for Phase 4.2: Graceful Degradation and Partial Success (Task Group 4.2)."""

import pytest
from scraper.extraction import ExtractionEngine
from scraper.models import SiteConfig


class TestPartialExtractionHandling:
    """Test extraction engine handles partial failures gracefully."""

    def test_some_fields_missing_others_found(self, temp_dir):
        """Test extraction when some fields found, others missing."""
        html_content = """
<html>
<body>
    <h1 class="name">Test Facility</h1>
    <span class="location">Test Location</span>
    <!-- Missing: expertise, url, contact -->
</body>
</html>
"""

        site_config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="fablab",
            priority_fields={
                "name": "h1.name",
                "location": "span.location",
                "expertise": "div.expertise",
                "url": "a.website",
                "contact": "span.contact",
            },
        )

        engine = ExtractionEngine()
        result = engine.extract_fields(html_content, site_config)

        # Should extract what's available
        assert "name" in result.priority_fields
        assert "location" in result.priority_fields
        assert "expertise" not in result.priority_fields

        # Should track missing fields
        assert "expertise" in result.fields_status.not_found
        assert "url" in result.fields_status.not_found
        assert "contact" in result.fields_status.not_found

        # Should still return success=True because some fields extracted
        assert result.success is True

    def test_all_priority_fields_missing(self):
        """Test extraction fails gracefully when all priority fields missing."""
        html_content = "<html><body><p>No extractable data</p></body></html>"

        site_config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="fablab",
            priority_fields={
                "name": "h1.name",
                "location": "span.location",
                "expertise": "div.expertise",
                "url": "a.website",
                "contact": "span.contact",
            },
        )

        engine = ExtractionEngine()
        result = engine.extract_fields(html_content, site_config)

        # Should return success=False since no fields extracted
        assert result.success is False
        assert result.metadata.failure_reason == "no_fields_extracted"

        # All fields should be marked not_found
        assert len(result.fields_status.not_found) == 5

    def test_extra_fields_dont_affect_success(self):
        """Test extra fields missing don't affect success determination."""
        html_content = """
<html>
<body>
    <h1 class="name">Test Facility</h1>
    <span class="location">Test Location</span>
    <!-- Missing extra fields -->
</body>
</html>
"""

        site_config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="fablab",
            priority_fields={
                "name": "h1.name",
                "location": "span.location",
            },
            extra_fields={
                "operating_hours": "div.hours",
                "equipment": "ul.equipment",
            },
        )

        engine = ExtractionEngine()
        result = engine.extract_fields(html_content, site_config)

        # Should be successful because priority fields present
        assert result.success is True
        # Extra fields should be in not_found
        assert "operating_hours" in result.fields_status.not_found
        assert "equipment" in result.fields_status.not_found


class TestFieldLevelErrorHandling:
    """Test extraction continues even when individual field extraction fails."""

    def test_invalid_selector_continues_extraction(self):
        """Test extraction continues when one field has invalid selector."""
        html_content = """
<html>
<body>
    <h1 class="name">Test Facility</h1>
    <span class="location">Test Location</span>
    <div class="expertise">Expertise: 3D Printing</div>
</body>
</html>
"""

        site_config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="fablab",
            priority_fields={
                "name": "h1.name",
                "location": "span.location",
                "expertise": "div.expertise",
                "url": "a.nonexistent",  # Invalid selector
                "contact": "span.contact",
            },
        )

        engine = ExtractionEngine()
        result = engine.extract_fields(html_content, site_config)

        # Should extract valid fields
        assert "name" in result.priority_fields
        assert "location" in result.priority_fields
        assert "expertise" in result.priority_fields

        # Failed fields should be tracked
        assert "url" in result.fields_status.not_found or "url" in result.fields_status.failed
        assert (
            "contact" in result.fields_status.not_found or "contact" in result.fields_status.failed
        )

        # Extraction should still be considered successful
        assert result.success is True

    def test_error_in_one_extra_field_doesnt_stop_others(self):
        """Test error extracting one extra field doesn't stop other extras."""
        html_content = """
<html>
<body>
    <h1 class="name">Test Facility</h1>
    <span class="location">Test Location</span>
    <span class="contact">contact@test.com</span>
    <div class="hours">9am-5pm</div>
    <!-- Missing: equipment -->
</body>
</html>
"""

        site_config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="fablab",
            priority_fields={
                "name": "h1.name",
                "location": "span.location",
                "expertise": "div.expertise",
                "url": "a.website",
                "contact": "span.contact",
            },
            extra_fields={
                "operating_hours": "div.hours",
                "equipment": "ul.equipment",
            },
        )

        engine = ExtractionEngine()
        result = engine.extract_fields(html_content, site_config)

        # Should extract operating_hours
        assert "operating_hours" in result.extra_metadata
        # Equipment extraction should fail gracefully
        assert (
            "equipment" in result.fields_status.not_found
            or "equipment" in result.fields_status.failed
        )


class TestPartialSuccessTracking:
    """Test field status accurately tracks partial successes."""

    def test_fields_status_extracted_list(self):
        """Test fields_status.extracted contains only successfully extracted fields."""
        html_content = """
<html>
<body>
    <h1 class="name">Test Facility</h1>
    <span class="location">Test Location</span>
</body>
</html>
"""

        site_config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="fablab",
            priority_fields={
                "name": "h1.name",
                "location": "span.location",
                "expertise": "div.expertise",
            },
        )

        engine = ExtractionEngine()
        result = engine.extract_fields(html_content, site_config)

        assert "name" in result.fields_status.extracted
        assert "location" in result.fields_status.extracted
        assert "expertise" not in result.fields_status.extracted

    def test_fields_status_not_found_list(self):
        """Test fields_status.not_found contains unmatched fields."""
        html_content = """
<html>
<body>
    <h1 class="name">Test Facility</h1>
</body>
</html>
"""

        site_config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="fablab",
            priority_fields={
                "name": "h1.name",
                "location": "span.location",
                "expertise": "div.expertise",
            },
        )

        engine = ExtractionEngine()
        result = engine.extract_fields(html_content, site_config)

        assert "location" in result.fields_status.not_found
        assert "expertise" in result.fields_status.not_found

    def test_fields_status_complete_after_partial_extraction(self):
        """Test all fields accounted for in status after partial extraction."""
        html_content = """
<html>
<body>
    <h1 class="name">Test Facility</h1>
    <span class="location">Test Location</span>
</body>
</html>
"""

        site_config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="fablab",
            priority_fields={
                "name": "h1.name",
                "location": "span.location",
                "expertise": "div.expertise",
                "url": "a.website",
                "contact": "span.contact",
            },
        )

        engine = ExtractionEngine()
        result = engine.extract_fields(html_content, site_config)

        # All fields should be accounted for
        all_fields = set(site_config.priority_fields.keys())
        accounted_for = (
            set(result.fields_status.extracted)
            | set(result.fields_status.failed)
            | set(result.fields_status.not_found)
        )

        # Every field should be in exactly one status category
        for field_name in all_fields:
            counts = sum(
                [
                    field_name in result.fields_status.extracted,
                    field_name in result.fields_status.failed,
                    field_name in result.fields_status.not_found,
                ]
            )
            # Each field should be in exactly one status list
            assert counts == 1, f"Field {field_name} not in exactly one status list"
