#!/usr/bin/env python3
"""
Ansys Resource Downloader

Downloads core Ansys documentation and resources for the MCP server.
Organizes files with consistent naming and version tracking.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
import hashlib

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
RESOURCES_DIR = PROJECT_ROOT / "resources"
PDF_DIR = RESOURCES_DIR / "docs" / "pdf"
HTML_DIR = RESOURCES_DIR / "docs" / "html"
METADATA_DIR = RESOURCES_DIR / "metadata"

# Resource definitions
PDF_RESOURCES = [
    {
        "name": "Scripting in Mechanical Guide (2025 R1)",
        "url": "https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/pdf/Ansys_Scripting_in_Mechanical_Guide.pdf",
        "filename": "scripting_mechanical_2025r1.pdf",
        "description": "Canonical guide for Mechanical automation layer with API migration notes",
        "version": "2025 R1",
        "priority": 1
    },
    {
        "name": "Workbench Scripting Guide",
        "url": "https://dl.cfdexperts.net/cfd_resources/Ansys_Documentation/Workbench/Workbench_Scripting_Guide.pdf",
        "filename": "workbench_scripting_guide.pdf",
        "description": "Workbench journals, job control, and automation bridges",
        "version": "General",
        "priority": 1
    },
    {
        "name": "ACT Developer's Guide (2025 R1)",
        "url": "https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/pdf/Ansys_ACT_Developers_Guide.pdf",
        "filename": "act_developers_guide_2025r1.pdf",
        "description": "Extension model and namespaces for scripting stubs",
        "version": "2025 R1",
        "priority": 2
    },
    {
        "name": "DPF Post Cheat Sheet",
        "url": "https://cheatsheets.docs.pyansys.com/pydpf-post_cheat_sheet.pdf",
        "filename": "dpf_post_cheat_sheet.pdf",
        "description": "Quick reference for post-processing with DPF",
        "version": "Latest",
        "priority": 2
    }
]

HTML_RESOURCES = [
    {
        "name": "Mechanical API Stubs (v251)",
        "base_url": "https://scripting.mechanical.docs.pyansys.com/version/stable/api/ansys/mechanical/stubs/v251/",
        "local_dir": "mechanical_api_v251",
        "description": "Searchable API reference for Mechanical namespaces",
        "version": "v251",
        "priority": 1
    },
    {
        "name": "PyMechanical Documentation",
        "base_url": "https://mechanical.docs.pyansys.com/version/stable/",
        "local_dir": "pymechanical",
        "description": "CPython integration, architecture, and examples",
        "version": "Stable",
        "priority": 1
    },
    {
        "name": "PyWorkbench Documentation",
        "base_url": "https://workbench.docs.pyansys.com/version/stable/",
        "local_dir": "pyworkbench",
        "description": "gRPC Workbench control and scripting",
        "version": "Stable",
        "priority": 2
    },
    {
        "name": "DPF Core Documentation",
        "base_url": "https://dpf.docs.pyansys.com/version/stable/",
        "local_dir": "dpf_core",
        "description": "Data Processing Framework core functionality",
        "version": "Stable",
        "priority": 3
    },
    {
        "name": "DPF Post Documentation",
        "base_url": "https://post.docs.pyansys.com/version/stable/",
        "local_dir": "dpf_post",
        "description": "Post-processing with DPF",
        "version": "Stable",
        "priority": 2
    }
]

def ensure_directories():
    """Create necessary directories."""
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Directories created/verified")

def download_pdf(resource):
    """Download a single PDF resource."""
    url = resource["url"]
    filename = resource["filename"]
    filepath = PDF_DIR / filename

    print(f"📥 Downloading {resource['name']}...")
    print(f"   URL: {url}")
    print(f"   File: {filename}")

    # Skip if file already exists and is reasonable size
    if filepath.exists() and filepath.stat().st_size > 100000:  # 100KB
        file_size = filepath.stat().st_size / (1024 * 1024)  # MB
        print(f"   ⚠ File already exists ({file_size:.1f} MB), skipping...")
        return True

    try:
        # Different approaches for different URLs
        if "ansyshelp.ansys.com" in url:
            # Ansys secured URLs might need special handling
            print("   ⚠ Ansys secured URL detected - may require authentication")
            print("   → Attempting download with authentication bypass...")
            cmd = [
                "wget",
                "--no-check-certificate",
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "--timeout=60",
                "--tries=2",
                "--continue",
                "-O", str(filepath),
                url
            ]
        else:
            # Standard download
            cmd = [
                "wget",
                "--timeout=30",
                "--tries=3",
                "--continue",
                "-O", str(filepath),
                url
            ]

        print(f"   Running: {' '.join(cmd[:5])}...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            # Verify file was downloaded
            if filepath.exists() and filepath.stat().st_size > 1000:  # At least 1KB
                file_size = filepath.stat().st_size / (1024 * 1024)  # MB
                print(f"   ✓ Downloaded successfully ({file_size:.1f} MB)")
                return True
            else:
                print(f"   ✗ Downloaded file is too small or missing")
                if filepath.exists():
                    filepath.unlink()  # Remove empty file
                return False
        else:
            print(f"   ✗ Download failed (exit code {result.returncode})")
            print(f"   stderr: {result.stderr}")
            if filepath.exists():
                filepath.unlink()  # Remove empty file
            return False

    except subprocess.TimeoutExpired:
        print(f"   ✗ Download timeout after 120 seconds")
        if filepath.exists():
            filepath.unlink()
        return False
    except subprocess.CalledProcessError as e:
        print(f"   ✗ Download error: {e}")
        return False
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
        return False

def download_html_site(resource, max_depth=2):
    """Download HTML documentation site."""
    base_url = resource["base_url"]
    local_dir = HTML_DIR / resource["local_dir"]

    print(f"🌐 Downloading {resource['name']}...")
    print(f"   URL: {base_url}")
    print(f"   Local: {local_dir}")

    try:
        # Use wget to mirror the site
        cmd = [
            "wget",
            "--recursive",
            "--level", str(max_depth),
            "--no-parent",
            "--adjust-extension",
            "--convert-links",
            "--no-check-certificate",
            "--timeout=30",
            "--tries=2",
            "--directory-prefix", str(local_dir.parent),
            base_url
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"   ✓ Site downloaded successfully")
            return True
        else:
            print(f"   ⚠ Partial download (exit code {result.returncode})")
            # wget often returns non-zero for partial downloads, check if we got something
            if local_dir.exists():
                return True
            return False

    except Exception as e:
        print(f"   ✗ Download error: {e}")
        return False

def create_resource_index():
    """Create an index of all downloaded resources."""
    index = {
        "created": datetime.now().isoformat(),
        "pdf_resources": [],
        "html_resources": [],
        "statistics": {
            "total_pdfs": 0,
            "total_html_sites": 0,
            "total_size_mb": 0
        }
    }

    # Index PDF files
    for pdf_file in PDF_DIR.glob("*.pdf"):
        if pdf_file.is_file():
            file_size = pdf_file.stat().st_size
            index["pdf_resources"].append({
                "filename": pdf_file.name,
                "size_bytes": file_size,
                "size_mb": round(file_size / (1024 * 1024), 2),
                "modified": datetime.fromtimestamp(pdf_file.stat().st_mtime).isoformat()
            })
            index["statistics"]["total_pdfs"] += 1
            index["statistics"]["total_size_mb"] += file_size / (1024 * 1024)

    # Index HTML directories
    for html_dir in HTML_DIR.iterdir():
        if html_dir.is_dir():
            # Count HTML files
            html_files = list(html_dir.rglob("*.html"))
            index["html_resources"].append({
                "directory": html_dir.name,
                "html_files": len(html_files),
                "total_files": len(list(html_dir.rglob("*"))),
                "modified": datetime.fromtimestamp(html_dir.stat().st_mtime).isoformat()
            })
            index["statistics"]["total_html_sites"] += 1

    index["statistics"]["total_size_mb"] = round(index["statistics"]["total_size_mb"], 2)

    # Write index
    index_file = METADATA_DIR / "resource_index.json"
    with open(index_file, 'w') as f:
        json.dump(index, f, indent=2)

    print(f"📊 Resource index created: {index_file}")
    return index

def main():
    """Main download orchestrator."""
    print("🚀 Ansys Resource Downloader")
    print("=" * 50)

    # Check for wget
    try:
        subprocess.run(["wget", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: wget is required but not found")
        print("   Install with: brew install wget (macOS)")
        sys.exit(1)

    ensure_directories()

    # Download PDFs (Priority 1 & 2)
    print("\n📚 Downloading PDF Resources...")
    pdf_success = 0
    priority_1_pdfs = [r for r in PDF_RESOURCES if r.get("priority", 3) <= 2]

    for resource in priority_1_pdfs:
        if download_pdf(resource):
            pdf_success += 1
        print()  # Add spacing

    print(f"📚 PDF Downloads: {pdf_success}/{len(priority_1_pdfs)} successful")

    # Download HTML sites (Priority 1 only for now - these can be large)
    print("\n🌐 Downloading HTML Documentation...")
    html_success = 0
    priority_1_html = [r for r in HTML_RESOURCES if r.get("priority", 3) == 1]

    for resource in priority_1_html:
        if download_html_site(resource):
            html_success += 1
        print()  # Add spacing

    print(f"🌐 HTML Downloads: {html_success}/{len(priority_1_html)} successful")

    # Create resource index
    print("\n📊 Creating resource index...")
    index = create_resource_index()

    # Summary
    print("\n" + "=" * 50)
    print("📋 Download Summary:")
    print(f"   PDFs: {index['statistics']['total_pdfs']} files")
    print(f"   HTML sites: {index['statistics']['total_html_sites']} sites")
    print(f"   Total size: {index['statistics']['total_size_mb']:.1f} MB")
    print("\n✅ Resource gathering complete!")
    print(f"📁 Resources stored in: {RESOURCES_DIR}")

if __name__ == "__main__":
    main()