from fasthtml.common import *
from agent import Agent
import json
from datetime import datetime

app, rt = fast_app()

# Initialize agent
agent = Agent()

# Store messages as tuples (user_message, response, timestamp)
messages = []

# Store cart items with enhanced data
cart = {}

# Add favorites system
favorites = set()

@rt('/')
def get():
    # Clear messages and cart on page load
    global messages, cart
    messages = []
    cart = {}

    return Titled("🛍️ ShopSmart AI - Your Intelligent Shopping Assistant",
        Style("""
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            @keyframes slideIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.02); }
            }
            
            @keyframes shimmer {
                0% { background-position: -1000px 0; }
                100% { background-position: 1000px 0; }
            }
            
            .chat-msg { 
                animation: slideIn 0.3s ease-out; 
            }
            
            .cart-item { 
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                animation: slideIn 0.4s ease-out;
                position: relative;
                overflow: hidden;
            }
            
            .cart-item::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                transition: left 0.5s;
            }
            
            .cart-item:hover::before {
                left: 100%;
            }
            
            .cart-item:hover { 
                transform: translateY(-8px) scale(1.02);
                box-shadow: 0 12px 24px rgba(0,0,0,0.25) !important;
            }
            
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                background-size: 200% 200%;
                animation: gradientShift 15s ease infinite;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                min-height: 100vh;
            }
            
            @keyframes gradientShift {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            
            .main-container {
                max-width: 1600px;
                margin: 0 auto;
                padding: 20px 20px 140px 20px;
            }
            
            .app-header {
                text-align: center;
                color: white;
                margin-bottom: 25px;
                animation: fadeIn 0.6s ease-out;
            }
            
            .app-title {
                font-size: 42px;
                font-weight: 800;
                text-shadow: 0 4px 15px rgba(0,0,0,0.3);
                margin-bottom: 8px;
                letter-spacing: -1px;
            }
            
            .app-subtitle {
                font-size: 16px;
                opacity: 0.95;
                font-weight: 400;
                text-shadow: 0 2px 8px rgba(0,0,0,0.2);
            }
            
            .stats-bar {
                display: flex;
                gap: 15px;
                margin-bottom: 20px;
                animation: fadeIn 0.8s ease-out;
            }
            
            .stat-card {
                flex: 1;
                background: rgba(255,255,255,0.15);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 15px 20px;
                color: white;
                border: 1px solid rgba(255,255,255,0.2);
                transition: all 0.3s ease;
            }
            
            .stat-card:hover {
                background: rgba(255,255,255,0.25);
                transform: translateY(-3px);
            }
            
            .stat-label {
                font-size: 12px;
                opacity: 0.9;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 5px;
            }
            
            .stat-value {
                font-size: 24px;
                font-weight: 700;
            }
            
            .empty-state {
                text-align: center;
                padding: 40px 20px;
                color: #999;
            }
            
            .empty-state-icon {
                font-size: 48px;
                margin-bottom: 15px;
                opacity: 0.5;
            }
            
            .empty-state-text {
                font-size: 16px;
                line-height: 1.6;
            }
        """),
        Div(
            # App Header
            Div(
                Div("🛍️ ShopSmart AI", cls='app-title'),
                Div("Your Intelligent Shopping Companion Powered by AI", cls='app-subtitle'),
                cls='app-header'
            ),
            
            # Stats Bar
            Div(
                Div(
                    Div("💬 Messages", cls='stat-label'),
                    Div("0", id='msg-count', cls='stat-value'),
                    cls='stat-card'
                ),
                Div(
                    Div("🛒 Cart Items", cls='stat-label'),
                    Div("0", id='cart-count', cls='stat-value'),
                    cls='stat-card'
                ),
                Div(
                    Div("💰 Total Price", cls='stat-label'),
                    Div("$0.00", id='total-price', cls='stat-value'),
                    cls='stat-card'
                ),
                cls='stats-bar'
            ),
            
            # Main Content Area
            Div(
                # Left section - Chat
                Div(
                    Div(
                        Div("💬 Chat Assistant", style='font-size: 18px; color: white; font-weight: 700; display: flex; align-items: center; gap: 8px;'),
                        style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 18px 24px; border-radius: 16px 16px 0 0; box-shadow: 0 4px 15px rgba(0,0,0,0.15);'
                    ),
                    Div(
                        Div(
                            # Empty state for chat
                            Div(
                                Div("💭", cls='empty-state-icon'),
                                Div("Start chatting with ShopSmart AI! - Try: 'add 3 red apples' or 'what's in my cart?'", cls='empty-state-text'),
                                cls='empty-state',
                                id='chat-empty'
                            ),
                            id='chat-result', 
                            style='flex: 1; overflow-y: auto; padding: 20px; border-radius: 0 0 14px 14px; max-height: calc(75vh - 140px); background: white;'
                        ),
                        style='background: white; border-radius: 0 0 16px 16px; overflow: hidden; flex: 1;'
                    ),
                    style='flex: 1; display: flex; flex-direction: column; box-shadow: 0 15px 50px rgba(102, 126, 234, 0.35); border-radius: 16px; overflow: hidden; background: white;'
                ),
                
                # Right section - Cart
                Div(
                    Div(
                        Div("🛒 Shopping Cart", style='font-size: 18px; color: white; font-weight: 700; display: flex; align-items: center; gap: 8px;'),
                        style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 18px 24px; border-radius: 16px 16px 0 0; box-shadow: 0 4px 15px rgba(0,0,0,0.15);'
                    ),
                    Div(
                        Div(
                            # Empty state for cart
                            Div(
                                Div("🛍️", cls='empty-state-icon'),
                                Div("Your cart is empty - Add items to get started!", cls='empty-state-text'),
                                cls='empty-state',
                                id='cart-empty'
                            ),
                            id='cart-result', 
                            style='flex: 1; overflow-y: auto; padding: 20px; background: white; border-radius: 0 0 14px 14px; max-height: calc(75vh - 140px);'
                        ),
                        style='background: white; border-radius: 0 0 16px 16px; overflow: hidden; flex: 1;'
                    ),
                    style='flex: 1; display: flex; flex-direction: column; box-shadow: 0 15px 50px rgba(245, 87, 108, 0.35); border-radius: 16px; overflow: hidden; background: white;'
                ),
                style='display: flex; gap: 24px; margin-bottom: 20px;'
            ),
            cls='main-container'
        ),
        # Input form at bottom with modern design
        Form(
            Div(
                Input(
                    id='prompt', 
                    name='prompt', 
                    placeholder='💬 Type your message... (e.g., "add 2 red apples" or "what\'s my total?")', 
                    required=True, 
                    autocomplete='off',
                    style='flex: 1; padding: 20px 28px; font-size: 18px; border-radius: 30px; border: 2px solid rgba(255,255,255,0.4); background: white; transition: all 0.3s; outline: none; box-shadow: 0 4px 15px rgba(0,0,0,0.1);',
                    onfocus="this.style.borderColor='#667eea'; this.style.boxShadow='0 6px 20px rgba(102,126,234,0.4)'",
                    onblur="this.style.borderColor='rgba(255,255,255,0.4)'; this.style.boxShadow='0 4px 15px rgba(0,0,0,0.1)'"
                ),
                Button(
                    '🚀 Send', 
                    type='submit', 
                    style='padding: 20px 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-size: 18px; font-weight: 700; border-radius: 30px; border: none; cursor: pointer; transition: all 0.3s; box-shadow: 0 6px 20px rgba(102,126,234,0.5); margin-left: 15px; white-space: nowrap;  width: 10%;',
                    onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 25px rgba(102,126,234,0.6)'",
                    onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 6px 20px rgba(102,126,234,0.5)'"
                ),
                style='display: flex; align-items: center; max-width: 1400px; margin: 0 auto; width: 100%;'
            ),
            hx_post='/submit',
            hx_target='#chat-result',
            hx_swap='innerHTML',
            **{'hx-on::after-request': 'this.reset()'},
            style='position: fixed; bottom: 0; left: 0; right: 0; background: rgba(255,255,255,0.15); backdrop-filter: blur(20px); padding: 20px 30px; border-top: 1px solid rgba(255,255,255,0.25); box-shadow: 0 -5px 30px rgba(0,0,0,0.15); z-index: 1000;'
        )
    )

