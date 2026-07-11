import os
import logging
try:
    from pinecone import Pinecone
except ImportError:
    Pinecone = None

logger = logging.getLogger(__name__)

class RagService:
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = "vayuassist-rag"
        self.pc = None
        self.index = None
        
        if self.api_key and Pinecone:
            try:
                self.pc = Pinecone(api_key=self.api_key)
                self.index = self.pc.Index(self.index_name)
            except Exception as e:
                logger.error(f"Failed to initialize Pinecone: {e}")
                
    async def search(self, query: str, top_k: int = 5, filters: dict = None) -> list:
        if not self.index:
            if "water entering" in query.lower() or "flood" in query.lower():
                return [{"text": "If water enters your house, turn off main electrical switches and move to higher ground.", "metadata": {"source": "IMD"}}]
            elif "fever" in query.lower():
                return [{"text": "Boil water before drinking to prevent waterborne diseases during monsoons.", "metadata": {"source": "Health"}}]
            return []
            
        return []
