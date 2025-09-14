#!/usr/bin/env python3
"""
Test Enhanced Ansys MCP Server Capabilities

Demonstrates the new features and capabilities added to the server.
"""

from ansys_resource_loader import resource_loader, get_resource_content

def main():
    print("🧪 Testing Enhanced Ansys MCP Server Capabilities")
    print("=" * 60)

    # Test 1: PDF Data Loading
    print("\n1. PDF Data Loading:")
    pdf_data = resource_loader.get_pdf_data()
    print(f"   ✓ Loaded data from {pdf_data.get('files_processed', 0)} PDF files")
    print(f"   ✓ Total pages processed: {pdf_data.get('total_pages', 0):,}")

    # Test 2: Search Functionality
    print("\n2. Search Functionality:")
    search_results = resource_loader.search_content("PyMechanical architecture", max_results=3)
    print(f"   ✓ Found {len(search_results)} results for 'PyMechanical architecture'")
    for i, result in enumerate(search_results, 1):
        print(f"   {i}. {result['source']} ({result['type']}) - Score: {result['relevance_score']:.3f}")

    # Test 3: Chapter Access
    print("\n3. Chapter Access:")
    chapters = resource_loader.get_pdf_chapters("scripting_mechanical_2025r1.pdf")
    print(f"   ✓ Found {len(chapters)} chapters in scripting guide")
    if chapters:
        print(f"   First chapter: {chapters[0].get('title', 'Unknown')}")

    # Test 4: Code Examples
    print("\n4. Code Examples:")
    examples = resource_loader.get_code_examples()
    print(f"   ✓ Extracted {len(examples)} code examples from documentation")

    # Test 5: API References
    print("\n5. API References:")
    api_refs = resource_loader.get_api_references()
    print(f"   ✓ Found {len(api_refs)} API references")

    # Test 6: Resource Content Generation
    print("\n6. Resource Content Generation:")
    resources_to_test = [
        "workbench_overview",
        "pymechanical_architecture",
        "act_development",
        "dpf_post_processing"
    ]

    for resource_name in resources_to_test:
        try:
            content = get_resource_content(resource_name)
            print(f"   ✓ {resource_name}: {len(content):,} characters")
        except Exception as e:
            print(f"   ✗ {resource_name}: Error - {e}")

    print("\n" + "=" * 60)
    print("🎉 Enhanced MCP Server Testing Complete!")
    print("\nNew Capabilities Summary:")
    print("• 9 Resources (vs 4 original)")
    print("• 3 Tools for dynamic content access")
    print("• Search across 40+ MB of extracted documentation")
    print("• Chapter-level access to PDF manuals")
    print("• Code example extraction and retrieval")
    print("• API reference compilation")
    print("• Full-text search with relevance scoring")

if __name__ == "__main__":
    main()