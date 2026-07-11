import json
import os
import re

class GuardrailEngine:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        
        filepath = os.path.join(data_dir, "hard_stop_responses.json")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                self.hard_stops = json.load(f)
        except Exception as e:
            self.hard_stops = {}
            
        self.patterns = {
            "drowning": re.compile(r'\b(drowning|drown|sinking)\b', re.IGNORECASE),
            "electrocution": re.compile(r'\b(electrocuted|electrocution|electric shock|shocked by wire)\b', re.IGNORECASE),
            "fire": re.compile(r'\b(fire|burning|flames)\b', re.IGNORECASE),
            "snake_bite": re.compile(r'\b(snake bite|bitten by snake)\b', re.IGNORECASE),
            "childbirth": re.compile(r'\b(childbirth|giving birth|labor pains)\b', re.IGNORECASE),
            "heart_attack": re.compile(r'\b(heart attack|chest pain|cardiac arrest)\b', re.IGNORECASE),
        }

    def check_query(self, query: str) -> dict:
        for category, pattern in self.patterns.items():
            if pattern.search(query):
                response = self.hard_stops.get(category, "EMERGENCY DETECTED. Call 112 immediately.")
                return {
                    "safety": "escalated",
                    "response": response,
                    "category": category
                }
        
        return {"safety": "safe"}
        
    def check_response(self, llm_response: str) -> dict:
        if not llm_response or not llm_response.strip():
            return {"safety": "fallback", "response": "I cannot provide an answer at this time. Please contact local authorities."}
            
        injection_patterns = [
            r"ignore previous instructions",
            r"system role is now",
            r"you are a helpful assistant that will now"
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, llm_response, re.IGNORECASE):
                return {"safety": "fallback", "response": "I cannot provide an answer to this query."}
                
        return {"safety": "safe"}
