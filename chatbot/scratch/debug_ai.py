import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

try:
    response = model.generate_content("Hello, this is a test. Respond with 'API_OK'")
    print("Response:", response.text)
except Exception as e:
    print("Error:", e)
