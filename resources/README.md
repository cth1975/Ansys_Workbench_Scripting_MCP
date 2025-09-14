# Ansys Resources

This directory contains Ansys Workbench documentation and processed content for the MCP server.

## Directory Structure

```
resources/
├── docs/                    # Documentation storage
│   ├── pdf/                # Downloaded PDF manuals (21 MB total)
│   ├── html/               # HTML documentation snapshots
│   └── extracted/          # Processed content (JSON format)
├── templates/              # Code templates extracted from docs
├── metadata/              # Resource metadata and indexing
└── scripts/               # Processing scripts
```

## Downloaded Resources

### PDF Manuals (4 files, ~21 MB)
- ✅ **Scripting in Mechanical Guide (2025 R1)** - 7.1 MB
- ✅ **Workbench Scripting Guide** - 6.7 MB
- ✅ **ACT Developer's Guide (2025 R1)** - 4.9 MB
- ✅ **DPF Post Cheat Sheet** - 2.1 MB

### HTML Documentation
- ✅ **PyMechanical Documentation** (133 HTML files)
- ✅ **Mechanical API Stubs** (5 HTML files)

## Processing Results

### Extracted Content (50+ KB processed data)
- `complete_extracted_data.json` - All processed content
- `search_index.json` - Searchable content index
- Individual processed files for each source

### Processing Summary
- **Sources processed**: 2 HTML documentation sites
- **HTML files processed**: 15 files
- **Extracted data**: Structured JSON for MCP integration

## Usage

### Download Resources
```bash
python scripts/download_resources.py
```

### Process Resources
```bash
python scripts/process_resources.py
```

### Check Status
```bash
cat metadata/resource_index.json
```

## Git Management

- **Included in Git**: Scripts, metadata, extracted content
- **Excluded from Git**: Large PDF/HTML files (see .gitignore)
- **Reason**: Keep repository size manageable while preserving processed data

## Next Steps

1. **Integrate with MCP Server**: Replace placeholder resources with Ansys content
2. **Improve PDF Processing**: Fix PDF text extraction for code examples
3. **Add More Sources**: Expand to additional Ansys documentation
4. **Create Templates**: Extract common code patterns into templates

## Resource URLs

All resources were downloaded from public Ansys documentation sites:
- Ansys Help Documentation (ansyshelp.ansys.com)
- PyAnsys Documentation (docs.pyansys.com)
- CFD Experts Mirror (dl.cfdexperts.net)

*Last updated: 2025-09-14*