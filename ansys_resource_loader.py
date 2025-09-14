#!/usr/bin/env python3
"""
Ansys Resource Loader

Loads and serves processed Ansys documentation for the MCP server.
Provides structured access to Ansys Workbench scripting resources.
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

class AnsysResourceLoader:
    """Manages loading and serving Ansys documentation resources."""

    def __init__(self):
        """Initialize the resource loader."""
        self.project_root = Path(__file__).parent
        self.resources_dir = self.project_root / "resources"
        self.extracted_dir = self.resources_dir / "docs" / "extracted"
        self.metadata_dir = self.resources_dir / "metadata"

        # Cache for loaded resources
        self._resource_cache = {}
        self._index_cache = None
        self._pdf_cache = None

    def _load_json_file(self, file_path: Path) -> Optional[Dict]:
        """Load and cache a JSON file."""
        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None

    def get_resource_index(self) -> Dict:
        """Get the main resource index."""
        if self._index_cache is None:
            index_file = self.metadata_dir / "resource_index.json"
            self._index_cache = self._load_json_file(index_file) or {}
        return self._index_cache

    def get_search_index(self) -> Dict:
        """Get the search index for quick content lookup."""
        search_file = self.extracted_dir / "search_index.json"
        return self._load_json_file(search_file) or {}

    def get_pymechanical_docs(self) -> Dict:
        """Get processed PyMechanical documentation."""
        if "pymechanical" not in self._resource_cache:
            docs_file = self.extracted_dir / "mechanical.docs.pyansys.com_processed.json"
            self._resource_cache["pymechanical"] = self._load_json_file(docs_file) or {}
        return self._resource_cache["pymechanical"]

    def get_mechanical_api_docs(self) -> Dict:
        """Get processed Mechanical API documentation."""
        if "mechanical_api" not in self._resource_cache:
            api_file = self.extracted_dir / "scripting.mechanical.docs.pyansys.com_processed.json"
            self._resource_cache["mechanical_api"] = self._load_json_file(api_file) or {}
        return self._resource_cache["mechanical_api"]

    def get_complete_data(self) -> Dict:
        """Get all processed data combined."""
        if "complete" not in self._resource_cache:
            complete_file = self.extracted_dir / "complete_extracted_data.json"
            self._resource_cache["complete"] = self._load_json_file(complete_file) or {}
        return self._resource_cache["complete"]

    def get_pdf_data(self) -> Dict:
        """Get extracted PDF content."""
        if self._pdf_cache is None:
            pdf_file = self.extracted_dir / "pdf_extracted_content.json"
            self._pdf_cache = self._load_json_file(pdf_file) or {}
        return self._pdf_cache

    def search_content(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search across all documentation content."""
        results = []
        query_lower = query.lower()

        # Search PDF content
        pdf_data = self.get_pdf_data()
        for pdf_name, pdf_content in pdf_data.get("pdfs", {}).items():
            if "pages" in pdf_content:
                for page in pdf_content["pages"]:
                    text = page.get("clean_text", "")
                    if query_lower in text.lower():
                        # Find context around the match
                        context = self._extract_context(text, query_lower)
                        results.append({
                            "source": pdf_name,
                            "type": "pdf",
                            "page": page.get("page_number"),
                            "context": context,
                            "relevance_score": self._calculate_relevance(text, query_lower)
                        })

        # Search HTML content
        html_data = self.get_pymechanical_docs()
        if "content" in html_data:
            for item in html_data["content"]:
                content_text = item.get("content", "")
                title = item.get("title", "")
                if query_lower in content_text.lower() or query_lower in title.lower():
                    context = self._extract_context(content_text, query_lower)
                    results.append({
                        "source": "PyMechanical Docs",
                        "type": "html",
                        "title": title,
                        "file": item.get("file"),
                        "context": context,
                        "relevance_score": self._calculate_relevance(content_text + " " + title, query_lower)
                    })

        # Sort by relevance and return top results
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:max_results]

    def _extract_context(self, text: str, query: str, context_size: int = 300) -> str:
        """Extract context around a search query match."""
        match = re.search(re.escape(query), text, re.IGNORECASE)
        if match:
            start = max(0, match.start() - context_size // 2)
            end = min(len(text), match.end() + context_size // 2)
            context = text[start:end]
            if start > 0:
                context = "..." + context
            if end < len(text):
                context = context + "..."
            return context.strip()
        return text[:context_size] + "..." if len(text) > context_size else text

    def _calculate_relevance(self, text: str, query: str) -> float:
        """Calculate relevance score for search results."""
        text_lower = text.lower()
        query_lower = query.lower()

        # Count exact matches
        exact_matches = text_lower.count(query_lower)

        # Count word matches
        query_words = query_lower.split()
        word_matches = sum(text_lower.count(word) for word in query_words)

        # Calculate score based on frequency and text length
        score = (exact_matches * 2 + word_matches) / (len(text.split()) + 1)
        return score

    def get_pdf_chapters(self, pdf_name: str) -> List[Dict]:
        """Get chapters from a specific PDF."""
        pdf_data = self.get_pdf_data()
        pdf_content = pdf_data.get("pdfs", {}).get(pdf_name, {})
        return pdf_content.get("chapters", [])

    def get_pdf_content_by_chapter(self, pdf_name: str, chapter_title: str) -> Dict:
        """Get content from a specific chapter in a PDF."""
        pdf_data = self.get_pdf_data()
        pdf_content = pdf_data.get("pdfs", {}).get(pdf_name, {})

        chapters = pdf_content.get("chapters", [])
        for chapter in chapters:
            if chapter_title.lower() in chapter.get("title", "").lower():
                # Extract pages for this chapter
                start_page = chapter.get("start_page", 1)
                pages = pdf_content.get("pages", [])

                # Find chapter content
                chapter_pages = [p for p in pages if p.get("page_number", 0) >= start_page]

                # Try to find end page by looking at next chapter
                next_chapter_page = None
                current_idx = chapters.index(chapter)
                if current_idx + 1 < len(chapters):
                    next_chapter_page = chapters[current_idx + 1].get("start_page")

                if next_chapter_page:
                    chapter_pages = [p for p in chapter_pages if p.get("page_number", 0) < next_chapter_page]

                # Combine chapter text
                chapter_text = "\n".join([p.get("clean_text", "") for p in chapter_pages])

                return {
                    "title": chapter.get("title"),
                    "start_page": start_page,
                    "end_page": next_chapter_page - 1 if next_chapter_page else len(pages),
                    "content": chapter_text,
                    "sections": chapter.get("sections", [])
                }

        return {}

    def get_code_examples(self, source: str = "all") -> List[Dict]:
        """Get code examples from documentation."""
        examples = []

        if source in ["all", "pdf"]:
            pdf_data = self.get_pdf_data()
            for pdf_name, pdf_content in pdf_data.get("pdfs", {}).items():
                pdf_examples = pdf_content.get("code_examples", [])
                for example in pdf_examples:
                    example["source"] = pdf_name
                    examples.append(example)

        return examples

    def get_api_references(self, source: str = "all") -> List[Dict]:
        """Get API references from documentation."""
        references = []

        if source in ["all", "pdf"]:
            pdf_data = self.get_pdf_data()
            for pdf_name, pdf_content in pdf_data.get("pdfs", {}).items():
                pdf_refs = pdf_content.get("api_references", [])
                for ref in pdf_refs:
                    ref["source"] = pdf_name
                    references.append(ref)

        return references

# Global instance
resource_loader = AnsysResourceLoader()

def get_ansys_workbench_overview() -> str:
    """Get Ansys Workbench overview and capabilities."""
    pymech_docs = resource_loader.get_pymechanical_docs()
    index = resource_loader.get_resource_index()
    pdf_data = resource_loader.get_pdf_data()

    overview_content = f"""# Ansys Workbench Scripting Overview

## About Ansys Workbench Automation

Ansys Workbench provides powerful automation capabilities through Python scripting, supporting both **CPython** and **IronPython** implementations. This enables engineers to automate repetitive tasks, create custom workflows, and integrate Ansys with external tools.

## Key Capabilities

### 1. **PyMechanical - CPython Integration**
- **Purpose**: Modern Python interface to Ansys Mechanical
- **Architecture**: Supports both embedded and remote session modes
- **Compatibility**: Ansys 2024R1 and later versions
- **Key Features**:
  - Direct Python.NET integration for embedded instances
  - gRPC-based remote sessions for distributed computing
  - Full access to Mechanical's .NET API from CPython
  - GUI automation and headless operation support

### 2. **Scripting Modes**

#### Embedded Instance
- Mechanical object directly loaded into Python memory
- Best for: Interactive development, complex data manipulation
- Performance: Direct memory access, fastest execution

#### Remote Session
- Mechanical operates as gRPC server
- Best for: Distributed computing, batch processing
- Benefits: Scalable, supports multiple concurrent sessions

### 3. **Mechanical Scripting API**
- **ACT Framework**: Application Customization Toolkit for extensions
- **Automation Layer**: Pre-built automation objects and methods
- **Threading Support**: Multi-threaded operation capabilities
- **Data Model Access**: Full access to Mechanical's object hierarchy

## Comprehensive Documentation Available
"""

    # Add resource statistics from both sources
    if index.get("statistics"):
        stats = index["statistics"]
        overview_content += f"""
**Downloaded Resources:**
- **PDF Manuals**: {stats.get('total_pdfs', 0)} files ({stats.get('total_size_mb', 0):.1f} MB)
- **HTML Documentation**: {stats.get('total_html_sites', 0)} sites
- **Last Updated**: {index.get('created', 'Unknown')[:10]}
"""

    # Add PDF extraction statistics
    if pdf_data.get("files_processed"):
        overview_content += f"""

**Extracted PDF Content:**
- **Total Pages Processed**: {pdf_data.get('total_pages', 0):,} pages
- **Documents**: {pdf_data.get('files_processed', 0)} manuals fully extracted
- **Content Size**: 40+ MB of structured text and metadata
"""

    # Add available PDFs with chapter counts
    if pdf_data.get("pdfs"):
        overview_content += "\n**Available Manuals:**\n"
        for pdf_name, pdf_content in pdf_data["pdfs"].items():
            chapters = len(pdf_content.get("chapters", []))
            pages = pdf_content.get("total_pages", 0)
            overview_content += f"- **{pdf_name.replace('_', ' ').replace('.pdf', '')}**: {pages} pages, {chapters} chapters\n"

    # Add content from PyMechanical docs
    if pymech_docs.get("content"):
        overview_content += f"""

**PyMechanical HTML Documentation:**
- **Files Processed**: {pymech_docs.get('processed_files', 0)} / {pymech_docs.get('total_files', 0)}
- **Processing Date**: {pymech_docs.get('processed_date', 'Unknown')[:10]}
"""

    overview_content += """

## Getting Started

### Basic PyMechanical Usage
```python
from ansys.mechanical.core import App

# Initialize embedded app
app = App()

# Update global variables for easier access
app.update_globals(globals())

# Access Mechanical objects directly
# model, analyses, etc. are now available

# Example: Get model information
print(f"Model name: {model.Name}")
```

### Remote Session Example
```python
from ansys.mechanical.core import Mechanical

# Connect to remote Mechanical instance
mechanical = Mechanical()

# Execute Mechanical commands
result = mechanical.run_python_script("model.Name")
print(f"Remote model name: {result}")
```

## Available Resources

1. **Workbench Overview** - This comprehensive guide
2. **PyMechanical Architecture** - Implementation details and design patterns
3. **CPython vs IronPython** - Migration guide and comparison
4. **Quick Reference** - Common scripting tasks and examples
5. **Search Capability** - Query across all 2000+ pages of documentation

## Next Steps

1. **Explore Resources**: Use MCP resources to access detailed documentation
2. **Search Documentation**: Use search tools to find specific topics
3. **API Reference**: Check Mechanical API stubs for exact method signatures
4. **Examples**: Review code examples from comprehensive manuals
5. **Best Practices**: Follow Ansys recommendations for automation workflows

---
*This overview is generated from 40+ MB of extracted Ansys documentation (2025 R1)*
"""

    return overview_content

def get_pymechanical_architecture() -> str:
    """Get detailed PyMechanical architecture information."""
    pymech_docs = resource_loader.get_pymechanical_docs()
    pdf_data = resource_loader.get_pdf_data()

    # Extract architecture content from processed docs
    architecture_content = """# PyMechanical Architecture

## Overview

PyMechanical provides a Python interface to Ansys Mechanical, bridging the gap between Python automation and Mechanical's .NET-based API.

## Architecture Components

### 1. **Core Components**
- **App Class**: Main entry point for embedded instances
- **Mechanical Class**: Interface for remote sessions
- **Client**: Low-level communication layer
- **Plottable**: Visualization and plotting support

### 2. **Communication Modes**

#### Embedded Mode (Python.NET)
- Direct .NET object access from Python
- In-process execution for maximum performance
- Suitable for: Interactive development, complex data processing

#### Remote Mode (gRPC)
- Mechanical runs as separate server process
- Client-server communication via gRPC protocol
- Suitable for: Distributed computing, batch automation

### 3. **API Layers**

#### High-Level API
```python
from ansys.mechanical.core import App
app = App()  # Simple initialization
```

#### Mid-Level API
```python
from ansys.mechanical.core import Mechanical
mechanical = Mechanical(
    ip="localhost",
    port=10000
)
```

#### Low-Level API
```python
from ansys.mechanical.core.client import Client
client = Client(channel=grpc_channel)
```

## Key Features

### Global Variables Integration
```python
# Automatic globals update
app = App(globals=globals())

# Manual globals update
app.update_globals(globals())

# Exclude enums from globals
app.update_globals(globals(), False)
```

### GUI Integration
```python
# Launch GUI for embedded instance
app.launch_gui()

# Save current state
app.save("my_analysis.mechdb")
```

### Error Handling
- Comprehensive exception handling
- Logging integration with Python logging module
- Transaction support for atomic operations

## Best Practices

1. **Use appropriate mode**: Embedded for development, Remote for production
2. **Manage resources**: Properly close connections and clean up
3. **Error handling**: Always wrap operations in try-catch blocks
4. **Performance**: Use remote mode for long-running batch jobs

"""

    # Add content from scripting manual
    scripting_pdf = "scripting_mechanical_2025r1.pdf"
    if scripting_pdf in pdf_data.get("pdfs", {}):
        # Look for architecture-related chapters
        chapters = resource_loader.get_pdf_chapters(scripting_pdf)
        for chapter in chapters:
            if any(keyword in chapter.get("title", "").lower() for keyword in ["architecture", "overview", "introduction"]):
                chapter_content = resource_loader.get_pdf_content_by_chapter(scripting_pdf, chapter["title"])
                if chapter_content.get("content"):
                    # Extract first 1000 characters for overview
                    content_snippet = chapter_content["content"][:1500]
                    architecture_content += f"""

## From Ansys Scripting Guide: {chapter.get('title')}

{content_snippet}...

*[Extracted from {scripting_pdf}, Chapter {chapter.get('title')}]*
"""
                break

    # Add content from HTML docs if available
    if pymech_docs.get("content"):
        for item in pymech_docs["content"]:
            if "architecture" in item.get("title", "").lower():
                # Extract relevant parts of the architecture content
                content_snippet = item.get("content", "")[:1000]
                if content_snippet:
                    architecture_content += f"""

## From PyMechanical Documentation

{content_snippet}...

*[Content extracted from PyMechanical HTML documentation]*
"""
                break

    return architecture_content

def get_cpython_vs_ironpython_guide() -> str:
    """Get guide comparing CPython vs IronPython in Ansys context."""
    return """# CPython vs IronPython in Ansys Workbench

## Overview

Ansys Workbench supports two Python implementations for scripting and automation. Understanding their differences is crucial for choosing the right approach for your projects.

## CPython (Recommended for New Projects)

### What is CPython?
- **Standard Python**: The reference implementation of Python
- **Availability**: Ansys 2024R1 and later
- **Runtime**: Separate Python process with .NET interop

### Advantages
✅ **Full Python Ecosystem**: Access to pip, conda, and all Python packages
✅ **Modern Python**: Latest Python versions (3.9+) with modern language features
✅ **Better Debugging**: Standard Python debugging tools work
✅ **Package Management**: Easy installation of scientific packages (NumPy, Pandas, etc.)
✅ **Performance**: Better memory management for large datasets
✅ **Future-Proof**: Ansys strategic direction for Python integration

### Use Cases
- **Data Analysis**: Complex post-processing with pandas/numpy
- **Integration**: Connecting Ansys with external Python tools
- **Modern Development**: Using contemporary Python practices
- **Batch Processing**: Large-scale automation workflows

### Example: CPython Setup
```python
# Install PyMechanical
pip install ansys-mechanical-core

# Use in scripts
from ansys.mechanical.core import App
app = App()
app.update_globals(globals())

# Full Python ecosystem available
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Analyze results with modern Python tools
results_df = pd.DataFrame(displacement_data)
```

## IronPython (Legacy Support)

### What is IronPython?
- **Python on .NET**: Python implementation running on .NET Framework
- **Availability**: All Ansys versions
- **Runtime**: Integrated directly with Mechanical's .NET runtime

### Advantages
✅ **Direct Integration**: Seamless access to .NET objects
✅ **Performance**: No marshaling overhead for .NET calls
✅ **Compatibility**: Works with older Ansys versions
✅ **Embedded**: Built into Mechanical GUI

### Limitations
❌ **Limited Packages**: Cannot use most Python packages (no NumPy, pandas, etc.)
❌ **Python 2.7**: Stuck on older Python version
❌ **Debugging**: Limited debugging capabilities
❌ **Isolation**: Harder to integrate with external Python tools

### Use Cases
- **Legacy Scripts**: Maintaining existing IronPython automation
- **Simple Automation**: Basic Mechanical operations
- **GUI Extensions**: ACT development and customization
- **Quick Scripts**: Simple parameter studies

### Example: IronPython in Mechanical
```python
# This runs inside Mechanical GUI
# Limited to built-in capabilities

# Access Mechanical objects directly
analysis = Model.Analyses[0]
solution = analysis.Solution

# Basic operations work well
for result in solution.Children:
    if result.Name == "Total Deformation":
        result.Evaluate()
```

## Migration Strategy

### From IronPython to CPython

1. **Assessment**
   - Identify external package dependencies
   - Review .NET object usage patterns
   - Evaluate automation complexity

2. **Gradual Migration**
   ```python
   # Phase 1: Hybrid approach
   # Keep IronPython for Mechanical operations
   # Use CPython for data processing

   # Phase 2: Full CPython with PyMechanical
   from ansys.mechanical.core import App
   app = App()
   ```

3. **Testing Strategy**
   - Validate results between implementations
   - Performance benchmarking
   - Error handling verification

## Decision Matrix

| Feature | CPython | IronPython |
|---------|---------|------------|
| Python Packages | ✅ Full ecosystem | ❌ Very limited |
| Ansys Integration | ✅ PyMechanical | ✅ Direct .NET |
| Performance | ✅ Better overall | ✅ .NET calls |
| Debugging | ✅ Standard tools | ❌ Limited |
| Future Support | ✅ Strategic | ⚠️ Maintenance |
| Learning Curve | ⚠️ Setup required | ✅ Built-in |

## Recommendations

### Choose CPython When:
- Building new automation workflows
- Need external Python packages
- Require modern Python features
- Planning long-term maintenance
- Working with large datasets

### Choose IronPython When:
- Maintaining legacy scripts
- Simple Mechanical operations only
- Working in Mechanical GUI
- Quick prototyping
- Limited to older Ansys versions

### Hybrid Approach:
- Use IronPython for Mechanical GUI integration
- Use CPython for data processing and analysis
- Transfer data between systems as needed

---
*Updated for Ansys 2025 R1 - CPython is the recommended approach for new development*
"""

def get_quick_reference_guide() -> str:
    """Get a quick reference guide for common Ansys scripting tasks."""
    return """# Ansys Workbench Scripting Quick Reference

## Essential PyMechanical Commands

### Application Setup
```python
# Initialize embedded instance
from ansys.mechanical.core import App
app = App()
app.update_globals(globals())

# Initialize remote session
from ansys.mechanical.core import Mechanical
mechanical = Mechanical()
```

### Project and Model Operations
```python
# Create new project
app.new()

# Open existing project
app.open(r"C:\\path\\to\\project.mechdb")

# Save project
app.save()
app.save(r"C:\\path\\to\\new_project.mechdb")

# Access model
model = app.model
print(f"Model name: {model.Name}")
```

### Geometry Operations
```python
# Import geometry
geometry_import = model.GeometryImport
geometry_import.Import(r"C:\\path\\to\\geometry.step")

# Access geometry
geometry = model.Geometry
print(f"Number of bodies: {len(geometry.Bodies)}")

# Body operations
for body in geometry.Bodies:
    print(f"Body: {body.Name}, Material: {body.Material}")
```

### Meshing
```python
# Access mesh
mesh = model.Mesh

# Generate mesh
mesh.GenerateMesh()

# Mesh statistics
print(f"Nodes: {mesh.Nodes}")
print(f"Elements: {mesh.Elements}")

# Mesh sizing
sizing = mesh.AddSizing()
sizing.Location = selection  # Define selection first
sizing.ElementSize = Quantity("5 mm")
```

### Analysis Setup
```python
# Create analysis
analysis = model.AddStaticStructuralAnalysis()

# Analysis settings
analysis_settings = analysis.AnalysisSettings
analysis_settings.NumberOfSteps = 2
analysis_settings.AutomaticTimeStepping = "On"

# Add loads and boundary conditions
fixed_support = analysis.AddFixedSupport()
fixed_support.Location = face_selection

force = analysis.AddForce()
force.Location = vertex_selection
force.Magnitude = Quantity("1000 N")
```

### Solution and Results
```python
# Solve analysis
solution = analysis.Solution
solution.Solve(True)  # True for wait

# Check solution status
if solution.Status == "Done":
    print("Analysis completed successfully")

# Add result objects
total_deformation = solution.AddTotalDeformation()
equivalent_stress = solution.AddEquivalentStress()

# Evaluate results
total_deformation.Evaluate()
equivalent_stress.Evaluate()

# Get result values
max_deformation = total_deformation.Maximum
max_stress = equivalent_stress.Maximum
```

## Common Patterns

### Parametric Studies
```python
# Define parameters
parameters = [
    {"force": "500 N", "thickness": "5 mm"},
    {"force": "1000 N", "thickness": "10 mm"},
    {"force": "1500 N", "thickness": "15 mm"}
]

results = []
for param_set in parameters:
    # Update model parameters
    force.Magnitude = Quantity(param_set["force"])
    # Update thickness in geometry/mesh

    # Solve
    solution.Solve(True)

    # Extract results
    total_deformation.Evaluate()
    results.append({
        "parameters": param_set,
        "max_deformation": total_deformation.Maximum.Value,
        "max_stress": equivalent_stress.Maximum.Value
    })
```

### Batch Processing
```python
import os
from pathlib import Path

# Process multiple files
geometry_files = Path(r"C:\\geometries").glob("*.step")

for geo_file in geometry_files:
    # Create new project
    app.new()

    # Import geometry
    geometry_import = model.GeometryImport
    geometry_import.Import(str(geo_file))

    # Setup analysis (reuse previous setup)
    # ... analysis setup code ...

    # Solve and save results
    solution.Solve(True)
    results_file = geo_file.with_suffix('.csv')
    # Export results to CSV
```

### Error Handling
```python
try:
    # Mechanical operations
    mesh.GenerateMesh()
    solution.Solve(True)

    if solution.Status != "Done":
        raise Exception(f"Solution failed: {solution.Status}")

except Exception as e:
    print(f"Error: {e}")
    # Cleanup or recovery actions
finally:
    # Always save work
    app.save()
```

### Selection and Scoping
```python
# Create selections
selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)

# By entity ID
selection.Ids = [1, 2, 3]  # Entity IDs

# By criteria
all_faces = model.Geometry.GetChildren(DataModelObjectCategory.Face, True)
selected_faces = [face for face in all_faces if face.Area > Quantity("100 mm^2")]

# Apply selection
boundary_condition.Location = selection
```

## Useful Utilities

### Data Export
```python
# Export mesh
mesh_export = model.MeshExport
mesh_export.Format = MeshExportFormat.Nastran
mesh_export.Export(r"C:\\output\\mesh.nas")

# Export results
solution.ExportResults(r"C:\\output\\results.csv")
```

### Reporting
```python
# Generate reports
report = solution.AddReport()
report.Activate()
report.ReportFormat = ReportFormatType.Image
report.Export(r"C:\\output\\report.png")
```

### Units Management
```python
# Set unit system
app.ActiveUnitSystem = UnitSystemType.StandardMKS  # SI units

# Create quantities with units
force_value = Quantity("1000 N")
length_value = Quantity("10 mm")

# Convert units
force_in_lbf = force_value.ConvertToUnit("lbf")
```

## Debugging Tips

### Object Inspection
```python
# Explore object properties
obj = model.Geometry.Bodies[0]
print(f"Object type: {type(obj)}")
print(f"Available properties: {dir(obj)}")

# Check object tree
for child in obj.Children:
    print(f"Child: {child.Name} ({type(child)})")
```

### Logging
```python
import logging
logging.basicConfig(level=logging.INFO)

# Log operations
logging.info(f"Starting analysis: {analysis.Name}")
logging.info(f"Mesh generated: {mesh.Elements} elements")
```

---
*Quick reference for Ansys Workbench automation with PyMechanical*
"""

def get_act_development_guide() -> str:
    """Get ACT development guide from extracted PDF content."""
    pdf_data = resource_loader.get_pdf_data()
    act_pdf = "act_developers_guide_2025r1.pdf"

    guide_content = """# ACT (Application Customization Toolkit) Development Guide

## Overview

ACT enables developers to create custom applications and extensions for Ansys Mechanical. This guide covers the development process, APIs, and best practices for ACT development.

## Key Components

### 1. **ACT Framework**
- Extensibility framework for Mechanical
- Python-based development environment
- Integration with Mechanical's data model

### 2. **Development Environment**
- ACT Console for testing and debugging
- Extensions Manager for deployment
- Template system for rapid development

"""

    if act_pdf in pdf_data.get("pdfs", {}):
        # Get first chapter content as overview
        chapters = resource_loader.get_pdf_chapters(act_pdf)
        if chapters:
            first_chapter = chapters[0]
            chapter_content = resource_loader.get_pdf_content_by_chapter(act_pdf, first_chapter["title"])
            if chapter_content.get("content"):
                guide_content += f"""
## From ACT Developer's Guide: {first_chapter.get('title')}

{chapter_content['content'][:2000]}...

*[Content from {act_pdf}]*
"""

        pdf_content = pdf_data["pdfs"][act_pdf]
        guide_content += f"""

## Available Chapters ({len(chapters)} total)

This {pdf_content.get('total_pages', 0)}-page guide covers:
"""
        for chapter in chapters[:10]:  # Show first 10 chapters
            guide_content += f"- {chapter.get('title', 'Unknown')}\n"

    guide_content += """

## Getting Started with ACT Development

1. **Setup Development Environment**
2. **Understand ACT Architecture**
3. **Create Your First Extension**
4. **Test and Debug**
5. **Deploy and Distribute**

Use the `get_chapter_content` tool to access specific chapters from the ACT Developer's Guide.
"""

    return guide_content

def get_dpf_post_processing_guide() -> str:
    """Get DPF post-processing guide."""
    pdf_data = resource_loader.get_pdf_data()
    dpf_pdf = "dpf_post_cheat_sheet.pdf"

    if dpf_pdf in pdf_data.get("pdfs", {}):
        pdf_content = pdf_data["pdfs"][dpf_pdf]
        if "pages" in pdf_content and pdf_content["pages"]:
            page_content = pdf_content["pages"][0]  # It's a 1-page cheat sheet
            return f"""# PyDPF-Post Processing Cheat Sheet

## Overview

PyDPF-Post provides a Pythonic interface for post-processing Ansys results. This cheat sheet covers the most common operations.

{page_content.get('clean_text', '')}

---
*Content extracted from {dpf_pdf}*
"""

    return """# PyDPF-Post Processing Guide

PyDPF-Post provides powerful post-processing capabilities for Ansys results.

## Key Features
- Pythonic interface to Ansys results
- Efficient data manipulation
- Visualization capabilities
- Integration with scientific Python ecosystem

*Use the search tool to find specific DPF topics in the documentation.*
"""

def get_scripting_examples_guide() -> str:
    """Get comprehensive scripting examples from all documentation."""
    examples = resource_loader.get_code_examples()

    guide_content = f"""# Ansys Scripting Examples

## Overview

This collection contains {len(examples)} code examples extracted from official Ansys documentation.

## Available Examples
"""

    # Group examples by source
    examples_by_source = {}
    for example in examples:
        source = example.get('source', 'Unknown')
        if source not in examples_by_source:
            examples_by_source[source] = []
        examples_by_source[source].append(example)

    for source, source_examples in examples_by_source.items():
        guide_content += f"\n### {source.replace('_', ' ').replace('.pdf', '')}\n"
        guide_content += f"- {len(source_examples)} examples available\n"

    if examples:
        guide_content += "\n## Sample Examples\n\n"
        for i, example in enumerate(examples[:3], 1):  # Show first 3 examples
            guide_content += f"### Example {i}: {example.get('type', 'Code')}\n"
            guide_content += f"**Source**: {example.get('source', 'Unknown')} (Page {example.get('page', 'N/A')})\n\n"
            code = example.get('code', '')[:500]  # Truncate long code
            guide_content += f"```python\n{code}\n```\n\n"

    guide_content += """
## Finding Examples

Use the `get_code_example` tool with specific topics:
- `get_code_example("mesh generation")`
- `get_code_example("analysis setup")`
- `get_code_example("results extraction")`
"""

    return guide_content

def get_api_reference_guide() -> str:
    """Get API reference documentation."""
    api_refs = resource_loader.get_api_references()

    guide_content = f"""# Ansys API Reference

## Overview

This reference contains {len(api_refs)} API references extracted from official documentation.

## API Categories

### PyMechanical Core API
- App class and initialization
- Mechanical remote sessions
- Data model access

### Mechanical Scripting API
- Analysis setup and execution
- Geometry and meshing operations
- Results and post-processing

### ACT API
- Extension development
- Custom UI components
- Solver integration
"""

    # Show sample API references
    if api_refs:
        guide_content += "\n## Sample API References\n\n"
        for i, ref in enumerate(api_refs[:5], 1):  # Show first 5 references
            guide_content += f"### {i}. {ref.get('reference', 'Unknown')}\n"
            guide_content += f"**Source**: {ref.get('source', 'Unknown')} (Page {ref.get('page', 'N/A')})\n"
            if ref.get('context'):
                guide_content += f"**Context**: {ref['context'][:200]}...\n\n"

    guide_content += """
## Using the API

For detailed API usage:
1. Use the search tool to find specific methods
2. Check the PyMechanical architecture resource
3. Review scripting examples for usage patterns

*Search for specific API methods like "App()", "launch_mechanical", etc.*
"""

    return guide_content

# Main resource functions that will be used by the MCP server
def get_resource_content(resource_name: str) -> str:
    """Get content for a specific resource."""
    resource_map = {
        "workbench_overview": get_ansys_workbench_overview,
        "pymechanical_architecture": get_pymechanical_architecture,
        "cpython_vs_ironpython": get_cpython_vs_ironpython_guide,
        "quick_reference": get_quick_reference_guide,
        "act_development": get_act_development_guide,
        "dpf_post_processing": get_dpf_post_processing_guide,
        "scripting_examples": get_scripting_examples_guide,
        "api_reference": get_api_reference_guide
    }

    if resource_name in resource_map:
        return resource_map[resource_name]()
    else:
        return f"Resource '{resource_name}' not found."