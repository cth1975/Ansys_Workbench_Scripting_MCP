#!/usr/bin/env python3
"""
Ansys Resource Processor

Processes downloaded Ansys documentation to extract useful content for MCP server.
Creates structured JSON files with searchable content.
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
import hashlib

# Try to import PDF processing libraries
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
RESOURCES_DIR = PROJECT_ROOT / "resources"
PDF_DIR = RESOURCES_DIR / "docs" / "pdf"
HTML_DIR = RESOURCES_DIR / "docs" / "html"
EXTRACTED_DIR = RESOURCES_DIR / "docs" / "extracted"
TEMPLATES_DIR = RESOURCES_DIR / "templates"

def ensure_dependencies():
    """Check and install required dependencies."""
    missing = []
    if not PDF_AVAILABLE:
        missing.append("PyPDF2")
    if not BS4_AVAILABLE:
        missing.append("beautifulsoup4")

    if missing:
        print(f"⚠️  Missing required dependencies: {', '.join(missing)}")
        print("Installing...")
        try:
            import subprocess
            for pkg in missing:
                subprocess.run([sys.executable, "-m", "pip", "install", pkg], check=True)
            print("✓ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    return True

def extract_text_from_pdf(pdf_path):
    """Extract text content from PDF file."""
    if not PDF_AVAILABLE:
        return None

    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text_content = []

            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    text = page.extract_text()
                    if text.strip():
                        text_content.append({
                            "page": page_num + 1,
                            "content": text.strip()
                        })
                except Exception as e:
                    print(f"   Warning: Could not extract page {page_num + 1}: {e}")
                    continue

            return text_content
    except Exception as e:
        print(f"   Error processing PDF: {e}")
        return None

def extract_code_examples(text):
    """Extract code examples from text content."""
    code_examples = []

    # Common patterns for code blocks in Ansys documentation
    patterns = [
        r'```python(.*?)```',
        r'```(.*?)```',
        r'>>> (.*?)(?=\n|$)',
        r'import ansys.*?(?=\n\n|\n[A-Z])',
        r'from ansys.*?(?=\n\n|\n[A-Z])',
    ]

    for i, pattern in enumerate(patterns):
        matches = re.finditer(pattern, text, re.DOTALL | re.MULTILINE)
        for match in matches:
            code = match.group(1) if i < 2 else match.group(0)
            if code.strip() and len(code.strip()) > 10:  # Filter out very short matches
                code_examples.append({
                    "code": code.strip(),
                    "pattern_type": f"pattern_{i+1}",
                    "language": "python" if "python" in pattern else "unknown"
                })

    return code_examples

def extract_api_references(text):
    """Extract API references and method signatures."""
    api_refs = []

    # Patterns for API references
    patterns = [
        r'ansys\.[a-zA-Z_][a-zA-Z0-9_.]*\([^)]*\)',  # Method calls
        r'ansys\.[a-zA-Z_][a-zA-Z0-9_.]*',            # Property/class references
        r'mechanical\.[a-zA-Z_][a-zA-Z0-9_.]*',       # Mechanical namespace
        r'workbench\.[a-zA-Z_][a-zA-Z0-9_.]*',        # Workbench namespace
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, text, re.MULTILINE)
        for match in matches:
            api_ref = match.group(0).strip()
            if api_ref and len(api_ref) > 5:  # Filter short matches
                api_refs.append({
                    "reference": api_ref,
                    "type": "method" if "(" in api_ref else "property"
                })

    # Remove duplicates
    seen = set()
    unique_refs = []
    for ref in api_refs:
        key = ref["reference"]
        if key not in seen:
            seen.add(key)
            unique_refs.append(ref)

    return unique_refs

def process_pdf(pdf_path):
    """Process a single PDF file."""
    print(f"📄 Processing {pdf_path.name}...")

    # Extract text content
    text_content = extract_text_from_pdf(pdf_path)
    if not text_content:
        print(f"   ✗ Could not extract text from {pdf_path.name}")
        return None

    # Combine all text for analysis
    full_text = "\n".join([page["content"] for page in text_content])

    # Extract structured information
    code_examples = extract_code_examples(full_text)
    api_references = extract_api_references(full_text)

    processed_data = {
        "source_file": pdf_path.name,
        "processed_date": datetime.now().isoformat(),
        "total_pages": len(text_content),
        "text_length": len(full_text),
        "summary": {
            "code_examples": len(code_examples),
            "api_references": len(api_references)
        },
        "content": {
            "pages": text_content[:5],  # First 5 pages for space
            "code_examples": code_examples[:20],  # Top 20 examples
            "api_references": api_references[:50]  # Top 50 API refs
        }
    }

    print(f"   ✓ Extracted {len(code_examples)} code examples, {len(api_references)} API references")
    return processed_data

def process_html_files(html_dir):
    """Process HTML documentation files."""
    if not BS4_AVAILABLE:
        print(f"   ⚠️  BeautifulSoup not available, skipping HTML processing")
        return None

    print(f"🌐 Processing HTML files in {html_dir.name}...")

    html_files = list(html_dir.rglob("*.html"))
    if not html_files:
        print(f"   ⚠️  No HTML files found in {html_dir}")
        return None

    processed_content = []
    for html_file in html_files[:10]:  # Process first 10 files for now
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')

                # Extract title and main content
                title = soup.find('title')
                title_text = title.get_text() if title else "Unknown"

                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()

                # Extract text content
                content = soup.get_text()

                # Clean up whitespace
                lines = (line.strip() for line in content.splitlines())
                content = '\n'.join(line for line in lines if line)

                if len(content) > 100:  # Only include substantial content
                    processed_content.append({
                        "file": str(html_file.relative_to(html_dir)),
                        "title": title_text.strip(),
                        "content": content[:2000],  # First 2000 chars
                        "length": len(content)
                    })

        except Exception as e:
            print(f"   Warning: Could not process {html_file}: {e}")
            continue

    print(f"   ✓ Processed {len(processed_content)} HTML files")
    return {
        "source_directory": html_dir.name,
        "processed_date": datetime.now().isoformat(),
        "total_files": len(html_files),
        "processed_files": len(processed_content),
        "content": processed_content
    }

def create_search_index(extracted_data):
    """Create a searchable index of all content."""
    search_index = {
        "created": datetime.now().isoformat(),
        "sources": [],
        "code_examples": [],
        "api_references": [],
        "content_by_topic": {}
    }

    for source, data in extracted_data.items():
        if data:
            search_index["sources"].append({
                "name": source,
                "type": "pdf" if source.endswith('.pdf') else "html",
                "summary": data.get("summary", {})
            })

            # Add code examples
            if "content" in data and "code_examples" in data["content"]:
                for example in data["content"]["code_examples"]:
                    search_index["code_examples"].append({
                        "source": source,
                        "code": example["code"],
                        "language": example.get("language", "unknown")
                    })

            # Add API references
            if "content" in data and "api_references" in data["content"]:
                for ref in data["content"]["api_references"]:
                    search_index["api_references"].append({
                        "source": source,
                        "reference": ref["reference"],
                        "type": ref["type"]
                    })

    return search_index

def main():
    """Main processing orchestrator."""
    print("🔧 Ansys Resource Processor")
    print("=" * 50)

    # Check dependencies
    if not ensure_dependencies():
        sys.exit(1)

    # Re-import after potential installation
    global PyPDF2, BeautifulSoup
    if not PDF_AVAILABLE:
        import PyPDF2
    if not BS4_AVAILABLE:
        from bs4 import BeautifulSoup

    # Ensure output directory
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)

    extracted_data = {}

    # Process PDFs
    print("\n📚 Processing PDF Documentation...")
    pdf_files = list(PDF_DIR.glob("*.pdf"))

    for pdf_file in pdf_files:
        if pdf_file.stat().st_size > 1000:  # Only process substantial files
            processed = process_pdf(pdf_file)
            if processed:
                extracted_data[pdf_file.name] = processed

                # Save individual processed file
                output_file = EXTRACTED_DIR / f"{pdf_file.stem}_processed.json"
                with open(output_file, 'w') as f:
                    json.dump(processed, f, indent=2)

    # Process HTML directories
    print("\n🌐 Processing HTML Documentation...")
    html_dirs = [d for d in HTML_DIR.iterdir() if d.is_dir()]

    for html_dir in html_dirs:
        processed = process_html_files(html_dir)
        if processed:
            extracted_data[html_dir.name] = processed

            # Save individual processed file
            output_file = EXTRACTED_DIR / f"{html_dir.name}_processed.json"
            with open(output_file, 'w') as f:
                json.dump(processed, f, indent=2)

    # Create search index
    print("\n🔍 Creating search index...")
    search_index = create_search_index(extracted_data)

    # Save search index
    index_file = EXTRACTED_DIR / "search_index.json"
    with open(index_file, 'w') as f:
        json.dump(search_index, f, indent=2)

    # Save complete extracted data
    complete_file = EXTRACTED_DIR / "complete_extracted_data.json"
    with open(complete_file, 'w') as f:
        json.dump(extracted_data, f, indent=2)

    # Summary
    print("\n" + "=" * 50)
    print("📋 Processing Summary:")
    print(f"   Sources processed: {len(extracted_data)}")
    print(f"   Code examples found: {len(search_index['code_examples'])}")
    print(f"   API references found: {len(search_index['api_references'])}")
    print(f"   Files created: {len(list(EXTRACTED_DIR.glob('*.json')))}")
    print("\n✅ Resource processing complete!")
    print(f"📁 Processed data stored in: {EXTRACTED_DIR}")

if __name__ == "__main__":
    main()