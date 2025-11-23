from pydantic_ai import Agent as PydanticAgent
import asyncio
# import logfire  # Commented out - run without Logfire
from dotenv import load_dotenv
import os
import json
import hashlib
import time

load_dotenv(override=True)
# logfire.configure()  # Commented out
# logfire.instrument_pydantic_ai()  # Commented out

# Get API key from environment - this will be automatically picked up by pydantic-ai
google_api_key = os.getenv("GOOGLE_API_KEY")

# Strip any whitespace or quotes that might have been added
if google_api_key:
    google_api_key = google_api_key.strip().strip('"').strip("'")
    # Set it back to environment for pydantic-ai to use
    os.environ["GOOGLE_API_KEY"] = google_api_key

# Check if API key is set
if not google_api_key:
    raise ValueError(
        "GOOGLE_API_KEY not found in environment variables. "
        "Please check your .env file"
    )

print(f"Using API key: {google_api_key[:10]}...{google_api_key[-4:] if len(google_api_key) > 14 else ''}")

# Validate API key format
if not google_api_key.startswith("AIza"):
    raise ValueError(
        f"Invalid Google API key format. Google API keys should start with 'AIza'. "
        f"Your key starts with: {google_api_key[:10]}"
    )

model = "gemini-2.5-flash"

class Agent:
    def __init__(self):
        # Enhanced system prompt with price tracking and recommendations
        system_prompt = """
            You are ShopSmart AI, an intelligent shopping assistant with advanced capabilities.

            CORE FEATURES:
            - Smart product management (add/remove/update)
            - Price tracking and budget monitoring
            - Personalized recommendations
            - Shopping list management
            - Product information and comparisons

            ALLOWED TOPICS:
            - Adding/removing products with price tracking
            - Budget queries and spending analysis
            - Product recommendations based on preferences
            - Shopping assistance and product information
            - Cart management and order queries

            NOT ALLOWED: General knowledge, weather, news, math problems, programming help, etc.

            When users ADD products (supports multiple items):
            - Response format: {"action": "add", "items": [{"name": "ProductName", "quantity": number, "color": "#hexcolor", "attributes": "description", "price": number}]}
            - Detect natural colors and provide hex codes
            - Include prices (estimate if not specified)
            - Examples:
            * "add 2 apples" → {"action": "add", "items": [{"name": "Apples", "quantity": 2, "color": "#DC143C", "attributes": "", "price": 3.99}]}
            * "purple top size M for $25" → {"action": "add", "items": [{"name": "Top", "quantity": 1, "color": "#800080", "attributes": "Purple, Size M", "price": 25.00}]}
            * "3 bananas and 2 oranges" → {"action": "add", "items": [{"name": "Bananas", "quantity": 3, "color": "#FFE135", "attributes": "", "price": 2.99}, {"name": "Oranges", "quantity": 2, "color": "#FFA500", "attributes": "", "price": 4.49}]}

            When users REMOVE products:
            - Response: {"action": "remove", "name": "ProductName", "quantity": number}
            - quantity: 0 means remove all instances
            * "remove grapes" → {"action": "remove", "name": "Grapes", "quantity": 0}
            * "remove 1 laptop" → {"action": "remove", "name": "Laptop", "quantity": 1}

            When users ask CART QUERIES (items count, total price, budget):
            - Analyze the cart context provided
            - Respond naturally with insights
            - No JSON needed, just conversational text

            SMART FEATURES:
            - Track total spending
            - Suggest alternatives for expensive items
            - Remind about budget if items exceed reasonable amounts
            - Group similar items in responses

            Always capitalize product names. Return JSON only for add/remove actions.
            """
        self.agent = PydanticAgent(model, system_prompt=system_prompt)
        self.message_history = []
        self.user_preferences = {}  # Track user preferences over time
    
    async def get_response_async(self, user_message: str, cart_context: dict = None) -> str:
        """Get a response from the AI agent asynchronously with retry logic"""
        # Add cart context to the message if available
        if cart_context:
            cart_info = "\n\nCurrent cart contents:\n"
            if not cart_context:
                cart_info += "Cart is empty"
            else:
                for item_name, item_data in cart_context.items():
                    cart_info += f"- {item_name}: {item_data['quantity']} item(s)\n"
            
            enhanced_message = user_message + cart_info
        else:
            enhanced_message = user_message
        
        # Retry logic for handling 503 errors
        max_retries = 3
        retry_delay = 2  # Start with 2 seconds
        
        for attempt in range(max_retries):
            try:
                # Pass the message history to maintain context
                response = await self.agent.run(enhanced_message, message_history=self.message_history)
                
                # Update message history with new messages from this run
                self.message_history = response.all_messages()
                
                return response.output
                
            except Exception as e:
                error_msg = str(e)
                
                # Check if it's a 503 error
                if '503' in error_msg or 'overloaded' in error_msg.lower():
                    if attempt < max_retries - 1:
                        print(f"⚠️ Model overloaded, retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        return "⚠️ The AI model is currently overloaded. Please try again in a moment."
                else:
                    # For other errors, raise immediately
                    raise e
        
        return "⚠️ Unable to connect to AI service. Please try again later."
    
    def get_response(self, user_message: str) -> str:
        """Synchronous wrapper for get_response_async"""
        return asyncio.run(self.get_response_async(user_message))
    
    @staticmethod
    def generate_color_from_title(title: str) -> str:
        """Generate a consistent color from a title using hash"""
        # Generate hash from title
        hash_object = hashlib.md5(title.encode())
        hash_hex = hash_object.hexdigest()
        
        # Use first 6 characters as color, ensure it's not too dark
        r = int(hash_hex[0:2], 16)
        g = int(hash_hex[2:4], 16)
        b = int(hash_hex[4:6], 16)
        
        # Make colors lighter by ensuring minimum brightness
        r = max(r, 100)
        g = max(g, 100)
        b = max(b, 100)
        
        return f'#{r:02x}{g:02x}{b:02x}'
    
    @staticmethod
    def get_text_color(bg_color: str) -> str:
        """Determine if text should be white or black based on background color brightness"""
        try:
            # Remove # if present and handle empty/invalid colors
            hex_color = bg_color.lstrip('#').strip()
            
            # Default to black text if color is invalid
            if not hex_color or len(hex_color) < 6:
                return '#000000'
            
            # Convert to RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Calculate relative luminance (perceived brightness)
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            
            # Return black text for light backgrounds, white text for dark backgrounds
            return '#000000' if luminance > 0.5 else '#FFFFFF'
        except (ValueError, IndexError):
            # Default to black text on error
            return '#000000'
