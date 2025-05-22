from unittest.mock import Mock
import re
import yaml
from markitdown._base_converter import DocumentConverterResult
from cabinet.services.markdown_service import MarkdownService

# モックのmarkitdownインスタンスを作成
mock_markitdown = Mock()
mock_markitdown.convert_url.return_value = DocumentConverterResult(
    markdown="# Test Title\n\nThis is test content.",
    title="Test Title"
)

# テスト対象のサービス
service = MarkdownService(markitdown_instance=mock_markitdown)

# 変換を実行
result = service.convert_url_to_markdown("https://example.com")

# markitdownが正しく呼ばれたことを確認
assert mock_markitdown.convert_url.call_count == 1
assert mock_markitdown.convert_url.call_args[0][0] == "https://example.com"

# 出力をチェック
pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
match = re.match(pattern, result, re.DOTALL)
assert match is not None, "Result should contain frontmatter"

frontmatter_str, main_content = match.groups()
frontmatter = yaml.safe_load(frontmatter_str)

# フロントマターのフィールドを確認
assert "title" in frontmatter
assert frontmatter["title"] == "Test Title"
assert "url" in frontmatter
assert frontmatter["url"] == "https://example.com"
assert "tags" in frontmatter
assert isinstance(frontmatter["tags"], list)
assert "locations" in frontmatter
assert frontmatter["locations"] == ["https://example.com"]
assert "created_at" in frontmatter
assert "updated_at" in frontmatter

# マークダウン内容を確認
assert "# Test Title" in main_content
assert "This is test content." in main_content

print("All tests passed!")
