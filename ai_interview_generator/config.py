import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the parent directory
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

# API Keys
# Best Practice: Always load sensitive keys from Environment Variables in production
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# We can define the models to use here
# Gemini 1.5 Pro or Flash can generate structured JSON reliably
GEMINI_MODEL_NAME = "gemini-1.5-flash"

# Llama 3 70B on Groq backend provides great reasoning and speed for fallback
GROQ_MODEL_NAME = "llama3-70b-8192"
