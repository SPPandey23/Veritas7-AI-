# 🕵️‍♂️ AI Research Agent: Autonomous Multi-Agent Research System

> **An advanced, self-healing RAG pipeline that autonomously plans, researches, synthesizes, and refines complex queries into comprehensive answers.**

---

## 📖 Overview

The **AI Research Agent** is a cutting-edge multi-agent system designed to tackle complex research questions without human intervention. By leveraging the power of **LangGraph**, **Groq (Llama 3)**, and **Streamlit**, this project transforms a simple user prompt into a rigorous, multi-step investigation. 

**The Problem:** Traditional LLM prompts often yield shallow, hallucinated, or unverified answers for deep technical or academic queries. 
**The Solution:** A 7-stage, cyclic graph-based architecture that simulates a team of expert researchers. It breaks down the problem, searches the web, extracts document context, criticizes its own drafts, and iteratively refines the final output until it meets a high-quality threshold.

---

## ✨ Key Technical Innovations

- **Agentic Reasoning (LangGraph):** Orchestrates a cyclic, stateful workflow where multiple specialized agents pass information and evaluate each other's work.
- **Self-Healing Loop:** Integrates a designated `Critic` agent that grades generated drafts. If a draft fails the quality threshold, it is sent to a `Refiner` agent iteratively until it passes.
- **Dynamic Context Gathering:** Uses `Tavily` for web search and `BeautifulSoup4` for deep scraping to build up-to-date context, ensuring ground-truth accuracy beyond pre-trained knowledge.
- **Efficient Vector Search:** Implements `ChromaDB` and `SentenceTransformers` for rapid semantic chunking and retrieval of context, optimizing LLM context window limits.

---

## ⚙️ The Workflow: How it Works

The entire pipeline is structured as a directed graph where state flows continuously between nodes.

```mermaid
graph TD
    User([User Query]) --> P[Planner]
    P --> |Sub-questions| QR[Query Rewriter]
    QR --> |Search Keywords| R[Researcher / Gatherer]
    R --> |Raw Context & Docs| S[Summarizer]
    S --> |Rich Context Brief| G[Generator]
    G --> |Draft Answer| C{Critic}
    C --> |Passes Threshold| F([Final Answer])
    C --> |Fails Threshold| RF[Refiner]
    RF --> |Corrected Draft| C
```

### The 7 Stages of Research:
1. **Planner (`agents.planner`):** Analyzes the root query and generates logical sub-questions.
2. **Query Rewriter (`agents.query_rewriter`):** Optimizes sub-questions into highly effective search engine keywords.
3. **Researcher (`agents.research_agent`):** Scrapes the web (via Tavily) and vectorizes relevant information.
4. **Summarizer (`agents.summarizer`):** Condenses the massive raw HTML/text into a dense, high-signal context brief.
5. **Generator (`agents.generator`):** Drafts the initial comprehensive answer using the synthesized brief.
6. **Critic (`agents.critic_agent`):** Rigorously evaluates the draft against the original query for accuracy and completeness. Provide a verdict and score.
7. **Refiner (`agents.refiner`):** Iteratively corrects the draft based on the Critic's feedback (only triggers if the draft fails).

---

## 🛠️ Technology Stack

- **Core Frameworks:** Python, LangGraph, LangChain
- **LLM Engine:** Groq API (Llama 3 family)
- **Search & Retrieval:** Tavily API, BeautifulSoup4
- **Vector Database:** ChromaDB, SentenceTransformers (HuggingFace)
- **Frontend / UI:** Streamlit

---

## 📂 Project Structure

```text
model/
├── agents/             # The 'Brains': Specialized node logic
│   ├── planner.py
│   ├── query_rewriter.py
│   ├── research_agent.py
│   ├── summarizer.py
│   ├── critic_agent.py
│   └── refiner.py
├── config/             # Settings and Env management
│   └── settings.py
├── core/               # Graph orchestration and State management
│   ├── graph.py
│   └── state.py
├── retrieval/          # Scraping, embedding, and vector storage
│   ├── web_search.py
│   └── embeddings.py
├── .env                # Secret keys
├── README.md           # Documentation
├── requirements.txt    # Python dependencies
└── app.py              # Streamlit Entry Point
```

---

## 🚀 Installation & Setup

Follow these steps to deploy the AI Research Agent locally.

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd model
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys
Create a `.env` file in the root directory (or use the Streamlit sidebar at runtime):
```env
GROQ_API_KEY="your_groq_api_key_here"
TAVILY_API_KEY="your_tavily_api_key_here"
```
*(Note: You can get a free Groq key at [console.groq.com](https://console.groq.com) and a free Tavily key at [tavily.com](https://tavily.com))*

### 5. Run the Application
```bash
streamlit run app.py
```

Open the provided `localhost` URL in your browser, enter your API keys (if not set in `.env`), and formulate a complex question to start the automated research!
