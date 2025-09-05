# import requests
# from typing import List
# from langchain.embeddings.base import Embeddings

# from docling.chunking import HybridChunker
# from docling.document_converter import DocumentConverter
# from transformers import AutoTokenizer

# from langchain_chroma import Chroma
# from langchain.schema import Document

# from app.core.config import settings

# EMBED_API_BASE = settings.EMBED_API_BASE
# EMBED_MODEL = settings.EMBED_MODEL
# CHROMA_DOC_DB_PATH = settings.CHROMA_DOC_DB_PATH


# # --------------------------------------------------------------
# # VLLM Embedding Wrapper
# # --------------------------------------------------------------
# class VLLMEmbeddingFunction(Embeddings):
#     def __init__(self, base_url: str, model_name: str):
#         self.base_url = base_url
#         self.model_name = model_name

#     def embed_documents(self, texts: List[str]) -> List[List[float]]:
#         response = requests.post(
#             f"{self.base_url}/embeddings",
#             json={"model": self.model_name, "input": texts},
#         )
#         response.raise_for_status()
#         return [item["embedding"] for item in response.json()["data"]]

#     def embed_query(self, query: str) -> List[float]:
#         return self.embed_documents([query])[0]

#     def __call__(self, input: List[str]) -> List[List[float]]:
#         return self.embed_documents(input)

#     def name(self) -> str:
#         return f"vllm-{self.model_name}"


# def converter_md_to_vdb(file_path, tokenizer, vectorstore):

#     # --------------------------------------------------------------
#     # Convert and chunk
#     # --------------------------------------------------------------

#     converter = DocumentConverter()
#     print(f"Converting file: {file_path}")
#     result = converter.convert(file_path)

#     print("Document converted successfully.")

#     chunker = HybridChunker(
#         tokenizer=tokenizer,
#         max_tokens=MAX_TOKENS,
#         merge_peers=True,
#     )

#     chunk_iter = chunker.chunk(dl_doc=result.document)
#     chunks = list(chunk_iter)
#     print("Total chunks created:", len(chunks))

#     for c in chunks:
#         print(f"Chunk text: {c.text[:50]}...")

#     # --------------------------------------------------------------
#     # Prepare fields
#     # --------------------------------------------------------------
#     texts = [chunk.text for chunk in chunks]
#     metadatas = [
#         {
#             "filename": chunk.meta.origin.filename,
#             "page_numbers": ",".join(
#                 map(
#                     str,
#                     [
#                         page_no
#                         for page_no in sorted(
#                             set(
#                                 prov.page_no
#                                 for item in chunk.meta.doc_items
#                                 for prov in item.prov
#                             )
#                         )
#                     ],
#                 )
#             ),
#             "title": chunk.meta.headings[0] if chunk.meta.headings else None,
#         }
#         for chunk in chunks
#     ]

#     print("Prepared texts and metadata for ChromaDB.")

#     documents = [
#         Document(page_content=text, metadata=metadata)
#         for text, metadata in zip(texts, metadatas)
#     ]

#     print("Embeddings generated and stored in ChromaDB.")
#     print(f"Total documents to insert: {len(documents)}")
#     # --------------------------------------------------------------
#     # Add to Chroma
#     # --------------------------------------------------------------
#     vectorstore.add_documents(documents)

#     print("Documents added to ChromaDB successfully.")


# # --------------------------------------------------------------
# # Configuration
# # --------------------------------------------------------------
# tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL)
# MAX_TOKENS = 4095

# # --------------------------------------------------------------
# # Embedding
# # --------------------------------------------------------------
# embedding_function = VLLMEmbeddingFunction(
#     base_url=EMBED_API_BASE, model_name=EMBED_MODEL
# )


# # --------------------------------------------------------------
# # ChromaDB setup
# # --------------------------------------------------------------
# vectorstore = Chroma(
#     collection_name="knowledge_base",
#     embedding_function=embedding_function,
#     persist_directory=CHROMA_DOC_DB_PATH,
# )


# files = [
# ]

# for file in files:
#     print(f"Processing file: {file}")
#     path = f"data/guide_documents/{file}.pdf"
#     converter_md_to_vdb(path, tokenizer, vectorstore)
#     print(f"Finished processing file: {file}\n")


# files = [
# ]

# for file in files:
#     print(f"Processing file: {file}")
#     path = f"data/general_documents/{file}.pdf"
#     converter_md_to_vdb(path, tokenizer, vectorstore)
#     print(f"Finished processing file: {file}\n")
