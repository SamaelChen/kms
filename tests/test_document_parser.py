"""Unit tests for document parser"""
import pytest
import tempfile
from pathlib import Path

from app.core.document_parser import DocumentParser


class TestDocumentParser:
    @pytest.fixture
    def parser(self):
        return DocumentParser()
    
    def test_parser_initialization(self, parser):
        assert parser is not None
        assert hasattr(parser, 'supported_extensions')
    
    def test_is_supported_txt(self, parser):
        assert parser.is_supported("document.txt") is True
        assert parser.is_supported("file.md") is True
    
    def test_is_supported_pdf(self, parser):
        assert parser.is_supported("document.pdf") is True
    
    def test_is_supported_docx(self, parser):
        assert parser.is_supported("document.docx") is True
    
    def test_is_supported_unsupported(self, parser):
        assert parser.is_supported("document.jpg") is False
        assert parser.is_supported("document.exe") is False
    
    def test_is_supported_case_insensitive(self, parser):
        assert parser.is_supported("DOCUMENT.PDF") is True
        assert parser.is_supported("File.TXT") is True
    
    def test_parse_txt_file(self, parser):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test document.")
            temp_path = f.name
        
        try:
            result = parser.parse(temp_path)
            assert "This is a test document." in result
        finally:
            Path(temp_path).unlink()
    
    def test_parse_empty_file(self, parser):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("")
            temp_path = f.name
        
        try:
            result = parser.parse(temp_path)
            assert result == ""
        finally:
            Path(temp_path).unlink()
    
    def test_parse_nonexistent_file(self, parser):
        result = parser.parse("/nonexistent/path/file.txt")
        assert result == ""
    
    def test_parse_unsupported_extension(self, parser):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
            f.write("Content")
            temp_path = f.name
        
        try:
            result = parser.parse(temp_path)
            assert result == ""
        finally:
            Path(temp_path).unlink()
    
    def test_clean_text_excessive_whitespace(self, parser):
        text = "Line 1\n\n\n\nLine 2"
        result = parser._clean_text(text)
        assert "\n\n\n" not in result
    
    def test_clean_text_unicode(self, parser):
        text = "Test with unicode: café, naïve, 中文"
        result = parser._clean_text(text)
        assert "café" in result
    
    def test_supported_extensions(self, parser):
        extensions = parser.supported_extensions
        assert 'txt' in extensions
        assert 'pdf' in extensions
        assert 'docx' in extensions
        assert 'md' in extensions
