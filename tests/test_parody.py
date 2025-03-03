import pytest
from src.parody import (
    article_to_md,
    clean_article_md,
    CleanArticle,
    DocumentConversionError,
    ArticleExtractionError
)
from unittest.mock import patch, MagicMock

def test_article_to_md():
    """Test article to markdown conversion"""
    with patch('src.parody.DocumentConverter') as mock_converter:
        mock_instance = MagicMock()
        mock_instance.convert.return_value.document.export_to_markdown.return_value = "# Test Article\n\nTest content"
        mock_converter.return_value = mock_instance
        
        result = article_to_md("https://example.com/article")
        assert result == "# Test Article\n\nTest content"
        mock_instance.convert.assert_called_once_with("https://example.com/article")

def test_article_to_md_error():
    """Test article to markdown conversion error handling"""
    with patch('src.parody.DocumentConverter') as mock_converter:
        mock_instance = MagicMock()
        mock_instance.convert.side_effect = Exception("Failed to fetch")
        mock_converter.return_value = mock_instance
        
        with pytest.raises(DocumentConversionError) as exc_info:
            article_to_md("https://example.com/article")
        assert "Failed to convert document" in str(exc_info.value)

def test_clean_article_md():
    """Test article cleaning with OpenAI"""
    mock_article = CleanArticle(
        title="Test Title",
        body="Test body content",
        author="Test Author"
    )
    
    with patch('src.parody.OpenAI') as mock_openai, \
         patch('src.parody.yaml.safe_load') as mock_yaml:
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices[0].message.parsed = mock_article
        mock_client.beta.chat.completions.parse.return_value = mock_completion
        mock_openai.return_value = mock_client
        mock_yaml.return_value = {'clean_article_md': 'test prompt'}
        
        result = clean_article_md("# Test\n\nContent")
        assert result == mock_article
        mock_client.beta.chat.completions.parse.assert_called_once()

def test_clean_article_md_error():
    """Test article cleaning error handling"""
    with patch('src.parody.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_client.beta.chat.completions.parse.side_effect = Exception("API error")
        mock_openai.return_value = mock_client
        
        with pytest.raises(ArticleExtractionError) as exc_info:
            clean_article_md("# Test\n\nContent")
        assert "Failed to clean article" in str(exc_info.value)

def test_clean_article_md_none_result():
    """Test article cleaning with None result"""
    with patch('src.parody.OpenAI') as mock_openai, \
         patch('src.parody.yaml.safe_load') as mock_yaml:
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices[0].message.parsed = None
        mock_client.beta.chat.completions.parse.return_value = mock_completion
        mock_openai.return_value = mock_client
        mock_yaml.return_value = {'clean_article_md': 'test prompt'}
        
        with pytest.raises(ArticleExtractionError) as exc_info:
            clean_article_md("# Test\n\nContent")
        assert "Failed to extract article data" in str(exc_info.value)
