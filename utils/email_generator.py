from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_persuasive_email(name: str, interests: str, booking_link: str, itinerary_link: str) -> str:
    prompt = f"""
    Create a URGENTLY PERSUASIVE email for {name} who loves {interests}.
    Must include these exact elements in order:
    
    1. Personalized greeting with {name}
    2. Highlight their interest in {interests}
    3. Mention the attached itinerary PDF
    4. Reference the marketing poster attachment (call it "limited-time offer visual")
    5. Link to personalize itinerary: {itinerary_link}
    6. Booking link: {booking_link}
    7. Luxury tone with urgency
    
    Structure the email like this:
    
    Subject: [5-8 word enticing subject]
    
    Dear [Name],
    
    [Paragraph 1: Build excitement about their specific interests]
    
    [Paragraph 2: Describe what makes this offer unique]
    
    Don't miss:
    • Benefit 1 related to {interests}
    • Benefit 2 
    • Benefit 3
    
    [Call to action with urgency]
    
    Warm regards,
    [Signature]
    """
    
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-70b-8192",
        temperature=0.7
    )
    
    return response.choices[0].message.content