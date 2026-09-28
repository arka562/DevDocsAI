import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Use Gemini 1.5 Flash (or equivalent)
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_answer(question: str, context: list[str], history: list[dict] = None) -> str:
    """
    Generates an answer based ONLY on the provided context using Gemini, factoring in chat history.
    """
    if not API_KEY:
        return "Error: LLM_API_KEY is not set in the environment variables."

    if history is None:
        history = []

    formatted_context = "\n\n---\n\n".join(context)
    
    # Build conversation history string
    history_str = ""
    if history:
        history_str = "Conversation History:\n"
        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_str += f"{role}: {msg['content']}\n"
        history_str += "\n"
    
    prompt = f"""You are DevDocs AI, a developer documentation assistant.

Answer the user's question using ONLY the provided documentation context.
Use the Conversation History to understand pronouns or follow-up references.

If the answer cannot be found in the context, clearly state that the documentation does not contain enough information.

Documentation Context:
{formatted_context}

{history_str}Current Question:
{question}

Provide:
1. Clear explanation
2. Example when appropriate
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating answer: {e}")
        return f"Sorry, I encountered an error while generating the response: {str(e)}"
