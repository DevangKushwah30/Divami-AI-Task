# 🤖 AI Assistant Suite

Two AI-powered applications built with Pydantic AI and Google Gemini models.

---

## 🛍️ ShopSmart AI - E-Commerce Assistant

Intelligent shopping cart with natural language processing and price tracking.

### Setup

```bash
cd e-commerce
pip install python-fasthtml pydantic-ai python-dotenv logfire
echo "GOOGLE_API_KEY=your_key_here" > .env
python app.py
# Open: http://localhost:5004
```

### Features

- 🗣️ Natural language product management
- 💰 Automatic price tracking and cart totals
- 🎨 Smart color detection for products
- ⚡ Real-time updates with animations
- 🔄 Auto-retry on API errors
- 💬 Conversation history

### Usage Examples

```
"add 3 red apples"              → Adds with price estimate
"purple dress size M"           → Adds clothing with attributes
"2 bananas and 3 oranges"       → Adds multiple items
"what's my total?"              → Shows cart summary
"remove apples"                 → Removes items
```

---

## 🔬 Research Pro - AI Research Agent

Terminal-based research assistant with multi-source search and file export.

### Setup

```bash
cd research_agent
pip install pydantic-ai httpx python-dotenv logfire colorama duckduckgo-search
echo "GOOGLE_API_KEY=your_key_here" > .env
python main.py
```

### Features

- 🔍 Multi-source search (Wikipedia + DuckDuckGo)
- 💾 Export research to formatted files
- 🎨 Colorful terminal interface
- 📅 Date/time queries
- 🧠 Conversation memory

### Usage Examples

```
You → Research artificial intelligence
You → Who invented the telephone?
You → Research Python and save it
```

Exit: `exit`, `quit`, `bye`, or `Ctrl+C`

---

## 🔧 Setup Guide

### Get API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Generate API key (starts with "AIza")
3. Add to `.env` file in each project folder

### .env Format

```env
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

---

## 🐛 Troubleshooting

**API Key Error**
- Verify `.env` file exists
- Check key starts with "AIza"
- Remove quotes/spaces

**503 Model Overloaded**
- ShopSmart AI: Auto-retries 3 times
- Research Pro: Wait 1-2 minutes

**Port In Use**
```python
# Change in app.py:
serve(port=5005)
```

---

## 🎯 Tech Stack

- **AI**: Google Gemini 2.5/2.0 Flash
- **Framework**: Pydantic AI
- **UI**: FastHTML (Web) + Colorama (CLI)
- **Monitoring**: Logfire

---

## 📊 Comparison

| Feature | ShopSmart AI | Research Pro |
|---------|--------------|--------------|
| Interface | Web Browser | Terminal |
| Persistence | Session | Files |
| Tools | Price Tracking | 4 Search Tools |
| UI Style | Gradient Animations | Colored Text |

---

**Built with ❤️ using Google Gemini & Pydantic AI**