# Local RAG — Streamlit + Ollama + ChromaDB

A modular, local-first document Q&A application for Windows 11. Supports PDF (including OCR for scanned pages), Word DOCX, TXT, Markdown, Excel XLSX/XLSM, and CSV. Document files, embeddings, and metadata remain on your computer. Ollama runs the chat and embedding models locally.

## Features

- Upload and index supported documents.
- Select individual documents or reusable collections for each chat.
- Persistent ChromaDB vector store and SQLite metadata.
- Source citations with filenames and PDF page numbers / spreadsheet sheet names.
- Configurable Ollama models, chunk size, overlap, top-K and temperature.
- PDF text extraction first, OCR fallback for pages with little or no text.
- Delete document records and corresponding vectors.
- Duplicate detection by SHA-256 hash.

## Requirements

- Windows 11, 64-bit Python 3.11 or 3.12 recommended.
- Ollama installed and running.
- Tesseract OCR installed for scanned PDFs. OCR is optional for text PDFs.

## 1. Install Ollama models

Open PowerShell:

```powershell
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
ollama list
```

The app uses `http://localhost:11434` by default. Ollama's local API is documented at https://ollama.com/ .

## 2. Install Tesseract OCR

Install 64-bit Tesseract OCR for Windows. A commonly used package-manager command is:

```powershell
winget install -e --id tesseract-ocr.tesseract
```

Open a new PowerShell window and verify:

```powershell
tesseract --version
```

If Tesseract is not on PATH, find `tesseract.exe` (often `C:\\Program Files\\Tesseract-OCR\\tesseract.exe`) and set `TESSERACT_CMD` in `.env`. OCR language defaults to `eng`; install the required language data for other languages.

This project uses PyMuPDF to render pages and `pytesseract` to run OCR. It does not require OCRmyPDF or Ghostscript.

## 3. Create the Python environment

Extract the project ZIP, open PowerShell in the `local-rag` directory, and run:

```powershell
py -3.12 -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

If `py -3.12` is unavailable, use an installed 64-bit Python version supported by the packages, then create the venv with `python -m venv .venv`.

## 4. Run

```powershell
streamlit run app.py
```

Streamlit will print a local URL, usually `http://localhost:8501`.

## How to use

1. Open **Documents**, upload files, and click **Index selected uploads**.
2. Open **Collections** to create a collection and assign documents to it.
3. Open **Chat**, select one or more documents and/or collections in the sidebar, and ask questions.
4. Inspect the source citations and retrieved excerpts below each answer.
5. Open **Settings** to tune chunking, retrieval count, threshold, temperature, and Ollama model names.

The selected document scope is enforced in ChromaDB's metadata filter. It is not merely a prompt instruction. When no sources are selected, the app does not search the library.

## Local data

- `data/uploads/`: uploaded original files
- `data/chroma/`: persistent vector database
- `data/app.db`: SQLite metadata and collections

Back up the `data` folder while the app is stopped. Do not commit it to source control.

## Notes and limitations

- PDF OCR is performed page-by-page only when extracted text is below the configured minimum. Large scanned PDFs may take time on a CPU.
- Excel sheets are converted to row-oriented text so retrieval can preserve column names alongside values. Very large workbooks may take time to index.
- CSV files are parsed with pandas and converted to row-oriented text.
- Password-protected PDFs, encrypted files, damaged files, handwriting, and complex tables may not parse reliably.
- This starter app is intended for local single-user use. It does not include authentication or multi-user isolation.
- Model answers can still be wrong; verify important answers against the cited passages.
