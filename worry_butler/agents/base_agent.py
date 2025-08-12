"""
Base agent class for the Worry Butler system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BaseAgent(ABC):
    """
    Base class for all agents in the Worry Butler system.
    
    This class provides common functionality like:
    - OpenAI API integration OR Ollama (open-source) integration
    - Message formatting
    - Response processing
    """
    
    def __init__(self, 
                 model_name: str = "gpt-4", 
                 temperature: float = 0.7,
                 provider: str = "ollama",
                 ollama_model: str = "llama3.1:8b",
                 ollama_base_url: str = "http://localhost:11434"):
        """
        Initialize the base agent.
        
        Args:
            model_name: The OpenAI model to use (if using OpenAI)
            temperature: Creativity level (0.0 = focused, 1.0 = creative)
            provider: AI provider to use ("openai" or "ollama")
            ollama_model: The Ollama model to use
            ollama_base_url: Ollama server URL
        """
        self.provider = provider
        self.temperature = temperature
        
        if provider == "openai":
            # Use OpenAI
            self._setup_openai(model_name)
        else:
            # Use Ollama (open-source)
            self._setup_ollama(ollama_model, ollama_base_url)
        
        # Agent-specific attributes
        self.name = self.__class__.__name__
        self.system_prompt = self._get_system_prompt()
    
    def _setup_openai(self, model_name: str):
        """Set up OpenAI integration."""
        try:
            from langchain_openai import ChatOpenAI
            
            # Get API key from environment
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            
            # Initialize the language model
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=self.temperature,
                api_key=api_key
            )
            
        except ImportError:
            raise ImportError("langchain-openai not installed. Run: pip install langchain-openai")
    
    def _setup_ollama(self, model_name: str, base_url: str):
        """Set up Ollama integration."""
        try:
            # Try different import paths for Ollama
            ollama_class = None
            
            # Method 1: Try ChatOllama (preferred for chat models)
            try:
                from langchain_ollama.chat_models import ChatOllama
                ollama_class = ChatOllama
                print(f"✅ Using ChatOllama from langchain_ollama.chat_models")
            except ImportError:
                pass
            
            # Method 2: Try OllamaLLM (fallback for text generation)
            if not ollama_class:
                try:
                    from langchain_ollama.llms import OllamaLLM
                    ollama_class = OllamaLLM
                    print(f"✅ Using OllamaLLM from langchain_ollama.llms")
                except ImportError:
                    pass
            
            # Method 3: Try legacy Ollama import (for older versions)
            if not ollama_class:
                try:
                    from langchain_ollama import Ollama
                    ollama_class = Ollama
                    print(f"✅ Using Ollama from langchain_ollama")
                except ImportError:
                    pass
            
            # Method 4: Try langchain_community as fallback
            if not ollama_class:
                try:
                    from langchain_community.llms import Ollama
                    ollama_class = Ollama
                    print(f"✅ Using Ollama from langchain_community.llms")
                except ImportError:
                    pass
            
            if not ollama_class:
                raise ImportError("Could not find Ollama class in any langchain package")
            
            # Initialize the model
            self.llm = ollama_class(
                model=model_name,
                base_url=base_url,
                temperature=self.temperature
            )
            
            print(f"✅ Ollama setup successful with {ollama_class.__name__}")
            
        except ImportError as e:
            print(f"❌ Import error: {e}")
            print("💡 Please install langchain-ollama: pip install langchain-ollama")
            print("💡 Or try: pip install --upgrade langchain-ollama")
            raise ImportError(f"langchain-ollama not properly installed: {e}")
        except Exception as e:
            print(f"❌ Error setting up Ollama: {e}")
            raise
    
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
            message: The message to process
            context: Optional context information
            
        Returns:
            The agent's response
        """
        try:
            print(f"🔧 Processing message with {self.provider} provider...")
            print(f"🔧 Message length: {len(message)} characters")
            
            if self.provider == "openai":
                return self._process_with_openai(message, context)
            else:
                return self._process_with_ollama(message, context)
                
        except Exception as e:
            print(f"❌ Error in process_message: {e}")
            print(f"❌ Provider: {self.provider}")
            print(f"❌ Message: {message[:100]}...")
            raise
    
    def _process_with_openai(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process message using OpenAI format."""
        from langchain.schema import HumanMessage, SystemMessage
        
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
    
    def _process_with_ollama(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Process a message using Ollama.
        
        Args:
            message: The message to process
            context: Optional context information
            
        Returns:
            The agent's response
        """
        try:
            print(f"🔧 Ollama: Processing message...")
            
            # Format the message for Ollama
            if context:
                formatted_message = f"Context: {context}\n\nMessage: {message}"
            else:
                formatted_message = message
            
            # Create the full prompt with system instructions
            full_prompt = f"{self.system_prompt}\n\n{formatted_message}"
            print(f"🔧 Ollama: Full prompt length: {len(full_prompt)} characters")
            
            # Get response from Ollama
            print(f"🔧 Ollama: Sending request...")
            response = self.llm.invoke(full_prompt)
            print(f"🔧 Ollama: Response received: {type(response)}")
            
            # Extract the response content - handle both AIMessage and string responses
            if hasattr(response, 'content'):
                result = response.content
                print(f"🔧 Ollama: Response content length: {len(result)} characters")
                return result
            elif hasattr(response, 'text'):
                result = response.text
                print(f"🔧 Ollama: Response text length: {len(result)} characters")
                return result
            else:
                result = str(response)
                print(f"🔧 Ollama: Response as string length: {len(result)} characters")
                return result
                
        except Exception as e:
            print(f"❌ Error processing message with Ollama: {e}")
            print(f"❌ Error type: {type(e)}")
            print(f"❌ Error details: {str(e)}")
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
    
    def _get_agent_description(self) -> str:
        """
        Return a brief description of this agent's role.
        
        Returns:
            A short description of the agent's purpose
        """
        return "AI agent specialized in processing and responding to user input"
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about this agent.
        
        Returns:
            Dictionary with agent information
        """
        if self.provider == "openai":
            model_info = "OpenAI"
            model_name = getattr(self.llm, 'model', 'Unknown')
        else:  # ollama
            model_info = "Ollama"
            model_name = getattr(self.llm, 'model', 'Unknown')
        
        return {
            "name": self.name,
            "description": self._get_agent_description(),
            "model": f"{model_info} - {model_name}",
            "temperature": self.temperature,
            "provider": self.provider
        }
