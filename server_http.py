#!/usr/bin/env python3
"""
MCP Server with HTTP/SSE Transport
This version uses Server-Sent Events over HTTP instead of stdio
"""

from mcp.server.fastmcp import FastMCP

# Create MCP server instance with HTTP settings
mcp = FastMCP(
    "TechCorp Solutions HTTP Server",
    host="127.0.0.1",
    port=8001,
    debug=True
)

# Resources using individual decorators
@mcp.resource("text://company_info")
def get_company_info() -> str:
    """Get basic information about TechCorp Solutions."""
    return """
    Company: TechCorp Solutions
    Founded: 2020
    Employees: 150
    Headquarters: San Francisco, CA
    Mission: Building innovative software solutions for modern businesses.
    """

@mcp.resource("text://product_catalog")
def get_product_catalog() -> str:
    """Get list of available products and pricing."""
    return """
    Products:
    1. CloudSync Pro - Enterprise file synchronization ($99/month)
    2. DataViz Analytics - Business intelligence dashboard ($149/month)
    3. SecureVault - Encrypted data storage ($79/month)
    4. WorkFlow Manager - Project management suite ($119/month)
    """

@mcp.resource("text://api_docs")
def get_api_docs() -> str:
    """Get REST API documentation and usage guidelines."""
    return """
    API Documentation:

    Authentication: Bearer token required in Authorization header
    Base URL: https://api.techcorp.com/v1/

    Endpoints:
    - GET /users - List all users
    - POST /users - Create new user
    - GET /projects - List projects
    - POST /projects - Create project

    Rate Limits: 1000 requests per hour per API key
    """

# Prompts using individual decorators
@mcp.prompt()
def analyze_data(data_type: str, time_period: str = "monthly", focus_area: str = "overall trends") -> str:
    """
    Analyze business data and provide insights.

    Args:
        data_type: Type of data to analyze (sales, users, performance, etc.)
        time_period: Time period for analysis (daily, weekly, monthly, yearly)
        focus_area: Specific area to focus the analysis on
    """
    return f"""
Please analyze the following {data_type} with a focus on {focus_area}.

Analysis Parameters:
- Data Type: {data_type}
- Time Period: {time_period}
- Focus Area: {focus_area}

Please provide:
1. Key trends and patterns
2. Notable insights or anomalies
3. Actionable recommendations
4. Areas that need further investigation

Format your response with clear sections and bullet points for easy reading.
"""

@mcp.prompt()
def write_email(recipient_type: str, purpose: str, tone: str = "professional") -> str:
    """
    Generate a professional email template.

    Args:
        recipient_type: Type of recipient (customer, partner, employee, etc.)
        purpose: Purpose of the email (announcement, follow-up, request, etc.)
        tone: Desired tone (formal, friendly, urgent, etc.)
    """
    return f"""
Write a {tone} email for a {recipient_type} with the purpose of {purpose}.

Email Guidelines:
- Recipient: {recipient_type}
- Purpose: {purpose}
- Tone: {tone}

Please include:
1. Appropriate subject line
2. Professional greeting
3. Clear and concise body content
4. Appropriate closing
5. Call to action if needed

Keep the email focused and respectful of the recipient's time.
"""

@mcp.prompt()
def code_review(language: str, project_type: str = "application") -> str:
    """
    Generate code review checklist and guidelines.

    Args:
        language: Programming language (python, javascript, java, etc.)
        project_type: Type of project (web app, API, mobile, etc.)
    """
    return f"""
Create a code review checklist for a {language} {project_type}.

Review Focus:
- Language: {language}
- Project Type: {project_type}

Please provide a comprehensive checklist covering:
1. Code quality and style
2. Security considerations
3. Performance optimization
4. Best practices specific to {language}
5. Documentation and comments
6. Testing coverage
7. Error handling

Format as a checklist with clear categories and specific items to verify.
"""

# Run the server with SSE transport
if __name__ == "__main__":
    print("🚀 Starting MCP Server with HTTP/SSE transport")
    print("=" * 60)
    print(f"Server URL: http://127.0.0.1:8001")
    print(f"SSE Endpoint: http://127.0.0.1:8001/sse")
    print("")
    print("Server capabilities:")
    print("  📄 3 Resources:")
    print("    • text://company_info - Company Information")
    print("    • text://product_catalog - Product Catalog")
    print("    • text://api_docs - API Documentation")
    print("")
    print("  🎯 3 Prompts:")
    print("    • analyze_data - Business data analysis")
    print("    • write_email - Professional email templates")
    print("    • code_review - Code review checklists")
    print("")
    print("Connect MCP Inspector to: http://127.0.0.1:8001/sse")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)

    # Run with SSE transport (HTTP)
    mcp.run(transport="sse")