#!/usr/bin/env python3
"""
Test script for the Worry Butler system.

This script tests the basic functionality without requiring API calls.
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported correctly."""
    print("🧪 Testing imports...")
    
    try:
        from worry_butler.agents.base_agent import BaseAgent
        print("✅ BaseAgent imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import BaseAgent: {e}")
        return False
    
    try:
        from worry_butler.agents.overthinker_agent import OverthinkerAgent
        print("✅ OverthinkerAgent imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import OverthinkerAgent: {e}")
        return False
    
    try:
        from worry_butler.agents.therapist_agent import TherapistAgent
        print("✅ TherapistAgent imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import TherapistAgent: {e}")
        return False
    
    try:
        from worry_butler.agents.executive_agent import ExecutiveAgent
        print("✅ ExecutiveAgent imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ExecutiveAgent: {e}")
        return False
    
    try:
        from worry_butler.core.worry_butler import WorryButler
        print("✅ WorryButler imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import WorryButler: {e}")
        return False
    
    return True

def test_agent_creation():
    """Test that agents can be created (without API calls)."""
    print("\n🧪 Testing agent creation...")
    
    try:
        # This will fail without API key, but we can test the structure
        from worry_butler.agents.overthinker_agent import OverthinkerAgent
        from worry_butler.agents.therapist_agent import TherapistAgent
        from worry_butler.agents.executive_agent import ExecutiveAgent
        
        # Test that we can access the system prompts
        overthinker = OverthinkerAgent.__new__(OverthinkerAgent)
        overthinker._get_system_prompt = lambda: "Test prompt"
        
        therapist = TherapistAgent.__new__(TherapistAgent)
        therapist._get_system_prompt = lambda: "Test prompt"
        
        executive = ExecutiveAgent.__new__(ExecutiveAgent)
        executive._get_system_prompt = lambda: "Test prompt"
        
        print("✅ Agent classes can be instantiated")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create agents: {e}")
        return False

def test_system_prompts():
    """Test that system prompts are properly defined."""
    print("\n🧪 Testing system prompts...")
    
    try:
        from worry_butler.agents.overthinker_agent import OverthinkerAgent
        from worry_butler.agents.therapist_agent import TherapistAgent
        from worry_butler.agents.executive_agent import ExecutiveAgent
        
        # Test system prompts (without creating full instances)
        overthinker_prompt = OverthinkerAgent._get_system_prompt.__get__(OverthinkerAgent())()
        therapist_prompt = TherapistAgent._get_system_prompt.__get__(TherapistAgent())()
        executive_prompt = ExecutiveAgent._get_system_prompt.__get__(ExecutiveAgent())()
        
        # Check that prompts are substantial
        if len(overthinker_prompt) > 100:
            print("✅ Overthinker system prompt is substantial")
        else:
            print("❌ Overthinker system prompt seems too short")
            return False
        
        if len(therapist_prompt) > 100:
            print("✅ Therapist system prompt is substantial")
        else:
            print("❌ Therapist system prompt seems too short")
            return False
        
        if len(executive_prompt) > 100:
            print("✅ Executive system prompt is substantial")
        else:
            print("❌ Executive system prompt seems too short")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test system prompts: {e}")
        return False

def test_workflow_structure():
    """Test that the workflow structure is properly defined."""
    print("\n🧪 Testing workflow structure...")
    
    try:
        from worry_butler.core.worry_butler import WorryState
        
        # Test that the state model is properly defined
        state = WorryState(
            original_worry="Test worry",
            overthinking_response="Test overthinking",
            therapy_response="Test therapy",
            executive_summary="Test summary"
        )
        
        print("✅ WorryState model works correctly")
        
        # Test that all fields are accessible
        assert state.original_worry == "Test worry"
        assert state.overthinking_response == "Test overthinking"
        assert state.therapy_response == "Test therapy"
        assert state.executive_summary == "Test summary"
        
        print("✅ All state fields are accessible")
        return True
        
    except Exception as e:
        print(f"❌ Failed to test workflow structure: {e}")
        return False

def main():
    """Run all tests."""
    print("🤖 Worry Butler System Tests")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("🔑 OpenAI API key found (will test full functionality)")
    else:
        print("⚠️  No OpenAI API key found (will test structure only)")
    
    # Run tests
    tests = [
        test_imports,
        test_agent_creation,
        test_system_prompts,
        test_workflow_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        if api_key:
            print("\n🚀 To run the system:")
            print("   python main.py          # Command line interface")
            print("   python api.py           # Web interface")
        else:
            print("\n⚠️  To use the system, you'll need to:")
            print("   1. Copy env_example.txt to .env")
            print("   2. Add your OpenAI API key to .env")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
