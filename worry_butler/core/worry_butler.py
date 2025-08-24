#!/usr/bin/env python3
"""
Core Worry Butler system implementing a single-call multi-voice workflow.

This module uses a ConciergeAgent to produce, in one LLM call:
1. Overthinker (Prosecutor) - dramatic worst-case scenarios
2. Therapist (Defense) - CBT reframing and calming
3. Executive (Judge) - actionable, reassuring one-sentence summary
"""

from typing import Dict, Any, List
from worry_butler.agents.concierge_agent import ConciergeAgent


class WorryButler:
    """
    Main orchestrator for the three-agent worry processing system.
    
    Implements a sequential chain where each agent's output becomes
    the input for the next agent in the workflow.
    """
    
    def __init__(self, use_openai: bool = False, use_ollama: bool = True, ollama_model: str = None, ollama_base_url: str = None):
        """
        Initialize the Worry Butler with three specialized agents.
        
        Args:
            use_openai: Whether to use OpenAI API
            use_ollama: Whether to use Ollama (open-source) - default True
            ollama_model: Model name for Ollama (e.g., 'llama3.1:8b')
            ollama_base_url: Base URL for Ollama server
        """
        # Determine the actual provider to use
        if use_openai:
            provider = "openai"
        else:
            provider = "ollama"
        
        # Initialize the single concierge agent with the determined provider
        self.concierge = ConciergeAgent(
            provider=provider,
            ollama_model=ollama_model,
            ollama_base_url=ollama_base_url
        )
        
        # Store provider information
        self.use_openai = use_openai
        self.use_ollama = use_ollama
        self.provider = provider
        self.ollama_model = ollama_model
        self.ollama_base_url = ollama_base_url
    
    def process_worry(self, user_worry: str) -> Dict[str, Any]:
        """
        Process a user's worry through the three-agent chain.
        
        This is the main function that performs a single LLM call via ConciergeAgent
        and returns all three role outputs.
        
        Args:
            user_worry: The user's original worry statement
            
        Returns:
            Dictionary containing the complete conversation:
            - original_worry: User's input
            - overthinker_response: Dramatic worst-case scenario (from concierge)
            - therapist_response: CBT reframing and calming response (from concierge)
            - executive_summary: Actionable, reassuring summary (from concierge)
            - metadata: Processing information
            
        Raises:
            Exception: If any agent fails to process the input
        """
        try:
            # Single call to ConciergeAgent to get all three role outputs
            print("🛎️ Concierge Agent processing (single-call)...")
            bundle = self.concierge.generate_all(user_worry)

            # Map to legacy keys expected by API/frontend
            overthinker_response = bundle.get("overthinker", "")
            therapist_response = bundle.get("therapist", "")
            executive_summary = bundle.get("executive", "")

            # Compile the complete conversation bundle
            result = {
                "original_worry": user_worry,
                "overthinker_response": overthinker_response,
                "therapist_response": therapist_response,
                "executive_summary": executive_summary,
                "metadata": {
                    "workflow_completed": True,
                    "agent_sequence": ["concierge"],
                    "processing_notes": "Single-call concierge completed successfully"
                }
            }
            
            print("✅ Worry processing complete!")
            return result
            
        except Exception as e:
            # Comprehensive error handling for the entire workflow
            error_msg = f"Error in worry processing workflow: {str(e)}"
            print(f"❌ {error_msg}")
            
            # Return partial results if available, with error information
            partial_result = {
                "original_worry": user_worry,
                "error": error_msg,
                "partial_results": {},
                "metadata": {
                    "workflow_completed": False,
                    "error_occurred": True,
                    "error_details": str(e)
                }
            }
            
            # Include any partial results that were generated before the error
            if 'bundle' in locals():
                partial_result["partial_results"].update(bundle)
            
            raise Exception(error_msg)
    
    def get_agent_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all three agents for debugging and monitoring.
        
        Returns:
            List of dictionaries containing agent information
        """
        return [
            self.concierge.get_agent_info(),
        ]
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the current AI provider configuration.
        
        Returns:
            Dictionary with provider details
        """
        return {
            "provider": self.provider,
            "use_openai": self.use_openai,
            "use_ollama": self.use_ollama,
            "ollama_model": self.ollama_model,
            "ollama_base_url": self.ollama_base_url
        }
    
    def test_agent_chain(self, test_worry: str = "I'm worried about my presentation tomorrow") -> Dict[str, Any]:
        """
        Test the entire agent chain with a sample worry.
        
        This is useful for debugging and ensuring all agents are working correctly.
        
        Args:
            test_worry: Sample worry to test the system with
            
        Returns:
            Complete test results from the three-agent chain
        """
        print("🧪 Testing agent chain with sample worry...")
        print(f"Test input: '{test_worry}'")
        print("-" * 50)
        
        try:
            result = self.process_worry(test_worry)
            print("✅ Agent chain test completed successfully!")
            return result
        except Exception as e:
            print(f"❌ Agent chain test failed: {e}")
            raise
