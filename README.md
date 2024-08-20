# EPUB Summarizer

This repository provides tools to convert EPUB files into Markdown format and then summarize them using OpenAI's models. The project consists of two main scripts: `convert.py` and `summarize.py`.

## Features

- **Convert EPUB to Markdown**: Extracts text from an EPUB file and converts it to Markdown format.
- **List Chapters in Markdown**: Lists all chapters from the Markdown file.
- **Summarize Markdown**: Summarizes the content of a Markdown file, breaking it down into chapters, and generates concise summaries using GPT-based models.

## Prerequisites

### 1. Install Dependencies

Install the required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

### 2. Set the env variables

Create an .env file in the root of the project directory with your OpenAI API key and model:

```bash
OPENAI_API_KEY=your_openai_api_key_here
MODEL=gpt-4o-mini
```

## Usage
### 1. Convert an EPUB File to Markdown

Use the `convert.py` script to convert an EPUB file to Markdown format:

```bash
python convert.py /path/to/your.epub
```

### 2. List Chapters in a Markdown File

Use the `markdown.py` script to list all chapters in the Markdown file:

```bash
python markdown.py --chapters /path/to/your_markdown.md
```

### 3. Summarize the Markdown File
#### Summarize All Chapters

You can summarize all chapters interactively using the following command:

```bash
python markdown.py --summarize /path/to/your_markdown.md
```

The script will ask for confirmation before summarizing each chapter.

#### Summarize a Specific Chapter

To summarize a specific chapter, use the `--chapter` flag:

```bash
python markdown.py --summarize /path/to/your_markdown.md --chapter 1
```


### 4. Modify the Summarization Prompt

You can customize the prompt used for summarization by editing the `prompt.txt` file. 



