import os

# Set dummy environment variables to prevent import-time crashes during test collection
os.environ["TAVILY_API_KEY"] = "dummy_tavily_api_key"
os.environ["GROQ_API_KEY"] = "dummy_groq_api_key"
