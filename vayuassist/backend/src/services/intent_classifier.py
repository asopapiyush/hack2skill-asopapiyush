class IntentClassifier:
    def classify(self, message: str) -> str:
        msg = message.lower()
        
        if any(w in msg for w in ["help", "drowning", "fire", "emergency", "stuck", "attack"]):
            return "emergency"
            
        if any(w in msg for w in ["travel", "drive", "route", "safe to go", "road"]):
            return "travel_advisory"
            
        if any(w in msg for w in ["stock", "prepare", "kit", "buy", "before monsoon"]):
            return "preparedness"
            
        if any(w in msg for w in ["clean", "insurance", "after flood", "dry"]):
            return "recovery"
            
        return "faq"
