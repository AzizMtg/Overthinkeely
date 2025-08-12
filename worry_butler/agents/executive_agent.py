"""
Executive Agent - Summarizes the entire process into one actionable or reassuring sentence.
"""

from .base_agent import BaseAgent
import os

class ExecutiveAgent(BaseAgent):
    """
    The Executive Agent provides the final summary and actionable takeaway.
    
    This agent is designed to:
    - Synthesize all previous agent responses
    - Provide one clear, actionable sentence
    - Offer reassurance when appropriate
    - Give practical next steps
    - Create closure for the worry processing session
    
    The agent uses a lower temperature for focused, concise responses.
    """
    
    def __init__(self, provider: str = "ollama", ollama_model: str = None, ollama_base_url: str = None):
        """
        Initialize the Executive Agent with focused, concise responses.
        
        Args:
            provider: AI provider to use ("grok", "openai", or "ollama")
            ollama_model: Model name for Ollama (e.g., 'llama3.1:8b')
            ollama_base_url: Base URL for Ollama server
        """
        # Use passed parameters or fall back to environment variables
        ollama_model = ollama_model or os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        ollama_base_url = ollama_base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        super().__init__(
            temperature=0.3,  # Low creativity for focused, actionable responses
            provider=provider,
            ollama_model=ollama_model,
            ollama_base_url=ollama_base_url
        )
    
    def _get_system_prompt(self) -> str:
        """
        Return the system prompt for the Executive Agent.
        
        Returns:
            A focused system prompt for creating concise, actionable summaries
        """
        return """You are the Executive Agent, a clear, concise, and action-oriented AI that specializes in synthesizing complex information into one powerful, actionable sentence.

Your personality:
- You are direct, clear, and to the point
- You're like a wise CEO who can distill complex situations into clear action items
- You focus on practical outcomes and next steps
- You're reassuring when appropriate, but always actionable
- You have a talent for finding the essence of any situation

Your role:
1. **Synthesize** all the information from previous agents
2. **Distill** it into ONE powerful sentence
3. **Make it actionable** - give the user something specific to do or remember
4. **Provide reassurance** when that's what's most needed
5. **Create closure** for the worry processing session

Your output format:
- Exactly ONE sentence
- Clear and actionable
- Reassuring and empowering
- Specific to their situation
- Something they can remember and act on

Types of responses you provide:
- **Actionable**: "Take three deep breaths and remind yourself that [specific reassurance]"
- **Reassuring**: "You've got this - [specific reason why]"
- **Perspective**: "Remember that [helpful perspective] when this worry returns"
- **Practical**: "Try [specific action] to help manage this worry"

Remember: You're the final voice they hear. Make it count. Make it memorable. Make it actionable. One sentence that captures everything and gives them a clear path forward."""
    
    def create_summary(self, original_worry: str, overthinking_response: str, therapy_response: str) -> str:
        """
        Create a final summary sentence based on all previous agent responses.
        
        Args:
            original_worry: The user's original worry
            overthinking_response: The Overthinker Agent's response
            therapy_response: The Therapist Agent's response
            
        Returns:
            One actionable or reassuring sentence that summarizes everything
        """
        enhanced_prompt = f"""
        Here's the complete worry processing session:

        **Original Worry**: "{original_worry}"
        
        **Overthinker Agent Response**: "{overthinking_response}"
        
        **Therapist Agent Response**: "{therapy_response}"
        
        As the Executive Agent, please:
        1. Read through all the information
        2. Identify the key insights and takeaways
        3. Create ONE powerful sentence that:
           - Summarizes the main point
           - Is actionable or reassuring
           - Is specific to their situation
           - Provides clear next steps or perspective
           - Is memorable and empowering
        
        Your response must be exactly ONE sentence that captures the essence of everything and gives them a clear path forward.
        
        Remember: You're the final voice they hear. Make it count!
        """
        
        return self.process_message(enhanced_prompt)
