"""
Base agent class for the Worry Butler system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BaseAgent(ABC):
    """
    Base class for all agents in the Worry Butler system.
    
    This class provides common functionality like:
    - OpenAI API integration
    - Message formatting
    - Response processing
    """
    
    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.7):
        """
        Initialize the base agent.
        
        Args:
            model_name: The OpenAI model to use
            temperature: Creativity level (0.0 = focused, 1.0 = creative)
        """
        # Get API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Initialize the language model
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key
        )
        
        # Agent-specific attributes
        self.name = self.__class__.__name__
        self.system_prompt = self._get_system_prompt()
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """
        Return the system prompt for this agent.
        
        Returns:
            The system prompt string
        """
        pass
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Process a message using this agent's specialized knowledge.
        
        Args:
            message: The input message to process
            context: Optional context information from previous agents
            
        Returns:
            The agent's response
        """
        # Prepare messages for the LLM
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=message)
        ]
        
        # Add context if provided
        if context:
            context_message = f"Context from previous agents: {context}"
            messages.append(HumanMessage(content=context_message))
        
        # Get response from LLM
        response = self.llm.invoke(messages)
        
        return response.content
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about this agent.
        
        Returns:
            Dictionary with agent information
        """
        return {
            "name": self.name,
            "description": self._get_system_prompt()[:100] + "...",
            "model": self.llm.model_name,
            "temperature": self.llm.temperature
        }
