import os
import boto3
import shutil
import tempfile
from botocore.config import Config
from typing import List, Optional

from langchain_aws import BedrockEmbeddings
from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from transformers import AutoTokenizer
from langchain_chroma import Chroma
from langchain.schema import Document

from ...config.settings import settings
from ..models import SessionLocalConfig, KnowledgeBase

# --------------------------------------------------------------
# Configuration
# --------------------------------------------------------------

EMBED_MODEL_ID = settings.EMBED_MODEL_ID
TOKENIZER_MODEL_ID = settings.TOKENIZER_MODEL_ID

print(settings.CHROMA_DOC_DB_PATH)

# Ensure CHROMA_DOC_DB_PATH is absolute and writable
if settings.CHROMA_DOC_DB_PATH:
    if os.path.isabs(settings.CHROMA_DOC_DB_PATH):
        CHROMA_DOC_DB_PATH = settings.CHROMA_DOC_DB_PATH
    else:
        # Convert relative path to absolute from backend directory
        # This file is at backend/src/database/data_processing/pdf_vdb.py
        # So go up 4 levels to get to backend, then apply relative path
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file_dir)))
        CHROMA_DOC_DB_PATH = os.path.abspath(os.path.join(backend_dir, settings.CHROMA_DOC_DB_PATH))
else:
    # Default fallback
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file_dir)))
    CHROMA_DOC_DB_PATH = os.path.join(backend_dir, "src", "database", "vector_db", "knowledge_base")

print(f"Using CHROMA_DOC_DB_PATH: {CHROMA_DOC_DB_PATH}")
MAX_TOKENS = 4095

# --------------------------------------------------------------
# Embedding Function (Bedrock Best Practice)
# --------------------------------------------------------------

def get_bedrock_embedding_function() -> BedrockEmbeddings:
    """
    Creates and returns a BedrockEmbeddings client configured with a
    robust retry strategy, following AWS best practices.
    """
    retry_config = Config(
        retries={'max_attempts': 5, 'mode': 'standard'},
        connect_timeout=10,
        read_timeout=30
    )
    bedrock_runtime_client = boto3.client(
        service_name="bedrock-runtime",
        region_name=settings.AWS_REGION,
        config=retry_config
    )
    return BedrockEmbeddings(
        client=bedrock_runtime_client,
        model_id=EMBED_MODEL_ID
    )

# --------------------------------------------------------------
# PDF Processing Logic
# --------------------------------------------------------------

def _process_pdf_to_documents(
    file_path: str,
    tokenizer,
    extra_metadata: Optional[dict] = None
) -> List[Document]:
    """
    Converts a single PDF file into a list of LangChain Document objects,
    ready for embedding.
    """
    if not os.path.exists(file_path):
        print(f"File not found, skipping: {file_path}")
        return []

    converter = DocumentConverter()
    result = converter.convert(file_path)

    chunker = HybridChunker(
        tokenizer=tokenizer,
        max_tokens=MAX_TOKENS,
        merge_peers=True,
    )
    chunks = list(chunker.chunk(dl_doc=result.document))
    print(f"Total chunks created: {len(chunks)}")

    documents = []
    for chunk in chunks:
        page_numbers = sorted(
            set(prov.page_no for item in chunk.meta.doc_items for prov in item.prov)
        )
        metadata = {
            "filename": chunk.meta.origin.filename,
            "page_numbers": ",".join(map(str, page_numbers)),
            "title": chunk.meta.headings[0] if chunk.meta.headings else None,
        }
        if extra_metadata:
            metadata.update(extra_metadata)
        documents.append(Document(page_content=chunk.text, metadata=metadata))
    
    return documents

# --------------------------------------------------------------
# Main Vectorization Function
# --------------------------------------------------------------

def vectorise_knowledge_base_from_db(recreate: bool = True) -> List[str]:
    """
    Fetches all documents from the KnowledgeBase DB table, processes them,
    and embeds them into the Chroma vector store.

    Args:
        recreate: If True, deletes the existing vector store for a clean rebuild.

    Returns:
        A list of file names that were successfully processed.
    """
    print(f"Vector store directory: {CHROMA_DOC_DB_PATH}")
    
    # Ensure the directory exists and is writable
    os.makedirs(CHROMA_DOC_DB_PATH, exist_ok=True)
    
    # Check write permissions
    if not os.access(CHROMA_DOC_DB_PATH, os.W_OK):
        try:
            os.chmod(CHROMA_DOC_DB_PATH, 0o755)
        except Exception as e:
            print(f"Warning: Cannot set write permissions on {CHROMA_DOC_DB_PATH}: {e}")
    
    if recreate and os.path.isdir(CHROMA_DOC_DB_PATH):
        print(f"Removing existing vector store at {CHROMA_DOC_DB_PATH}...")
        try:
            shutil.rmtree(CHROMA_DOC_DB_PATH, ignore_errors=True)
            os.makedirs(CHROMA_DOC_DB_PATH, exist_ok=True)
        except Exception as e:
            print(f"Warning: Error recreating vector store directory: {e}")

    # Initialize resources
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_MODEL_ID)
    embedding_function = get_bedrock_embedding_function()
    
    # Initialize vector store with explicit settings for write access
    try:
        vectorstore = Chroma(
            collection_name="knowledge_base",
            embedding_function=embedding_function,
            persist_directory=CHROMA_DOC_DB_PATH,
        )
    except Exception as e:
        print(f"Error initializing Chroma vector store: {e}")
        print(f"Attempting to clear and recreate vector store...")
        shutil.rmtree(CHROMA_DOC_DB_PATH, ignore_errors=True)
        os.makedirs(CHROMA_DOC_DB_PATH, exist_ok=True)
        vectorstore = Chroma(
            collection_name="knowledge_base",
            embedding_function=embedding_function,
            persist_directory=CHROMA_DOC_DB_PATH,
        )

    db = SessionLocalConfig()
    processed_files = []
    try:
        records: List[KnowledgeBase] = db.query(KnowledgeBase).all()
        print(f"Found {len(records)} records in the knowledge base.")

        for rec in records:
            if not rec.file_content:
                print(f"Skipping {rec.file_name}: no binary content stored.")
                continue

            tmp_path = ""
            try:
                # Write blob to a temporary file for processing
                suffix = f".{rec.file_name.rsplit('.', 1)[1]}" if '.' in rec.file_name else ""
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(rec.file_content)
                    tmp_path = tmp.name
                
                print(f"--- Processing {rec.file_name} (ID: {rec.id}) ---")
                docs = _process_pdf_to_documents(
                    tmp_path,
                    tokenizer,
                    extra_metadata={
                        "kb_id": str(rec.id),
                        "original_filename": rec.file_name,
                        "description": rec.description,
                    },
                )

                if docs:
                    vectorstore.add_documents(docs)
                    print(f"Successfully added {len(docs)} document chunks to vector store.")
                    rec.study_status = 'studied'
                    processed_files.append(rec.file_name)
                else:
                    print("No documents were generated from this file.")

            except Exception as e:
                print(f"Failed to vectorise {rec.file_name}: {e}")
                rec.study_status = 'error'
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)
        
        print("Committing study status updates to the database...")
        db.commit()

    except Exception as e:
        print(f"An error occurred during the main vectorization loop: {e}")
        db.rollback()
    finally:
        db.close()

    print(f"\nVectorisation complete. Files processed: {len(processed_files)}")
    return processed_files


if __name__ == "__main__":
    vectorise_knowledge_base_from_db(recreate=True)
