#!/usr/bin/env python3
"""
Core Worry Butler system implementing a chained multi-agent workflow.

This module orchestrates three specialized AI agents that work in sequence:
1. Overthinker Agent - generates dramatic worst-case scenarios
2. Therapist Agent - applies CBT techniques to reframe and calm
3. Executive Agent - creates actionable, reassuring summaries
"""

from typing import Dict, Any, List
from worry_butler.agents.overthinker_agent import OverthinkerAgent
from worry_butler.agents.therapist_agent import TherapistAgent
from worry_butler.agents.executive_agent import ExecutiveAgent


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
        
        # Initialize the three agents with the determined provider
        self.overthinker = OverthinkerAgent(
            provider=provider,
            ollama_model=ollama_model,
            ollama_base_url=ollama_base_url
        )
        
        self.therapist = TherapistAgent(
            provider=provider,
            ollama_model=ollama_model,
            ollama_base_url=ollama_base_url
        )
        
        self.executive = ExecutiveAgent(
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
        
        This is the main function that implements the sequential workflow:
        1. Overthinker receives user input → generates dramatic scenario
        2. Therapist receives Overthinker output → applies CBT techniques
        3. Executive receives Therapist output → creates actionable summary
        
        Args:
            user_worry: The user's original worry statement
            
        Returns:
            Dictionary containing the complete conversation chain:
            - original_worry: User's input
            - overthinker_response: Dramatic worst-case scenario
            - therapist_response: CBT reframing and calming response
            - executive_summary: Actionable, reassuring summary
            - metadata: Processing information and timestamps
            
        Raises:
            Exception: If any agent fails to process the input
        """
        try:
            # Step 1: Overthinker Agent - Generate dramatic worst-case scenario
            print("🎭 Overthinker Agent processing...")
            overthinker_response = self.overthinker.process_worry(user_worry)
            
            # Step 2: Therapist Agent - Apply CBT techniques to Overthinker's output
            print("🧘‍♀️ Therapist Agent processing...")
            therapist_response = self.therapist.process_overthinking(
                user_worry, overthinker_response
            )
            
            # Step 3: Executive Agent - Create actionable summary from Therapist's output
            print("📋 Executive Agent processing...")
            executive_summary = self.executive.create_summary(
                user_worry, overthinker_response, therapist_response
            )
            
            # Compile the complete conversation chain
            result = {
                "original_worry": user_worry,
                "overthinker_response": overthinker_response,
                "therapist_response": therapist_response,
                "executive_summary": executive_summary,
                "metadata": {
                    "workflow_completed": True,
                    "agent_sequence": ["overthinker", "therapist", "executive"],
                    "processing_notes": "Three-agent chain completed successfully"
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
            if 'overthinker_response' in locals():
                partial_result["partial_results"]["overthinker_response"] = overthinker_response
            if 'therapist_response' in locals():
                partial_result["partial_results"]["therapist_response"] = therapist_response
            if 'executive_summary' in locals():
                partial_result["partial_results"]["executive_summary"] = executive_summary
            
            raise Exception(error_msg)
    
    def get_agent_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all three agents for debugging and monitoring.
        
        Returns:
            List of dictionaries containing agent information
        """
        return [
            self.overthinker.get_agent_info(),
            self.therapist.get_agent_info(),
            self.executive.get_agent_info()
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
