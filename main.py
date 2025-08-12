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
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please create a .env file with your OpenAI API key")
        print("See env_example.txt for the required format")
        return
    
    try:
        # Initialize the Worry Butler
        print("🚀 Initializing Worry Butler...")
        butler = WorryButler()
        
        # Show agent information
        print("\n📋 Agent Information:")
        for agent_info in butler.get_agent_info():
            print(f"  • {agent_info['name']}: {agent_info['description']}")
        
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
                print("⏳ This may take a few moments...")
                
                # Process the worry
                result = butler.process_worry(worry)
                
                # Display results
                print("\n" + "=" * 50)
                print("🎭 OVERTHINKER AGENT:")
                print(result['overthinker_response'])
                
                print("\n🧘‍♀️ THERAPIST AGENT:")
                print(result['therapy_response'])
                
                print("\n📋 EXECUTIVE SUMMARY:")
                print(f"💡 {result['executive_summary']}")
                
                print("\n" + "=" * 50)
                print("✨ Worry processing complete!")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Take care of yourself!")
                break
            except Exception as e:
                print(f"\n❌ Error processing worry: {e}")
                print("Please try again or contact support if the problem persists.")
    
    except Exception as e:
        print(f"❌ Error initializing Worry Butler: {e}")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main()
