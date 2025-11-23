from pydantic_ai import RunContext
import httpx
import os
from datetime import datetime
import json
import re
from duckduckgo_search import DDGS


async def web_search(ctx: RunContext[str], query: str) -> str:
    """
    Search Wikipedia for comprehensive information.
    
    Args:
        ctx: The run context
        query: The search query to look up
    
    Returns:
        Formatted Wikipedia search results with relevant information
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            results = []
            
            # Try Wikipedia OpenSearch API
            try:
                wiki_response = await client.get(
                    "https://en.wikipedia.org/w/api.php",
                    params={
                        "action": "opensearch",
                        "search": query,
                        "limit": 3,
                        "namespace": 0,
                        "format": "json"
                    },
                    timeout=10.0
                )
                
                if wiki_response.status_code == 200:
                    wiki_data = wiki_response.json()
                    if len(wiki_data) >= 4 and wiki_data[1]:
                        titles = wiki_data[1]
                        descriptions = wiki_data[2]
                        urls = wiki_data[3]
                        
                        results.append(f"📚 **Wikipedia Results:**\n")
                        for i in range(min(len(titles), 3)):
                            if titles[i]:
                                results.append(f"{i+1}. **{titles[i]}**")
                                if i < len(descriptions) and descriptions[i]:
                                    results.append(f"   {descriptions[i]}")
                                if i < len(urls) and urls[i]:
                                    results.append(f"   🔗 {urls[i]}\n")
                        
                        if results:
                            return "\n".join(results)
            except Exception as e:
                pass
                
            return f"No Wikipedia results found for '{query}'"
            
    except Exception as e:
        return f"Search error: {str(e)[:150]}"

async def duck_search(ctx: RunContext[str], query: str) -> str:
    """
    Perform a DuckDuckGo web search for general information.
    
    Args:
        ctx: The run context
        query: The search query to look up
    Returns:
        Formatted DuckDuckGo search results with URLs and descriptions
    """ 
    try:
        with DDGS() as ddgs:
            results = []
            for r in ddgs.text(query, max_results=3):
                title = r.get('title', 'No Title')
                snippet = r.get('body', 'No Snippet')
                url = r.get('url', 'No URL')
                
                results.append(f"**{title}**\n{snippet}\n🔗 {url}\n")
            
            if results:
                return "🦆 **DuckDuckGo Results:**\n\n" + "\n".join(results)
            else:
                return f"No DuckDuckGo results found for '{query}'"
    except Exception as e:
        return f"DuckDuckGo search error: {str(e)[:150]}"

async def get_date_time(ctx: RunContext[str]) -> str:
    """
    Get the current date and time with detailed formatting.
    
    Args:
        ctx: The run context
    
    Returns:
        Current date and time formatted as a detailed string
    """
    now = datetime.now()
    return f"📅 **Current Date & Time:**\n{now.strftime('%A, %B %d, %Y at %I:%M:%S %p')}"

async def save_research(ctx: RunContext[str], filename: str, content: str) -> str:
    """
    Save research findings to a file in the research_outputs folder.
    
    Args:
        ctx: The run context
        filename: Name of the file (without extension, .txt will be added)
        content: The research content to save
    
    Returns:
        Confirmation message with file path
    """
    try:
        # Create research_outputs directory if it doesn't exist
        output_dir = "research_outputs"
        os.makedirs(output_dir, exist_ok=True)
        
        # Clean filename and add timestamp
        clean_filename = re.sub(r'[^\w\s-]', '', filename).strip()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_filename = f"{clean_filename}_{timestamp}.txt"
        filepath = os.path.join(output_dir, full_filename)
        
        # Add header to content
        header = f"""
{'=' * 70}
RESEARCH REPORT
{'=' * 70}
Topic: {filename}
Generated: {datetime.now().strftime('%A, %B %d, %Y at %I:%M:%S %p')}
{'=' * 70}

"""
        full_content = header + content
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        return f"✅ **Research saved successfully!**\n📁 File: {filepath}\n📊 Size: {len(content)} characters"
        
    except Exception as e:
        return f"❌ Error saving research: {str(e)}"