@rt('/submit')
async def post(prompt: str):
    try:
        # Get response from agent asynchronously with cart context
        response = await agent.get_response_async(prompt, cart_context=cart)

        # Process the response
        chat_message = ""
        try:
            # Remove markdown code blocks if present
            cleaned_response = response.strip()
            if cleaned_response.startswith('```'):
                lines = cleaned_response.split('\n')
                cleaned_response = '\n'.join(lines[1:-1]).strip()

            response_data = json.loads(cleaned_response)
            action = response_data.get('action')

            if action == 'add':
                # Handle multiple items with price tracking
                items = response_data.get('items', [])
                added_items = []

                for item in items:
                    product_name = item.get('name', 'Unknown')
                    quantity = item.get('quantity', 1)
                    color = item.get('color', '')
                    price = item.get('price', 0.0)  # Get price from AI

                    # Validate and fallback to generated color if invalid
                    if not color or not color.strip() or color.strip() == '#':
                        color = agent.generate_color_from_title(product_name)

                    attributes = item.get('attributes', '')

                    # Create unique key with attributes if present
                    cart_key = f"{product_name} ({attributes})" if attributes else product_name

                    # Update cart with price tracking
                    if cart_key in cart:
                        cart[cart_key]['quantity'] += quantity
                    else:
                        cart[cart_key] = {'quantity': quantity, 'color': color, 'price': price}

                    added_items.append(f"{quantity} {cart_key}")

                # Calculate total
                total_price = sum(item['quantity'] * item.get('price', 0) for item in cart.values())
                chat_message = f"✅ Added {', '.join(added_items)} to cart (Total: ${total_price:.2f})"

            elif action == 'remove':
                product_name = response_data.get('name', 'Unknown')
                remove_quantity = response_data.get('quantity', 0)  # 0 means remove all

                # Find matching product in cart (could have attributes)
                found_key = None
                for key in cart.keys():
                    if key.startswith(product_name):
                        found_key = key
                        break

                # Remove from cart
                if found_key:
                    current_quantity = cart[found_key]['quantity']

                    if remove_quantity == 0 or remove_quantity >= current_quantity:
                        # Remove entire item
                        del cart[found_key]
                        chat_message = f"🗑️ Removed {found_key} from cart"
                    else:
                        # Reduce quantity
                        cart[found_key]['quantity'] -= remove_quantity
                        chat_message = f"➖ Removed {remove_quantity} {found_key} (Remaining: {cart[found_key]['quantity']})"
                else:
                    chat_message = f"❌ {product_name} not found in cart"
            else:
                chat_message = response

        except (json.JSONDecodeError, TypeError):
            # Not JSON, regular chat message
            chat_message = response

        # Add to messages with timestamp
        timestamp = datetime.now().strftime("%I:%M %p")
        messages.append((prompt, chat_message, timestamp))

        # Build chat display with modern styling
        chat_display = []
        for user_msg, bot_msg, time_str in messages:
            # User message - right aligned with gradient background
            chat_display.append(
                Div(
                    Div(
                        Div(user_msg, style='margin-bottom: 6px; font-weight: 500; line-height: 1.5;'),
                        Div(time_str, style='font-size: 10px; opacity: 0.8; text-align: right;'),
                        style='display: inline-block; padding: 16px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 24px 24px 6px 24px; max-width: 75%; word-wrap: break-word; box-shadow: 0 4px 12px rgba(102,126,234,0.4);'
                    ),
                    style='text-align: right; margin-bottom: 16px; animation: slideIn 0.3s ease-out;'
                )
            )
            # Bot message - left aligned with card style
            chat_display.append(
                Div(
                    Div(
                        Div(
                            Div("🤖", style='font-size: 20px;'),
                            Div("ShopSmart AI", style='font-weight: 700; color: #667eea;'),
                            style='display: flex; align-items: center; gap: 8px; margin-bottom: 8px; padding-bottom: 8px; border-bottom: 2px solid #f0f0f0;'
                        ),
                        Div(bot_msg, style='margin-bottom: 8px; line-height: 1.6; color: #2d3748; font-size: 15px;'),
                        Div(time_str, style='font-size: 10px; opacity: 0.5; text-align: left;'),
                        style='display: inline-block; padding: 18px 22px; background: linear-gradient(to bottom, #ffffff 0%, #f8f9ff 100%); color: #2d3748; border-radius: 24px 24px 24px 6px; max-width: 75%; word-wrap: break-word; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border: 2px solid #f0f0f0;'
                    ),
                    style='text-align: left; margin-bottom: 20px; animation: slideIn 0.3s ease-out;'
                )
            )

        # Return both chat and cart updates using out-of-band swaps
        cart_display = []
        total_items = sum(item['quantity'] for item in cart.values())
        total_price = sum(item['quantity'] * item.get('price', 0) for item in cart.values())
        
        # Add total price banner with enhanced styling
        if cart:
            cart_display.append(
                Div(
                    Div(
                        Div("💰", style='font-size: 28px; margin-right: 12px;'),
                        Div(
                            Div("Cart Total", style='font-size: 13px; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px;'),
                            Div(f"${total_price:.2f}", style='font-size: 28px; font-weight: 800; margin-top: 4px;'),
                            style='flex: 1;'
                        ),
                        style='display: flex; align-items: center; color: white;'
                    ),
                    style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 20px 24px; border-radius: 16px; margin-bottom: 20px; box-shadow: 0 6px 20px rgba(56, 239, 125, 0.4); animation: pulse 2s infinite;'
                )
            )
        
        for product_name, item_data in cart.items():
            quantity = item_data['quantity']
            bg_color = item_data['color']
            price = item_data.get('price', 0)
            item_total = quantity * price
            text_color = agent.get_text_color(bg_color)
            
            cart_display.append(
                Div(
                    Div(
                        Div(
                            Div("🏷️", style=f'font-size: 24px; margin-right: 12px; color: {text_color};'),
                            Div(
                                Div(product_name, style=f'font-weight: 700; font-size: 18px; color: {text_color}; margin-bottom: 4px;'),
                                Div(
                                    Div(
                                        Div("Qty", style=f'font-size: 11px; opacity: 0.8; text-transform: uppercase; color: {text_color};'),
                                        Div(str(quantity), style=f'font-size: 20px; font-weight: 700; color: {text_color};'),
                                    ),
                                    Div(
                                        Div("Price", style=f'font-size: 11px; opacity: 0.8; text-transform: uppercase; color: {text_color}; text-align: right;'),
                                        Div(f'${item_total:.2f}', style=f'font-size: 20px; font-weight: 700; color: {text_color};'),
                                    ),
                                    style='display: flex; justify-content: space-between; gap: 20px; margin-top: 8px;'
                                ),
                                style='flex: 1;'
                            ),
                            style='display: flex; align-items: center;'
                        ),
                        style=f'padding: 20px 24px; background: linear-gradient(135deg, {bg_color} 0%, {bg_color}dd 100%); border-radius: 16px;'
                    ),
                    style='margin-bottom: 16px;',
                    cls='cart-item'
                )
            )

        return Div(
            Div(*chat_display) if chat_display else Div(
                Div("💭", cls='empty-state-icon'),
                Div("Start chatting with ShopSmart AI! - Try: 'add 3 red apples' or 'what's in my cart?'", cls='empty-state-text'),
                cls='empty-state'
            ),
            Div(id='cart-result', hx_swap_oob='true', *(cart_display if cart_display else [
                Div(
                    Div("🛍️", cls='empty-state-icon'),
                    Div("Your cart is empty - Add items to get started!", cls='empty-state-text'),
                    cls='empty-state'
                )
            ])),
            Div(str(len(messages)), id='msg-count', hx_swap_oob='true', cls='stat-value'),
            Div(str(total_items), id='cart-count', hx_swap_oob='true', cls='stat-value'),
            Div(f"${total_price:.2f}", id='total-price', hx_swap_oob='true', cls='stat-value')
        )

    except Exception as e:
        print(f"Error in /submit: {e}")
        import traceback
        traceback.print_exc()
        return Div(f"Error: {str(e)}", style='color: red; padding: 10px;')

serve(port=5004)

