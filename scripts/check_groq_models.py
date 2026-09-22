import os
import requests

def get_groq_models():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY environment variable not set.")
        return

    url = "https://api.groq.com/openai/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print("✅ Successfully connected to Groq API!\n")
        print("Available Models:")
        print("-" * 50)
        
        for model in data.get("data", []):
            model_id = model.get("id")
            # Highlight recommended Llama models
            if "llama" in model_id.lower():
                print(f"⭐ {model_id}")
            else:
                print(f"   {model_id}")
                
    except Exception as e:
        print(f"Failed to fetch models: {e}")

if __name__ == "__main__":
    get_groq_models()
