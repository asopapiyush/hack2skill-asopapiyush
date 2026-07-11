import os
from typing import Dict, Any
from openai import OpenAI
from src.services.guardrail_engine import GuardrailEngine
from src.services.intent_classifier import IntentClassifier

# Initialize OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatService:
    def __init__(self):
        self.guardrails = GuardrailEngine()
        self.classifier = IntentClassifier()
        
    async def handle_message(
        self, 
        user_id: str, 
        message: str, 
        user_context: dict = None
    ) -> Dict[str, Any]:
        """
        Handle chat message with real OpenAI integration
        user_context: {family_size, location, region, health_conditions}
        """
        
        if user_context is None:
            user_context = {}
        
        # 1. Check guardrails (emergency keywords)
        safety_check = self.guardrails.check_query(message)
        if safety_check["safety"] == "escalated":
            return {
                "response": safety_check["response"],
                "intent": "emergency",
                "escalation": True,
                "user_id": user_id
            }
        
        # 2. Classify intent
        intent = self.classifier.classify(message)
        
        # 3. Build LLM prompt with context
        system_prompt = self._build_system_prompt(user_context)
        user_prompt = self._build_user_prompt(message, intent, user_context)
        
        try:
            # 4. Call OpenAI
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500,
                timeout=10
            )
            
            llm_response = response.choices[0].message.content
            
        except Exception as e:
            print(f"OpenAI error: {e}")
            # Fallback if OpenAI fails
            llm_response = self._get_fallback_response(intent, user_context)
        
        # 5. Validate response with guardrails
        resp_check = self.guardrails.check_response(llm_response)
        if resp_check["safety"] == "fallback":
            llm_response = resp_check["response"]
        
        return {
            "response": llm_response,
            "intent": intent,
            "escalation": False,
            "user_id": user_id
        }
    
    def _build_system_prompt(self, user_context: dict) -> str:
        """Build system prompt with user context"""
        location = user_context.get("location") or "unknown"
        region = user_context.get("region") or "India"
        
        return f"""You are VayuAssist, a monsoon preparedness assistant for India.
        
User Location: {location}, {region}
User Family Size: {user_context.get('family_size', 'unknown')}
Health Conditions: {user_context.get('health_conditions', 'none')}

Your role:
1. Provide personalized monsoon preparedness advice
2. Give emergency guidance for disaster situations
3. Help create actionable safety plans
4. Be concise, clear, and safety-focused
5. Always prioritize life safety over property

When giving advice:
- Be specific to the user's family situation
- Include local emergency numbers when relevant
- Provide step-by-step instructions
- Ask follow-up questions if needed for clarification

Format responses clearly with:
- Main advice
- Action items
- Emergency contacts if needed"""
    
    def _build_user_prompt(self, message: str, intent: str, context: dict) -> str:
        """Build user prompt with context"""
        
        context_str = ""
        if context.get('family_size'):
            context_str += f"Family size: {context['family_size']} people\n"
        if context.get('health_conditions'):
            context_str += f"Health considerations: {context['health_conditions']}\n"
        if context.get('location'):
            context_str += f"Living in: {context['location']}\n"
        
        return f"""User Query: {message}

Intent: {intent}
{context_str}

Please provide personalized, actionable advice for this monsoon preparedness question."""
    
    def _get_fallback_response(self, intent: str, context: dict) -> str:
        """Fallback response if OpenAI fails"""
        
        if intent == "emergency":
            return """🚨 EMERGENCY DETECTED
For immediate help, call:
- Fire/Rescue: 101
- Ambulance: 102
- Police: 100
- Disaster Management: 1070

Stay safe and wait for professional help."""
        
        elif intent == "preparedness":
            family_size = context.get("family_size", "your household")
            return f"""For monsoon preparedness ({family_size}):
1. Stock at least 2 weeks of drinking water
2. Keep important documents in waterproof bags
3. Have a first aid kit and medications ready
4. Install emergency contact numbers
5. Identify safe evacuation routes

Would you like details on any of these?"""
        
        else:
            return """I can help with:
- Creating personalized preparedness plans
- Emergency response guidance
- Safety tips for your family
- Recovery instructions after flooding

What would you like to know?"""
