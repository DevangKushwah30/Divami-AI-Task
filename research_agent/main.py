from pydantic_ai import Agent
import asyncio
# import logfire  # Commented out - run without Logfire
from dotenv import load_dotenv
import time
from tools import web_search, get_date_time, duck_search, save_research
from colorama import init, Fore, Back, Style
import sys

# Initialize colorama for Windows color support
init(autoreset=True)

# Load environment variables
load_dotenv(override=True)

# Configure logfire for monitoring
# logfire.configure()  # Commented out
# logfire.instrument_pydantic_ai()  # Commented out

# Use Gemini 2.0 Flash
model = "gemini-2.0-flash"

def print_banner():
    """Print a colorful banner"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════╗
{Fore.CYAN}║{Fore.YELLOW}           🔬 RESEARCH PRO - AI Research Assistant                  {Fore.CYAN}║
{Fore.CYAN}║{Fore.GREEN}              Powered by Google Gemini 2.0 Flash                    {Fore.CYAN}║
{Fore.CYAN}╚══════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def print_capabilities():
    """Print available capabilities with icons"""
    print(f"\n{Fore.MAGENTA}╔═══ Available Capabilities ═══╗{Style.RESET_ALL}")
    print(f"{Fore.GREEN}  🔍 Web Search{Fore.CYAN} - Find information from Wikipedia")
    print(f"{Fore.GREEN}  🦆 DuckDuckGo Search{Fore.CYAN} - General web search")
    print(f"{Fore.GREEN}  📅 Date & Time{Fore.CYAN} - Get current date/time")
    print(f"{Fore.GREEN}  💾 Save Research{Fore.CYAN} - Export findings to files")
    print(f"{Fore.MAGENTA}╚═══════════════════════════════╝{Style.RESET_ALL}\n")

def print_status(message, status="info"):
    """Print colored status messages"""
    if status == "info":
        print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")
    elif status == "success":
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
    elif status == "error":
        print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")
    elif status == "thinking":
        print(f"{Fore.YELLOW}🤔 {message}{Style.RESET_ALL}")

def print_separator():
    """Print a separator line"""
    print(f"{Fore.BLUE}{'─' * 70}{Style.RESET_ALL}")

# Create the research agent with enhanced tools
agent = Agent(
    model,
    system_prompt="""You are Research Pro, an expert AI research assistant specializing in comprehensive information gathering and analysis.
    
    Your enhanced capabilities:
    - 🔍 Multi-source web search (Wikipedia, DuckDuckGo)
    - 📅 Real-time date and time information
    - 💾 Save research findings to organized files
    - 📊 Data synthesis and analysis
    
    Research workflow:
    1. Use web_search and duck_search to gather comprehensive information
    2. Cross-reference multiple sources for accuracy
    3. Synthesize findings into clear, well-organized summaries
    4. Offer to save important research using save_research tool
    5. Cite sources and provide URLs when available
    
    Example interactions:
    - "Research Python programming" → Search multiple sources, synthesize info
    - "Who invented the telephone?" → Quick factual answer with sources
    - "Research climate change and save it" → Comprehensive research + file save
    
    Be thorough, accurate, and always cite your sources. Format responses with clear sections and bullet points when appropriate.
    """,
    tools=[web_search, duck_search, get_date_time, save_research]
)

time.sleep(1)


async def main():
    """Main function to run the research agent with enhanced UI"""
    message_history = []
    
    print_banner()
    print_capabilities()
    print_status("Research Pro is ready to assist you!", "success")
    print(f"\n{Fore.YELLOW}Type 'exit', 'quit', or 'bye' to end the session.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Press Ctrl+C for emergency exit.{Style.RESET_ALL}\n")
    print_separator()
    
    conversation_count = 0

    while True:
        try:
            # Prompt with color
            user_input = input(f"\n{Fore.GREEN}You{Fore.WHITE} → {Style.RESET_ALL}")
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                print(f"\n{Fore.CYAN}╔══════════════════════════════════════════╗")
                print(f"{Fore.CYAN}║  {Fore.YELLOW}👋 Thank you for using Research Pro!  {Fore.CYAN}║")
                print(f"{Fore.CYAN}║  {Fore.GREEN}Happy researching and learning!       {Fore.CYAN}║")
                print(f"{Fore.CYAN}╚══════════════════════════════════════════╝{Style.RESET_ALL}\n")
                break
            
            if not user_input.strip():
                continue

            conversation_count += 1
            print_status(f"Processing query #{conversation_count}...", "thinking")
            
            # Animate thinking
            for i in range(3):
                sys.stdout.write(f"\r{Fore.YELLOW}⏳ Analyzing")
                for j in range(i + 1):
                    sys.stdout.write(".")
                sys.stdout.flush()
                time.sleep(0.3)
            print()  # New line after animation

            # Run agent with message history
            response = await agent.run(user_input, message_history=message_history)
            
            # Display response with formatting
            print(f"\n{Fore.MAGENTA}╔═══ Research Pro Response ═══╗{Style.RESET_ALL}")
            print(f"{Fore.WHITE}{response.output}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}╚═══════════════════════════════╝{Style.RESET_ALL}\n")

            # Update message history
            message_history = response.all_messages()
            
            print_status("Response complete!", "success")
            print_separator()
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}⚠ Interrupted by user{Style.RESET_ALL}")
            print(f"{Fore.CYAN}👋 Goodbye! Happy researching!{Style.RESET_ALL}\n")
            break
        except Exception as e:
            print_status(f"Error: {str(e)}", "error")
            # logfire.error(f"Error in main loop: {str(e)}")  # Commented out
            print_separator()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.CYAN}Session terminated. Goodbye!{Style.RESET_ALL}")
