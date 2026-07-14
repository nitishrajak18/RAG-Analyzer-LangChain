import os
import warnings
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader, TextLoader
try:
    from langchain_community.document_loaders import UnstructuredPDFLoader  # better table extraction
except ImportError:
    UnstructuredPDFLoader = None
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI

warnings.filterwarnings("ignore")
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Loads variables from a local .env file (see .env.example) so you never
# have to hardcode your API key in the code.
load_dotenv()

# ==========================================
# CONFIG VARIABLES — change these as needed
# ==========================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
MAX_FILES = 5
CHUNK_SIZE = 500
CHUNK_OVERLAP = 200
RETRIEVAL_K = 5


class MultiDocRAGBot:
    def __init__(self):
        # Local embeddings (no API needed) to convert text into vectors
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.vector_store = None

        if not GROQ_API_KEY:
            print("⚠️ WARNING: GROQ_API_KEY not found. Add it to your .env file.")

        # Groq exposes an OpenAI-compatible endpoint, so ChatOpenAI works as-is
        self.llm = ChatOpenAI(
            api_key=GROQ_API_KEY or "dummy-key",
            base_url=GROQ_BASE_URL,
            model=GROQ_MODEL,
            temperature=0.1,
        )

    def process_files(self, file_paths):
        """file_paths: list of local file paths (already saved to disk)."""
        if not file_paths:
            return "⚠️ Status: No file uploaded."
        if len(file_paths) > MAX_FILES:
            return f"⚠️ Status: Error. Max {MAX_FILES} files allowed."

        try:
            all_documents = []
            for index, path in enumerate(file_paths, start=1):
                try:
                    if UnstructuredPDFLoader and path.lower().endswith(".pdf"):
                        loader = UnstructuredPDFLoader(path)
                    elif path.lower().endswith(".pdf"):
                        loader = PyPDFLoader(path)
                    else:
                        loader = TextLoader(path)
                    docs = loader.load()
                except Exception:
                    # Fallback to PyPDF if Unstructured fails
                    loader = PyPDFLoader(path)
                    docs = loader.load()

                for doc in docs:
                    doc.metadata["source_id"] = f"PDF #{index}"
                all_documents.extend(docs)

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
            )
            texts = text_splitter.split_documents(all_documents)

            self.vector_store = FAISS.from_documents(texts, self.embeddings)
            return f"✅ Index Ready: {len(file_paths)} files, {len(texts)} chunks."
        except Exception as e:
            return f"❌ System Error: {str(e)}"

    def ask(self, message):
        """Returns (reply_text, context_preview_text, docs_and_scores_or_None)."""
        if not self.vector_store:
            return "⚠️ Please upload and process documents first.", "", None

        try:
            docs_and_scores = self.vector_store.similarity_search_with_score(
                message, k=RETRIEVAL_K
            )
            docs = [doc for doc, score in docs_and_scores]

            context_text_for_llm = ""
            context_preview = ""
            for i, doc in enumerate(docs):
                source = doc.metadata.get("source_id", "Unknown")
                context_preview += f"--- CHUNK {i+1} [{source}] ---\n{doc.page_content[:200]}...\n\n"
                context_text_for_llm += f"Source: {source}\nContent: {doc.page_content}\n\n"

            system_msg = """You are a helpful AI analyst. Keep responses concise and direct—answer the question only, no extra speculation or summaries.

            The Context below was retrieved from uploaded documents. Read it carefully — if it answers the question, even partially, answer directly using it and cite the source naturally where it adds value (e.g., "According to PDF #1...").
            Do not force citations after every sentence.

            Only if the Context truly does not contain anything relevant to the question, answer from general knowledge instead and clearly note: "This is based on general knowledge, not found in the uploaded documents." Do not default to general knowledge just because the match feels imperfect — prefer the provided Context whenever it's on-topic.

            Context:"""
            user_prompt = f"{context_text_for_llm}\n\nQuestion: {message}"
            messages = [("system", system_msg), ("user", user_prompt)]
            response = self.llm.invoke(messages)
            return response.content, context_preview, docs_and_scores
        except Exception as e:
            return f"❌ Error: {str(e)}", "", None
