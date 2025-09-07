from strands import tool
from langchain_chroma import Chroma
from langchain_aws import BedrockEmbeddings
import os
import sys
from ....config.settings import settings

def _get_embedding_function():
    """Get the embedding function using settings configuration."""
    model_id = settings.EMBED_MODEL_ID or "amazon.titan-embed-text-v2:0"
    region = settings.AWS_REGION or "us-east-1"
    return BedrockEmbeddings(model_id=model_id, region_name=region)

def _get_vectorstore():
    """Get the vector store with proper path configuration."""
    # Use the same path logic as pdf_vdb.py for consistency
    if settings.CHROMA_DOC_DB_PATH:
        if os.path.isabs(settings.CHROMA_DOC_DB_PATH):
            persist_dir = settings.CHROMA_DOC_DB_PATH
        else:
            # Convert relative path to absolute from backend directory
            current_file_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file_dir))))
            persist_dir = os.path.abspath(os.path.join(backend_dir, settings.CHROMA_DOC_DB_PATH))
    else:
        # Default fallback
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file_dir))))
        persist_dir = os.path.join(backend_dir, "src", "database", "vector_db", "knowledge_base")
    
    return Chroma(
        collection_name="knowledge_base",
        embedding_function=_get_embedding_function(),
        persist_directory=persist_dir
    )

@tool
def knowledge_base_search(query: str) -> str:
    """
    Searches the knowledge base for relevant information.

    Args:
        query: The search query.

    Returns:
        A string containing the search results.
    """
    try:
        vectorstore = _get_vectorstore()
        retriever = vectorstore.as_retriever(
            search_type="mmr", 
            search_kwargs={"k": 3, "fetch_k": 20, "lambda_mult": 0.25}
        )
        
        docs = retriever.invoke(query)
        if not docs:
            return "No relevant documents found."
        
        # Return a concise textual summary
        lines = []
        for i, d in enumerate(docs, 1):
            snippet = d.page_content.strip().replace('\n', ' ')
            if len(snippet) > 300:
                snippet = snippet[:297] + '...'
            meta = d.metadata or {}
            lines.append(f"{i}. {meta.get('original_filename') or meta.get('filename')} | pgs {meta.get('page_numbers')} | {snippet}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error searching knowledge base: {str(e)}"

def test_knowledge_base_search():
    """Test function for the knowledge base search."""
    print("Testing knowledge base search...")
    
    test_queries = [
        "What is Ewen education background",
        "What programming languages does Ewen know?",
        "What is Ewen work experience?"
    ]
    
    for query in test_queries:
        print(f"\n--- Query: {query} ---")
        result = knowledge_base_search(query)
        print(result)
        print("-" * 60)
    
    return "Test completed successfully"

def validate_vectorstore_connection():
    """Validate that the vectorstore is accessible and has data."""
    try:
        vectorstore = _get_vectorstore()
        # Try to get some documents to verify the store has data
        retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
        docs = retriever.invoke("test")
        if docs:
            print(f"✓ Vector store is accessible with {len(docs)} documents found")
            return True
        else:
            print("⚠ Vector store is accessible but no documents found")
            return False
    except Exception as e:
        print(f"✗ Vector store connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Knowledge Base Tools Test ===")
    
    # First validate connection
    print("\n1. Validating vector store connection...")
    validate_vectorstore_connection()
    
    # Then test search functionality
    print("\n2. Testing search functionality...")
    test_knowledge_base_search()