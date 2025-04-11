import re
import random
from verification import verify_health_info

# Simple rule-based chatbot for health information verification
# In a real app, this would use more sophisticated NLP models

# Greeting messages
GREETINGS = [
    "Hello! I'm your health information assistant. How can I help you today?",
    "Hi there! I can help verify health information or connect you with a doctor. What would you like to do?",
    "Welcome to HealthVerify. I'm here to help you find accurate health information. What can I assist with?"
]

# Responses for verified information
VERIFIED_RELIABLE = [
    "This information appears to be from a reliable source. Is there anything specific you'd like to know about it?",
    "I've verified this information, and it comes from a trusted health source. How else can I help?",
    "Good news! This content is from a credible health authority. Do you have any questions about it?"
]

VERIFIED_UNRELIABLE = [
    "This information may contain misleading claims. Would you like me to explain why?",
    "I've found some concerning phrases in this content that are common in health misinformation. Should we discuss alternatives?",
    "This doesn't seem to come from a reliable health source. Would you like me to suggest trusted resources instead?"
]

VERIFIED_UNCERTAIN = [
    "I don't have enough information to fully verify this content. Can you provide more details or the original source?",
    "This is in a grey area - I can't definitively say if it's reliable or not. Would you like me to connect you with a healthcare professional?",
    "I'm not certain about the reliability of this information. Would you like me to suggest some trusted sources on this topic?"
]

# Follow-up questions
FOLLOW_UP_QUESTIONS = [
    "Are you experiencing any health issues related to this information?",
    "Would you like to speak with a healthcare professional about this topic?",
    "Would you like to see the latest verified news about this health topic?"
]

def get_chatbot_response(message):
    """Generate a response based on user message"""
    
    # Check for greetings
    if re.search(r'\b(hi|hello|hey|greetings)\b', message.lower()):
        return random.choice(GREETINGS)
    
    # Check for verification request
    if re.search(r'\b(verify|check|real|fake|true|false|fact|myth)\b', message.lower()) or "http" in message:
        # Call verification function
        verification_result = verify_health_info(message)
        
        if verification_result['verified']:
            if verification_result['is_reliable'] == True:
                response = random.choice(VERIFIED_RELIABLE) + "\n\n" + verification_result['message']
            elif verification_result['is_reliable'] == False:
                response = random.choice(VERIFIED_UNRELIABLE) + "\n\n" + verification_result['message']
            else:
                response = random.choice(VERIFIED_UNCERTAIN) + "\n\n" + verification_result['message']
                
            # Add details if available
            if verification_result['details']:
                response += "\n\nAdditional information:\n"
                for detail in verification_result['details']:
                    response += f"• {detail}\n"
                    
            # Add follow-up
            response += f"\n\n{random.choice(FOLLOW_UP_QUESTIONS)}"
            return response
        else:
            return "I couldn't verify that information. Could you please provide more details or a link to the source?"
    
    # Check for consultation request
    if re.search(r'\b(doctor|consult|appointment|book|medical help|professional|symptom)\b', message.lower()):
        return "I can help you book a consultation with a healthcare professional. Would you like to schedule an appointment now? You can visit our Doctor Consultation page."
    
    # Check for news request
    if re.search(r'\b(news|latest|update|recent)\b', message.lower()):
        return "Would you like to see the latest health news? You can visit our News section for verified health updates."
    
    # Default response
    return "I'm here to help verify health information, connect you with doctors, or show you the latest health news. What would you like to do?"
