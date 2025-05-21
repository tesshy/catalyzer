from markitdown import MarkItDown

url = "https://github.com/microsoft/markitdown"
markitdown = MarkItDown()
result = markitdown.convert_url(url)

print(f"Title: {result.title}")
print(f"Markdown Content:\n{result.markdown[:200]}...")  # 最初の200文字だけ表示