# Multi-Agent Research Assistant

A lightweight research assistant built with Python, LangChain, Streamlit, and Tavily. It coordinates specialized LLM agent roles to gather web sources, scrape relevant web pages, synthesize a research report, and evaluate report quality.

## Features

- **Web Search Agent**: Queries Tavily for recent articles and online sources.
- **Reader Agent**: Scrapes and cleans web pages for deeper contextual evidence.
- **Writer Agent**: Synthesizes search results and scraped content into a structured report (introduction, key findings, conclusion, sources).
- **Critic Agent**: Evaluates the report and outputs a score out of 10, list of strengths, areas for improvement, and a final verdict.
- **Streamlit Web UI**: Web interface with progress status, raw data expanders, and markdown report download.

## Project Structure

```
.
├── app.py           # Streamlit user interface
├── pipeline.py      # Workflow orchestration
├── agents.py        # Agent and chain setups (supports Groq & OpenAI)
├── tools.py         # Web search and web scraping tools
├── requirements.txt # Python dependencies
└── .env.example     # Environment variable template
```

## Setup & Running

### 1. Clone and install dependencies

```bash
git clone https://github.com/AkarshiAaryan/multi-agent-rag.git
cd multi-agent-rag
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Add your API keys to `.env`:

```env
TAVILY_API_KEY=your_tavily_api_key
GROQ_API_KEY=your_groq_api_key
# or OPENAI_API_KEY=your_openai_api_key
```

### 3. Run

**Streamlit Web Interface**:
```bash
streamlit run app.py
```

**Terminal CLI**:
```bash
python pipeline.py
```
