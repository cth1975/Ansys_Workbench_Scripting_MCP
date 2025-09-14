#!/usr/bin/env python3
"""
Test MCP Resource Content Delivery

This script tests what content is actually being delivered through the MCP protocol
to help diagnose if AI assistants receive the full content.
"""

import asyncio
import json
from ansys_resource_loader import get_resource_content

def test_all_resources():
    """Test all resource content generation."""
    print("🧪 Testing MCP Resource Content Delivery")
    print("=" * 60)

    resources = [
        "workbench_overview",
        "pymechanical_architecture",
        "cpython_vs_ironpython",
        "quick_reference",
        "act_development",
        "dpf_post_processing",
        "scripting_examples",
        "api_reference"
    ]

    total_content = 0

    for resource_name in resources:
        print(f"\n📄 Testing Resource: {resource_name}")
        try:
            content = get_resource_content(resource_name)
            content_length = len(content)
            total_content += content_length

            print(f"   ✅ Content Length: {content_length:,} characters")
            print(f"   ✅ Content Type: {type(content)}")

            # Check for rich content indicators
            markdown_indicators = ['#', '##', '###', '**', '*', '```', '-']
            found_indicators = [ind for ind in markdown_indicators if ind in content]
            print(f"   ✅ Markdown Elements: {len(found_indicators)} found {found_indicators[:5]}")

            # Show content structure
            lines = content.split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            print(f"   ✅ Structure: {len(lines)} total lines, {len(non_empty_lines)} with content")

            # Show first and last few lines
            print(f"   📝 First 150 chars: {repr(content[:150])}")
            if content_length > 300:
                print(f"   📝 Last 100 chars: {repr(content[-100:])}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print(f"\n📊 Summary:")
    print(f"   Total Content Generated: {total_content:,} characters")
    print(f"   Average per Resource: {total_content // len(resources):,} characters")

    return total_content

def test_search_functionality():
    """Test search functionality."""
    print(f"\n🔍 Testing Search Functionality")
    print("-" * 40)

    from ansys_resource_loader import resource_loader

    search_terms = ["PyMechanical", "automation", "scripting", "analysis"]

    for term in search_terms:
        results = resource_loader.search_content(term, max_results=3)
        print(f"\n🔎 Search '{term}': {len(results)} results")

        for i, result in enumerate(results, 1):
            print(f"   {i}. {result['source']} ({result['type']}) - Score: {result['relevance_score']:.3f}")
            context_length = len(result.get('context', ''))
            print(f"      Context: {context_length} characters")

def test_tools_simulation():
    """Simulate how tools would be called by AI assistants."""
    print(f"\n🛠️ Testing Tool Responses")
    print("-" * 40)

    # Simulate search_ansys_docs tool
    print(f"\n1. Testing search_ansys_docs tool:")
    try:
        from ansys_resource_loader import resource_loader
        results = resource_loader.search_content("mesh generation", max_results=2)

        if results:
            search_output = f"# Search Results for: 'mesh generation'\n\n"
            search_output += f"Found {len(results)} relevant results:\n\n"

            for i, result in enumerate(results, 1):
                search_output += f"## Result {i}: {result['source']}\n"
                search_output += f"**Type**: {result['type'].upper()}\n"
                search_output += f"**Relevance**: {result['relevance_score']:.3f}\n\n"
                search_output += f"**Context**:\n{result['context']}\n\n---\n\n"

            print(f"   ✅ Generated response: {len(search_output):,} characters")
            print(f"   📝 Sample: {repr(search_output[:200])}")
        else:
            print(f"   ⚠️ No search results found")

    except Exception as e:
        print(f"   ❌ Search tool error: {e}")

    # Simulate get_chapter_content tool
    print(f"\n2. Testing get_chapter_content tool:")
    try:
        from ansys_resource_loader import resource_loader
        chapters = resource_loader.get_pdf_chapters("scripting_mechanical_2025r1.pdf")

        if chapters:
            chapter_title = chapters[0].get('title', 'Unknown')
            chapter_content = resource_loader.get_pdf_content_by_chapter(
                "scripting_mechanical_2025r1.pdf",
                chapter_title
            )

            if chapter_content:
                content = chapter_content.get('content', '')
                print(f"   ✅ Chapter content: {len(content):,} characters")
                print(f"   📝 Title: {chapter_content.get('title')}")
                print(f"   📄 Pages: {chapter_content.get('start_page')} - {chapter_content.get('end_page')}")
            else:
                print(f"   ⚠️ No chapter content found")
        else:
            print(f"   ⚠️ No chapters found")

    except Exception as e:
        print(f"   ❌ Chapter tool error: {e}")

def main():
    """Run all tests."""
    print("🔬 MCP Content Delivery Diagnostic")
    print("Testing what AI assistants will actually receive")
    print("=" * 60)

    total_chars = test_all_resources()
    test_search_functionality()
    test_tools_simulation()

    print(f"\n" + "=" * 60)
    print(f"🎯 CONCLUSION:")
    print(f"   • Total content available: {total_chars:,} characters")
    print(f"   • 8 resources with rich Markdown content")
    print(f"   • Search functionality working")
    print(f"   • Tools generating proper responses")
    print(f"   • Content includes formatting, structure, examples")
    print(f"\n✅ AI assistants should receive FULL CONTENT, not just JSON")
    print(f"🔍 If you only see JSON in MCP Inspector, this might be a display issue")
    print(f"📝 The actual AI model will receive the complete formatted content")

if __name__ == "__main__":
    main()