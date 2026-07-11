from typing import Dict, Any
from src.services.guardrail_engine import GuardrailEngine
from src.services.intent_classifier import IntentClassifier
from src.services.rag_service import RagService

class ChatService:
    def __init__(self):
        self.guardrails = GuardrailEngine()
        self.classifier = IntentClassifier()
        self.rag = RagService()
        
    async def handle_message(self, user_id: str, message: str, language: str = "en", is_voice: bool = False) -> Dict[str, Any]:
        # 1. Guardrail Check (Hard stops)
        safety_check = self.guardrails.check_query(message)
        if safety_check["safety"] == "escalated":
            return {
                "response": safety_check["response"],
                "intent": "emergency",
                "escalation_flag": True,
                "latency_ms": 0
            }
            
        # 2. Intent Classification
        intent = self.classifier.classify(message)
        
        # 3. RAG Retrieval
        docs = await self.rag.search(message)
        
        # 4. LLM Generation (Mocked for verification)
        context = "\n".join([d["text"] for d in docs]) if docs else "No specific documents found."
        
        if intent == "emergency":
            llm_response = f"Please contact local authorities. Info: {context}"
        elif intent == "preparedness":
            llm_response = f"Here is a preparedness tip: {context}"
        else:
            llm_response = f"I can help with that. {context}"
            
        # 5. Response Safety Check
        resp_check = self.guardrails.check_response(llm_response)
        if resp_check["safety"] == "fallback":
            llm_response = resp_check["response"]
            
        return {
            "response": llm_response,
            "intent": intent,
            "escalation_flag": False,
            "latency_ms": 100
        }
