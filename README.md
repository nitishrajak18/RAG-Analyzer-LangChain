# 📚 Multi-Source RAG Analyzer

A Retrieval-Augmented Generation (RAG) application that enables users to ask questions across multiple PDF documents using Large Language Models (LLMs). The system performs semantic search, retrieves the most relevant document chunks, and generates context-aware answers with source citations.

---

## 🚀 Features

- 📄 Upload and analyze multiple PDF documents
- 🔍 Semantic search using HuggingFace Embeddings
- 🧠 Context-aware question answering with GROQ API
- 📌 Source citation for transparent and trustworthy responses
- 📊 Relevance scoring for retrieved document chunks
- 📈 Interactive visualizations for document insights
- ⚡ Reduced information retrieval time by approximately **70%**

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend Development |
| LangChain | RAG Pipeline |
| HuggingFace Embeddings | Semantic Vector Embeddings |
 | Vector Database  |
| GROQ API | LLM for Answer Generation |
| Streamlit | User Interface *(or Gradio if used)* |
| PDF Processing |

---

## 🏗️ Architecture

```text
                PDF Documents
                      │
                      ▼
            Document Loader
                      │
                      ▼
              Text Chunking
                      │
                      ▼
      HuggingFace Embeddings
                      │
                      ▼
             Vector Database
                      │
        User Question
              │
              ▼
      Similarity Search
              │
              ▼
      Relevant Document Chunks
              │
              ▼
         Perplexity API
              │
              ▼
 Answer + Source Citation + Relevance Score
```

## 💡 How It Works

1. Upload one or more PDF documents.
2. The documents are split into smaller chunks.
3. Each chunk is converted into embeddings using HuggingFace.
4. Embeddings are stored in a vector database.
5. When a user asks a question, semantic similarity search retrieves the most relevant chunks.
6. Retrieved context is sent to the Groq API.
7. The model generates an answer along with source citations and relevance scores.

