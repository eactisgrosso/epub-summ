import os
import argparse
from pathlib import Path
from langchain_core.documents import Document
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
MODEL = os.environ['MODEL']

LOWERCASE_WORDS = {"in", "with", "the", "a", "an", "and", "but", "or", "nor", "for", "on", "at", "to", "by", "from", "of", "not"}

def should_include_title(title):
    exclude_words = ["contents", "guide", "dedication", "preface", "acknowledgments", "outline", "revision", "who should read", "references", "o’reilly", "how to contact us"]
    return not any(title.lower().startswith(word) for word in exclude_words)

def correct_case(title):
    words = title.split('_')
    corrected_words = []
    for i, word in enumerate(words):
        if i == 0 or word.lower() not in LOWERCASE_WORDS:
            corrected_words.append(word.capitalize())
        else:
            corrected_words.append(word.lower())
    return ' '.join(corrected_words)

def create_book_dir(path):
    book_name = os.path.splitext(os.path.basename(path))[0]
    book_dir = os.path.join(os.getcwd(), "books", book_name)
    os.makedirs(book_dir, exist_ok=True)
    return book_dir

def summarize_chapter(chapter_text, prompt_text):
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name=MODEL,
        chunk_size=10000,
        chunk_overlap=100,
    )
    docs = text_splitter.create_documents([chapter_text])

    llm = ChatOpenAI(model=MODEL, temperature=0, openai_api_key=OPENAI_API_KEY)
    prompt = ChatPromptTemplate.from_messages(
        [("system", prompt_text)]
    )
    chain = create_stuff_documents_chain(llm, prompt)
    
    summary = ""
    for token in chain.stream({"context": docs}):
        summary += token
        print(token, end="", flush=True)  
    
    return summary

def extract_chapters(path):
    metadata = {
        "source": str(path.name),
        "path": str(path),
        "created": path.stat().st_ctime,
        "last_modified": path.stat().st_mtime,
        "last_accessed": path.stat().st_atime
    }
    with open(str(path), encoding="UTF-8") as f:
        text = f.read()
        
    doc = Document(page_content=text, metadata=metadata)
    
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "Header 1"),
            ("##", "Header 2")
        ]
    )

    chapters = []
    sections = markdown_splitter.split_text(doc.page_content)
    for section in sections:
        section.metadata.update(doc.metadata)  
        if "Header 1" in section.metadata:
           section.metadata["Title"] = section.metadata["Header 1"] 
        elif "Header 2" in section.metadata:
           section.metadata["Title"] = section.metadata["Header 2"] 
        
        title = section.metadata.get("Title", "").strip()
        if title and should_include_title(title):
            existing_chapter = next((chapter for chapter in chapters if chapter.metadata["Title"] == title), None)
            if existing_chapter:
                existing_chapter.page_content += "\n\n" + section.page_content
            else:
                chapters.append(section)
    return chapters

def list_chapters(path):
    chapters = extract_chapters(path)
    for i, chapter in enumerate(chapters, 1):
        chapter_title = correct_case(chapter.metadata["Title"].replace(' ', '_'))
        print(f"{i}. {chapter_title}")

def summarize(path, chapter_number=None):    
    book_dir = create_book_dir(path)
    chapters = extract_chapters(path)

    with open("prompt.txt" , 'r', encoding='utf-8') as file:
        prompt_text = file.read()
    
    for i, chapter in enumerate(chapters, 1):
        chapter_title = correct_case(chapter.metadata["Title"].replace(' ', '_'))

        if chapter_number and chapter_number != i:
            continue
        
        print(f"Summarizing: {chapter_title}")

        summary = summarize_chapter(chapter.page_content, prompt_text)

        chapter_file_name = f"Chapter_{i}_{chapter_title.replace(' ', '_')}.md"
        chapter_path = os.path.join(book_dir, chapter_file_name)

        with open(chapter_path, 'w', encoding='utf-8') as f:
            f.write(f"# {chapter_title}\n\n")
            f.write(summary)

        print(f"\n\nSaved summary to: {chapter_path}\n")
        
        if not chapter_number:
            continue_summarizing = input("Do you want to continue with the next chapter? (y/n):")
            if continue_summarizing != 'y':
                break
        
    print("\nSummarization complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tool for managing and summarizing Markdown files.")
    parser.add_argument("--list-chapters", type=str, help="List all chapters in the Markdown file")
    parser.add_argument("--summarize", type=str, help="Summarize one or all chapters from the Markdown file")
    parser.add_argument("--chapter", type=int, help="Number of the specific chapter to summarize")

    args = parser.parse_args()

    if args.list_chapters:
        list_chapters(Path(args.list_chapters))
    elif args.summarize:
        summarize(Path(args.summarize), args.chapter)
    else:
        parser.print_help()
