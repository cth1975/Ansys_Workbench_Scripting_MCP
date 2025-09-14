#!/usr/bin/env python3
"""
Enhanced PDF Content Extractor for Ansys Documentation

Uses PyMuPDF for robust text extraction from PDF manuals.
Extracts structured content with chapters, sections, and metadata.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import fitz  # PyMuPDF


class AnsysPDFExtractor:
    """Enhanced PDF extractor for Ansys documentation."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.pdf_dir = project_root / "resources" / "docs" / "pdf"
        self.output_dir = project_root / "resources" / "docs" / "extracted"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_text_from_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract structured text from a PDF file."""
        try:
            doc = fitz.open(pdf_path)
            content = {
                "file": pdf_path.name,
                "total_pages": len(doc),
                "extracted_date": datetime.now().isoformat(),
                "pages": [],
                "outline": [],
                "metadata": {}
            }

            # Extract document metadata
            metadata = doc.metadata
            content["metadata"] = {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "creation_date": metadata.get("creationDate", ""),
                "modification_date": metadata.get("modDate", "")
            }

            # Extract table of contents/outline
            try:
                toc = doc.get_toc()
                content["outline"] = self._process_outline(toc)
            except:
                content["outline"] = []

            # Extract text from each page
            for page_num in range(len(doc)):
                page = doc[page_num]

                # Extract text
                text = page.get_text()

                # Extract text blocks with formatting info
                blocks = page.get_text("dict")

                page_content = {
                    "page_number": page_num + 1,
                    "text": text,
                    "clean_text": self._clean_text(text),
                    "word_count": len(text.split()),
                    "blocks": self._process_text_blocks(blocks),
                    "sections": self._identify_sections(text)
                }

                content["pages"].append(page_content)

            doc.close()

            # Post-process: identify chapters and major sections
            content["chapters"] = self._extract_chapters(content)
            content["code_examples"] = self._extract_code_examples(content)
            content["api_references"] = self._extract_api_references(content)

            return content

        except Exception as e:
            print(f"Error extracting from {pdf_path}: {e}")
            return {
                "file": pdf_path.name,
                "error": str(e),
                "extracted_date": datetime.now().isoformat()
            }

    def _process_outline(self, toc: List) -> List[Dict]:
        """Process table of contents/outline."""
        processed_toc = []
        for item in toc:
            if len(item) >= 3:
                processed_toc.append({
                    "level": item[0],
                    "title": item[1],
                    "page": item[2]
                })
        return processed_toc

    def _process_text_blocks(self, blocks_dict: Dict) -> List[Dict]:
        """Process text blocks with formatting information."""
        processed_blocks = []

        if "blocks" in blocks_dict:
            for block in blocks_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        if "spans" in line:
                            for span in line["spans"]:
                                processed_blocks.append({
                                    "text": span.get("text", ""),
                                    "font": span.get("font", ""),
                                    "size": span.get("size", 0),
                                    "flags": span.get("flags", 0),
                                    "bbox": span.get("bbox", [])
                                })

        return processed_blocks

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove page headers/footers (common patterns)
        text = re.sub(r'Page \d+ of \d+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'ANSYS.*?Release \d+\.\d+', '', text, flags=re.IGNORECASE)

        # Remove excessive line breaks
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)

        return text.strip()

    def _identify_sections(self, text: str) -> List[Dict]:
        """Identify sections and subsections in the text."""
        sections = []

        # Common section patterns for Ansys documentation
        patterns = [
            r'^(\d+\.?\d*\.?\d*)\s+([A-Z][^.\n]+?)(?=\n|\d+\.)',  # Numbered sections
            r'^([A-Z][A-Z\s]{2,})(?=\n)',  # ALL CAPS headers
            r'^([A-Z][a-z\s]+?)(?=\n\n|\n[A-Z])',  # Title case headers
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                sections.append({
                    "type": "section",
                    "title": match.group().strip(),
                    "start_pos": match.start(),
                    "end_pos": match.end()
                })

        return sorted(sections, key=lambda x: x["start_pos"])

    def _extract_chapters(self, content: Dict) -> List[Dict]:
        """Extract chapter-level organization from the document."""
        chapters = []

        # Use outline if available
        if content.get("outline"):
            current_chapter = None
            for item in content["outline"]:
                if item["level"] == 1:  # Top-level items are chapters
                    if current_chapter:
                        chapters.append(current_chapter)
                    current_chapter = {
                        "title": item["title"],
                        "start_page": item["page"],
                        "sections": []
                    }
                elif item["level"] == 2 and current_chapter:
                    current_chapter["sections"].append({
                        "title": item["title"],
                        "page": item["page"]
                    })

            if current_chapter:
                chapters.append(current_chapter)

        return chapters

    def _extract_code_examples(self, content: Dict) -> List[Dict]:
        """Extract code examples from the document."""
        code_examples = []

        for page in content.get("pages", []):
            text = page.get("clean_text", "")

            # Look for code blocks (common patterns in Ansys docs)
            patterns = [
                r'```python\n(.*?)\n```',  # Markdown style
                r'```\n(.*?)\n```',       # Generic code blocks
                r'from ansys\.(.*?)(?=\n\n|\n[A-Z])',  # Python imports
                r'app\s*=\s*App\(\)(.*?)(?=\n\n|\n[A-Z])',  # PyMechanical app creation
            ]

            for pattern in patterns:
                matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    code_examples.append({
                        "page": page["page_number"],
                        "code": match.group(1).strip() if len(match.groups()) > 0 else match.group().strip(),
                        "context": self._get_surrounding_context(text, match.start(), match.end()),
                        "type": "python" if "python" in match.group().lower() else "code"
                    })

        return code_examples

    def _extract_api_references(self, content: Dict) -> List[Dict]:
        """Extract API references and method signatures."""
        api_refs = []

        for page in content.get("pages", []):
            text = page.get("clean_text", "")

            # Look for API method signatures and classes
            patterns = [
                r'class\s+(\w+)\s*\(',  # Class definitions
                r'def\s+(\w+)\s*\(',   # Method definitions
                r'(\w+\.\w+\.\w+)',    # Dotted notation (API paths)
                r'@\w+\.(\w+)',        # Decorators (MCP resources/tools)
            ]

            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    api_refs.append({
                        "page": page["page_number"],
                        "reference": match.group(),
                        "type": "api",
                        "context": self._get_surrounding_context(text, match.start(), match.end())
                    })

        return api_refs

    def _get_surrounding_context(self, text: str, start: int, end: int, context_size: int = 200) -> str:
        """Get surrounding context for a text match."""
        context_start = max(0, start - context_size)
        context_end = min(len(text), end + context_size)
        return text[context_start:context_end].strip()

    def process_all_pdfs(self) -> Dict[str, Any]:
        """Process all PDF files in the pdf directory."""
        results = {
            "processing_date": datetime.now().isoformat(),
            "files_processed": 0,
            "files_failed": 0,
            "total_pages": 0,
            "pdfs": {}
        }

        pdf_files = list(self.pdf_dir.glob("*.pdf"))

        for pdf_file in pdf_files:
            print(f"Processing {pdf_file.name}...")

            extracted_content = self.extract_text_from_pdf(pdf_file)

            if "error" not in extracted_content:
                results["files_processed"] += 1
                results["total_pages"] += extracted_content.get("total_pages", 0)

                # Save individual PDF extraction
                output_file = self.output_dir / f"{pdf_file.stem}_extracted.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(extracted_content, f, indent=2, ensure_ascii=False)

                print(f"  ✓ Extracted {extracted_content.get('total_pages', 0)} pages")
                print(f"  ✓ Found {len(extracted_content.get('chapters', []))} chapters")
                print(f"  ✓ Found {len(extracted_content.get('code_examples', []))} code examples")

            else:
                results["files_failed"] += 1
                print(f"  ✗ Failed: {extracted_content.get('error')}")

            results["pdfs"][pdf_file.name] = extracted_content

        # Save combined results
        combined_file = self.output_dir / "pdf_extracted_content.json"
        with open(combined_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\nProcessing complete:")
        print(f"  Files processed: {results['files_processed']}")
        print(f"  Files failed: {results['files_failed']}")
        print(f"  Total pages: {results['total_pages']}")

        return results


def main():
    """Main function to run PDF extraction."""
    project_root = Path(__file__).parent.parent
    extractor = AnsysPDFExtractor(project_root)

    print("Starting enhanced PDF extraction...")
    results = extractor.process_all_pdfs()

    return results


if __name__ == "__main__":
    main()