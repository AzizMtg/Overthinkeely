#!/usr/bin/env python3
"""
Example usage of the Worry Butler system.

This script shows how to use the Worry Butler programmatically
and demonstrates various features of the system.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from worry_butler import WorryButler

def example_basic_usage():
    """Demonstrate basic usage of the Worry Butler."""
    print("🔍 Example 1: Basic Usage")
    print("-" * 40)
    
    # Create a Worry Butler instance
    butler = WorryButler()
    
    # Process a simple worry
    worry = "I'm worried about my job interview tomorrow"
    print(f"🤔 User's worry: {worry}")
    
    print("\n🔄 Processing through agents...")
    result = butler.process_worry(worry)
    
    # Display results
    print(f"\n🎭 Overthinker Agent:")
    print(result['overthinker_response'])
    
    print(f"\n🧘‍♀️ Therapist Agent:")
    print(result['therapy_response'])
    
    print(f"\n📋 Executive Summary:")
    print(f"💡 {result['executive_summary']}")
    
    print(f"\n📊 Metadata: {result['metadata']}")
    
    return result

def example_json_output():
    """Demonstrate JSON output functionality."""
    print("\n\n🔍 Example 2: JSON Output")
    print("-" * 40)
    
    butler = WorryButler()
    worry = "I'm anxious about my upcoming presentation"
    
    print(f"🤔 User's worry: {worry}")
    
    # Get JSON output
    json_result = butler.process_worry_json(worry)
    print(f"\n📄 JSON Output:")
    print(json_result)

def example_agent_info():
    """Demonstrate getting agent information."""
    print("\n\n🔍 Example 3: Agent Information")
    print("-" * 40)
    
    butler = WorryButler()
    agent_info = butler.get_agent_info()
    
    for i, agent in enumerate(agent_info, 1):
        print(f"\n🤖 Agent {i}: {agent['name']}")
        print(f"   Description: {agent['description']}")
        print(f"   Model: {agent['model']}")
        print(f"   Temperature: {agent['temperature']}")

def example_multiple_worries():
    """Demonstrate processing multiple worries."""
    print("\n\n🔍 Example 4: Multiple Worries")
    print("-" * 40)
    
    butler = WorryButler()
    
    worries = [
        "I'm worried about my relationship",
        "I'm anxious about my finances",
        "I'm stressed about my health"
    ]
    
    for i, worry in enumerate(worries, 1):
        print(f"\n🤔 Worry {i}: {worry}")
        print("🔄 Processing...")
        
        try:
            result = butler.process_worry(worry)
            print(f"💡 Executive Summary: {result['executive_summary']}")
        except Exception as e:
            print(f"❌ Error: {e}")

def example_error_handling():
    """Demonstrate error handling."""
    print("\n\n🔍 Example 5: Error Handling")
    print("-" * 40)
    
    # Test with empty worry
    try:
        butler = WorryButler()
        result = butler.process_worry("")
        print("✅ Empty worry processed successfully")
    except Exception as e:
        print(f"❌ Error with empty worry: {e}")
    
    # Test with very long worry
    try:
        long_worry = "I'm worried about " + "everything " * 100
        result = butler.process_worry(long_worry)
        print("✅ Long worry processed successfully")
    except Exception as e:
        print(f"❌ Error with long worry: {e}")

def main():
    """Run all examples."""
    print("🤖 Worry Butler - Example Usage")
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
        # Run examples
        example_basic_usage()
        example_json_output()
        example_agent_info()
        example_multiple_worries()
        example_error_handling()
        
        print("\n" + "=" * 50)
        print("🎉 All examples completed successfully!")
        print("\n💡 Key Takeaways:")
        print("   • The system processes worries through 3 specialized agents")
        print("   • Each agent has a distinct personality and expertise")
        print("   • Results are returned in structured format")
        print("   • The system is designed to be easily extensible")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main()
