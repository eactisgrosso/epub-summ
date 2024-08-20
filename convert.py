import os
import re
import argparse
import ebooklib
from ebooklib import epub
import html2text

def epub_to_markdown(epub_path):
    book = epub.read_epub(epub_path)

    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    h.ignore_tables = True 
    h.bypass_tables = True
    h.wrap_links = False
    h.wrap_list_items = False
    h.single_line_break = True
    h.escape_snob = True
    h.protect_links = True
    h.body_width = 0

    markdown_content = ""
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            content = h.handle(item.content.decode('utf-8'))
            header_level = len(re.match(r'^(#+)', content).group(1)) if re.match(r'^(#+)', content) else None
            if header_level == 1 or header_level == 2:
                markdown_content += content

    books_dir = os.path.join(os.getcwd(), "books")
    os.makedirs(books_dir, exist_ok=True)

    file_name = os.path.splitext(os.path.basename(epub_path))[0]
    sanitized_file_name = file_name.replace(" ", "_")
    file_path = os.path.join(books_dir, f'{sanitized_file_name}.md')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"Markdown file saved to: {file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert EPUB to Markdown.")
    parser.add_argument("epub_path", type=str, help="Path to the EPUB file to convert")
    args = parser.parse_args()

    epub_to_markdown(args.epub_path)
