"""
List all available models from Google GenAI API
to find correct model names and their supported capabilities.
"""
import os
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize client
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in environment variables")
    exit(1)

client = genai.Client(api_key=api_key)

print("=" * 80)
print("AVAILABLE MODELS IN GOOGLE GENAI API")
print("=" * 80)
print()

# List all models
try:
    models = client.models.list()
    
    gemini_models = []
    for model in models:
        # Filter for Gemini models
        if 'gemini' in model.name.lower():
            gemini_models.append(model)
    
    # Sort by name
    gemini_models.sort(key=lambda m: m.name)
    
    print(f"Found {len(gemini_models)} Gemini models:\n")
    
    for model in gemini_models:
        print(f"Model: {model.name}")
        
        # Check supported methods
        if hasattr(model, 'supported_generation_methods'):
            methods = model.supported_generation_methods
            print(f"  Supported methods: {', '.join(methods)}")
        
        # Check if it supports generateContent
        supports_generate = False
        if hasattr(model, 'supported_generation_methods'):
            supports_generate = 'generateContent' in model.supported_generation_methods
        
        print(f"  Supports generateContent: {'YES' if supports_generate else 'NO'}")
        
        # Display name
        if hasattr(model, 'display_name'):
            print(f"  Display Name: {model.display_name}")
        
        # Description
        if hasattr(model, 'description'):
            desc = model.description[:100] + "..." if len(model.description) > 100 else model.description
            print(f"  Description: {desc}")
        
        print()
    
    # Filter for models that support generateContent
    print("=" * 80)
    print("MODELS SUPPORTING generateContent (usable for chat):")
    print("=" * 80)
    print()
    
    for model in gemini_models:
        if hasattr(model, 'supported_generation_methods') and 'generateContent' in model.supported_generation_methods:
            print(f"  • {model.name}")
    
    print()
    
except Exception as e:
    print(f"Error listing models: {e}")
    import traceback
    traceback.print_exc()
