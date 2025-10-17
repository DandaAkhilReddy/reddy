"""
Test Step 7: JSON Extraction
"""
import pytest
from services.json_extractor import JSONExtractor, ExtractionStrategy


class TestJSONExtractor:
    """Test multi-strategy JSON extraction"""

    def setup_method(self):
        self.extractor = JSONExtractor()

    def test_strategy_direct_clean_json(self):
        """Test Strategy 1: Direct parse with clean JSON"""
        response = '{"chest_circumference_cm": 100, "waist_circumference_cm": 85}'
        result, strategy = self.extractor.extract(response)

        assert result is not None
        assert strategy == ExtractionStrategy.DIRECT
        assert result["chest_circumference_cm"] == 100
        assert result["waist_circumference_cm"] == 85

    def test_strategy_markdown_strip(self):
        """Test Strategy 2: Strip markdown code blocks"""
        response = '''```json
{
  "chest_circumference_cm": 100,
  "waist_circumference_cm": 85
}
```'''
        result, strategy = self.extractor.extract(response)

        assert result is not None
        assert strategy == ExtractionStrategy.MARKDOWN_STRIP
        assert result["chest_circumference_cm"] == 100

    def test_strategy_markdown_strip_no_json_tag(self):
        """Test Strategy 2: Markdown without 'json' tag"""
        response = '''```
{"chest_circumference_cm": 100, "waist_circumference_cm": 85}
```'''
        result, strategy = self.extractor.extract(response)

        assert result is not None
        assert strategy == ExtractionStrategy.MARKDOWN_STRIP

    def test_strategy_regex_extract(self):
        """Test Strategy 3: Regex extraction with surrounding text"""
        response = '''Here are the measurements:
{"chest_circumference_cm": 100, "waist_circumference_cm": 85}
These values were extracted from the images.'''
        result, strategy = self.extractor.extract(response)

        assert result is not None
        assert strategy == ExtractionStrategy.REGEX_EXTRACT
        assert result["chest_circumference_cm"] == 100

    def test_strategy_error_fix_trailing_comma(self):
        """Test Strategy 4: Fix trailing comma"""
        response = '{"chest_circumference_cm": 100, "waist_circumference_cm": 85,}'
        result, strategy = self.extractor.extract(response)

        assert result is not None
        assert strategy == ExtractionStrategy.ERROR_FIX
        assert result["chest_circumference_cm"] == 100

    def test_all_strategies_fail(self):
        """Test when all strategies fail"""
        response = 'This is not JSON at all, just random text'
        result, strategy = self.extractor.extract(response)

        assert result is None
        assert strategy is None

    def test_nested_json(self):
        """Test extraction with nested objects"""
        response = '''```json
{
  "chest_circumference_cm": 100,
  "waist_circumference_cm": 85,
  "metadata": {
    "confidence": 0.95
  }
}
```'''
        result, strategy = self.extractor.extract(response)

        assert result is not None
        assert "metadata" in result
        assert result["metadata"]["confidence"] == 0.95

    def test_array_in_json(self):
        """Test extraction with arrays"""
        response = '{"measurements": [100, 85, 95], "count": 3}'
        result, strategy = self.extractor.extract(response)

        assert result is not None
        assert result["measurements"] == [100, 85, 95]
        assert result["count"] == 3

    def test_empty_response(self):
        """Test with empty response"""
        response = ''
        result, strategy = self.extractor.extract(response)

        assert result is None

    def test_only_whitespace(self):
        """Test with only whitespace"""
        response = '   \n\n\t  '
        result, strategy = self.extractor.extract(response)

        assert result is None
