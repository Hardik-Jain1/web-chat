# 🤖 WebChat AI Assistant

ChatBot uses the RAG(Retrieval Augmented Generation) technique to interact with a given website URL and answer the questions about that website.

Simply provide a URL, and the AI will learn from the website content to answer your questions!

This Chatbot uses the RAG(Retrieval Augmented Generation) technique to get the web scraped data, store it in a vector database, and then retrieve the relevant context from it (w.r.t to the asked question) to provide it to the LLM(ChatGPT) along with question which then generates the relevant output. 

## ✨ Features

- 🌐 **Website Content Extraction**: Fetch and process content from any URL
- 💬 **Interactive Chat Interface**: Modern chat UI with message history
- 📚 **Source Attribution**: See which parts of the website were used to answer your questions
- ⚙️ **Customizable Settings**: Adjust AI temperature, chunk sizes, and more
- 📊 **Real-time Statistics**: Track processing stats and chat metrics

## 🏗️ Project Structure

```
webchat-streamlit-app/
├── src/
│   ├── app.py                     # Main Streamlit application
│   ├── components/                # UI Components
│   │   ├── chat_interface.py      # Chat UI with message history
│   │   └── sidebar.py             # Settings and configuration UI
│   ├── services/                  # Core Services
│   │   ├── ai_provider.py         # AI provider factory (OpenAI/Gemini)
│   │   ├── chatbot_service.py     # Main chatbot logic
│   │   ├── data_fetcher.py        # Website content fetching
│   │   └── document_processor.py  # Text chunking and processing
│   ├── templates/                 # AI Prompt Templates
│   │   └── prompt_templates.py    # Optimized prompts for different providers
│   └── utils/                     # Utilities
│       └── config.py              # Configuration management
├── .streamlit/
│   └── config.toml               # Streamlit theme and settings
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
└── README.md                     # This file
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd webchat-streamlit-app

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the environment template and add your API keys:

```bash
copy .env.example .env
```

Edit `.env` file:
```env
# Choose your preferred AI provider
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
DEFAULT_PROVIDER=openai
```

### 3. Run the Application

```bash
streamlit run src/app.py
```

## 🎯 How to Use

1. **🔧 Configure AI Provider**
   - Open the sidebar
   - Select OpenAI or Gemini as your AI provider
   - Enter your API key
   - Adjust settings if needed

2. **🌐 Fetch Website Data**
   - Enter any website URL
   - Click "Fetch Data"
   - Wait for content processing

3. **💬 Start Chatting**
   - Ask questions about the website
   - View sources for each answer
   - Enjoy the conversation!

## 🛠️ Configuration Options

### AI Provider Settings
- **Provider**: OpenAI GPT or Google Gemini
- **Temperature**: Controls response creativity (0.0-1.0)
- **Website Name**: Customize the chatbot's persona

### Document Processing
- **Chunk Size**: Size of text chunks for processing (500-2000)
- **Chunk Overlap**: Overlap between chunks (50-500)

## 📋 Requirements

- Python 3.8+
- Streamlit
- LangChain
- OpenAI API (optional)
- Google AI API (optional)
- Beautiful Soup 4
- FAISS
- Requests

## 🔑 API Keys

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key

### Google API Key (for Gemini)
1. Go to [Google AI Studio](https://makersuite.google.com/)
2. Create a project
3. Enable the Generative AI API
4. Create an API key

## 🎨 Customization

### Prompts
Modify `src/templates/prompt_templates.py` to customize AI responses:

```python
def get_qa_chain_prompt(website_name: str = "YourWebsite"):
    # Customize your prompt here
    template = f"""Your custom prompt for {website_name}..."""
    return PromptTemplate.from_template(template)
```

## 📈 Features Roadmap

- [ ] 📄 PDF upload support
- [ ] 🔍 Advanced search within chat history
- [ ] 📊 Analytics dashboard
- [ ] 🌍 Multiple language support
- [ ] 🔐 User authentication
- [ ] 💾 Chat history persistence
- [ ] 🎤 Voice input/output
- [ ] 📱 Mobile optimization

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.