import os
import json
import httpx
from dotenv import load_dotenv
from sip.core.contracts.rag import Context

load_dotenv()

class LLMGenerator:
    """Generates the final response using Gemini."""
    
    async def generate(self, query: str, context: Context) -> str:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return (
                "**Error:** `GEMINI_API_KEY` is not set.\n\n"
                "Please create a `.env` file in the root directory containing `GEMINI_API_KEY=your_key`, "
                "or export it in your terminal, then restart the server.\n\n"
                "*(Here are the retrieved chunks we would have used)*:\n\n"
                + "\n\n".join([f"--- Evidence ---\n{item.knowledge_record.chunk.text}" for item in context.evidence_items[:3]])
            )
            
        # Format prompt
        context_texts = "\n\n".join([item.knowledge_record.chunk.text for item in context.evidence_items])
        prompt = f"Context information is below.\n---------------------\n{context_texts}\n---------------------\nGiven the context information and not prior knowledge, answer the query.\nQuery: {query}\nAnswer: "
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=30.0)
                
                if response.status_code == 200:
                    data = response.json()
                    try:
                        text = str(data["candidates"][0]["content"]["parts"][0]["text"])
                        return text
                    except (KeyError, IndexError):
                        return "Error parsing response from Gemini: " + json.dumps(data)
                else:
                    return f"Error from Gemini API ({response.status_code}): {response.text}"
        except Exception as e:
            return f"Error contacting Gemini API: {str(e)}"
