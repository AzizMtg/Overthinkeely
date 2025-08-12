#!/usr/bin/env python3
"""
Main entry point for the Worry Butler system.

This script demonstrates how to use the Worry Butler to process worries
through the three-agent workflow.
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from worry_butler import WorryButler

def main():
    """
    Main function that demonstrates the Worry Butler system.
    """
    print("🤖 Welcome to Worry Butler! 🧠💭")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check configuration and determine provider
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if openai_key:
        print("🔑 OpenAI API key found")
        choice = input("Choose AI provider:\n1. Ollama (open-source, local) - RECOMMENDED\n2. OpenAI (cloud-based, requires API key)\nEnter choice (1 or 2): ").strip()
        
        if choice == "2":
            use_openai = True
            use_ollama = False
            print("🚀 Using OpenAI API")
        else:
            use_openai = False
            use_ollama = True
            print("🚀 Using Ollama (open-source models)")
    else:
        print("🔧 No OpenAI API key found - using Ollama (open-source models)")
        print("💡 To use OpenAI, add OPENAI_API_KEY to your .env file")
        use_openai = False
        use_ollama = True
    
    try:
        # Initialize the Worry Butler
        print("\n🚀 Initializing Worry Butler...")
        
        # Get Ollama configuration from environment
        ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        butler = WorryButler(
            use_grok=False, # Removed Grok API support
            use_openai=use_openai,
            use_ollama=use_ollama,
            ollama_model=ollama_model,
            ollama_base_url=ollama_base_url
        )
        
        # Show provider information
        provider_info = butler.get_provider_info()
        print(f"\n⚙️  Configuration:")
        print(f"  • Provider: {provider_info['provider']}")
        if provider_info['use_openai']:
            print(f"  • Model: OpenAI API")
        elif provider_info['use_ollama']:
            print(f"  • Model: {provider_info['ollama_model']}")
            print(f"  • Server: {provider_info['ollama_base_url']}")
            print("💡 Make sure Ollama is running: ollama serve")
        
        # Show agent information
        print("\n📋 Agent Information:")
        for agent_info in butler.get_agent_info():
            print(f"  • {agent_info['name']}: {agent_info['description']}")
            print(f"    Model: {agent_info['model']}")
            print(f"    Temperature: {agent_info['temperature']}")
        
        print("\n" + "=" * 50)
        print("💭 Ready to process your worries!")
        print("Type 'quit' to exit")
        print("=" * 50)
        
        # Interactive loop
        while True:
            try:
                # Get user input
                worry = input("\n🤔 What's worrying you today? ").strip()
                
                if worry.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye! Take care of yourself!")
                    break
                
                if not worry:
                    print("Please share what's worrying you.")
                    continue
                
                print("\n🔄 Processing your worry through the agents...")
                if use_ollama:
                    print("⏳ This may take a few moments with local models...")
                else:
                    print("⏳ This may take a few moments...")
                
                # Process the worry
                result = butler.process_worry(worry)
                
                # Display results
                print("\n" + "=" * 50)
                print("🎭 OVERTHINKER AGENT:")
                print(result['overthinker_response'])
                
                print("\n🧘‍♀️ THERAPIST AGENT:")
                print(result['therapist_response'])
                
                print("\n📋 EXECUTIVE SUMMARY:")
                print(f"💡 {result['executive_summary']}")
                
                print("\n" + "=" * 50)
                print("✨ Worry processing complete!")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Take care of yourself!")
                break
            except Exception as e:
                print(f"\n❌ Error processing worry: {e}")
                if use_ollama:
                    print("💡 Make sure Ollama is running: ollama serve")
                    print("💡 Check if your model is available: ollama list")
                print("Please try again or contact support if the problem persists.")
    
    except Exception as e:
        print(f"❌ Error initializing Worry Butler: {e}")
        if use_ollama:
            print("\n💡 For Ollama setup help:")
            print("   1. Install Ollama: https://ollama.ai")
            print("   2. Start Ollama: ollama serve")
            print("   3. Pull your model: ollama pull llama3.1:8b")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main()
