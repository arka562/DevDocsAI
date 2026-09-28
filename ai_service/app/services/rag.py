from app.services.embeddings import get_embedding
from app.services.vector_store import vector_store
from app.services.llm import generate_answer

def run_rag_pipeline(question: str, history: list[dict] = None) -> dict:
    """
    Executes the RAG pipeline:
    1. Embeds question
    2. Retrieves top K chunks from FAISS
    3. Builds prompt context (with history)
    4. Generates answer using LLM
    """
    if history is None:
        history = []
        
    # 1. Embed the user's question
    question_embedding = get_embedding(question)
    
    # 2. Retrieve relevant chunks (Top 5)
    results = vector_store.search(question_embedding, top_k=5)
    
    if not results:
        return {
            "answer": "No relevant documentation found. Please upload some documents first.",
            "sources": []
        }
        
    # Extract just the text for the LLM context
    context_chunks = [res["text"] for res in results]
    
    # Extract unique sources for the citations
    sources = []
    seen = set()
    for res in results:
        source_name = res["source"]
        if source_name not in seen:
            sources.append({"documentName": source_name})
            seen.add(source_name)
            
    # 3 & 4. Generate answer via LLM
    answer = generate_answer(question, context_chunks, history)
    
    return {
        "answer": answer,
        "sources": sources
    }
