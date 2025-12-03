import requests
from app.config import get_settings

settings = get_settings()

class HuggingFaceService:
    def __init__(self):
        self.api_key = settings.HUGGINGFACE_API_KEY
        self.model = settings.HF_CHATBOT_MODEL
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    def chat(self, message: str, conversation_history: list = None) -> str:
        """Chat with IBM Granite model"""
        if conversation_history is None:
            conversation_history = []
        
        # Build conversation context
        context = ""
        for msg in conversation_history[-5:]:  # Last 5 messages
            role = msg.get("role", "user")
            content = msg.get("content", "")
            context += f"{role}: {content}\n"
        
        context += f"user: {message}\nassistant:"
        
        payload = {
            "inputs": context,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.7,
                "top_p": 0.9,
                "return_full_text": False
            }
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "").strip()
                return str(result)
            else:
                return f"I'm having trouble connecting right now. Please try again. (Status: {response.status_code})"
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"

huggingface_service = HuggingFaceService()
