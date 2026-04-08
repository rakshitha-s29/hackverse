import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def test_connection():
    api_key = os.getenv("GROQ_API_KEY")
    base_url = os.getenv("GROQ_BASE_URL")
    model = os.getenv("GROQ_MODEL")
    
    print(f"Testing Groq Connection...")
    print(f"Model: {model}")
    print(f"Base URL: {base_url}")
    
    try:
        llm = ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            model=model
        )
        response = llm.invoke("Hello, are you running on Groq with Llama?")
        print("\nSuccess! Response from LLM:")
        print(response.content)
    except Exception as e:
        print(f"\nFailed! Error: {e}")

if __name__ == "__main__":
    test_connection()
