import google.generativeai as genai
import os

key = "AIzaSyBFFdNvXdN5D92KHGIljf49fWmw_SKEfMU"
print(f"Testing API Key: {key[:10]}...")

try:
    genai.configure(api_key=key)
    
    # 1. List Models
    print("\n--- Available Models ---")
    try:
        models = [m.name for m in genai.list_models()]
        for m in models:
            print(m)
    except Exception as e:
        print(f"Listing failed: {e}")

    # 2. Test Generation
    print("\n--- Testing Generation ---")
    test_models = ["models/gemini-1.5-pro", "models/gemini-pro", "models/gemini-1.5-flash"]
    
    for model_name in test_models:
        try:
            print(f"Trying {model_name}...", end=" ")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello")
            print("Success!")
            break
        except Exception as e:
            print(f"Failed: {str(e)[:100]}...")

except Exception as e:
    print(f"Configuration failed: {e}")
