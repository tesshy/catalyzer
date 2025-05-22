import unittest
from unittest.mock import patch, MagicMock
from cabinet.services.markdown_service import get_markdown_service, MarkdownService, _MARKDOWN_SERVICE_INSTANCE

print("Testing dependency injection...")

# 最初のインスタンスを取得
original_instance = get_markdown_service()
print(f"Original instance ID: {id(original_instance)}")

# 2回目の呼び出しで同じインスタンスが返ってくるか確認
second_instance = get_markdown_service()
print(f"Second instance ID: {id(second_instance)}")
print(f"Same instance? {original_instance is second_instance}")

# グローバル変数のパッチをあてる
with patch('cabinet.services.markdown_service._MARKDOWN_SERVICE_INSTANCE') as mock_instance:
    mock_service = MagicMock(spec=MarkdownService)
    mock_instance.return_value = mock_service
    
    # この時点ではまだパッチは無効（グローバル変数に直接パッチを当てても意味がない）
    injected_instance = get_markdown_service()
    print(f"Injected instance is mock? {injected_instance is mock_service}")

# 正しいパッチ方法: 関数自体をパッチする
with patch('cabinet.services.markdown_service.get_markdown_service') as mock_get_service:
    mock_service = MagicMock(spec=MarkdownService)
    mock_get_service.return_value = mock_service
    
    # これで正しく差し替えられる
    print("After correct patching:")
    print(f"get_markdown_service() returns mock? {get_markdown_service() is mock_service}")
    
    # オリジナルの関数は変わらない
    print(f"Original instance still accessible? {original_instance is _MARKDOWN_SERVICE_INSTANCE}")

print("Test complete!")
