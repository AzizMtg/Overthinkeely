"""
Main Worry Butler system that orchestrates all three agents.
"""

from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field
from ..agents import OverthinkerAgent, TherapistAgent, ExecutiveAgent
import json

class WorryState(BaseModel):
    """
    State object that flows through the LangGraph workflow.
    
    This tracks the progress of a worry through all three agents.
    """
    original_worry: str = Field(description="The user's original worry statement")
    overthinking_response: str = Field(default="", description="Overthinker Agent's response")
    therapy_response: str = Field(default="", description="Therapist Agent's response")
    executive_summary: str = Field(default="", description="Executive Agent's final summary")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class WorryButler:
    """
    Main Worry Butler system that orchestrates the three-agent workflow.
    
    This class uses LangGraph to create a sequential workflow where:
    1. Overthinker Agent explores worst-case scenarios
    2. Therapist Agent provides CBT-based intervention
    3. Executive Agent creates a final summary
    
    The system is designed to be modular and easily extensible.
    """
    
    def __init__(self):
        """
        Initialize the Worry Butler system with all three agents.
        """
        # Initialize all three agents
        self.overthinker = OverthinkerAgent()
        self.therapist = TherapistAgent()
        self.executive = ExecutiveAgent()
        
        # Build the LangGraph workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self):
        """
        Build the LangGraph workflow that connects all three agents.
        
        Returns:
            A configured LangGraph StateGraph
        """
        # Create the state graph
        workflow = StateGraph(WorryState)
        
        # Add nodes for each agent
        workflow.add_node("overthinker", self._overthinker_node)
        workflow.add_node("therapist", self._therapist_node)
        workflow.add_node("executive", self._executive_node)
        
        # Define the flow: overthinker -> therapist -> executive -> end
        workflow.set_entry_point("overthinker")
        workflow.add_edge("overthinker", "therapist")
        workflow.add_edge("therapist", "executive")
        workflow.add_edge("executive", END)
        
        # Compile the workflow
        return workflow.compile()
    
    def _overthinker_node(self, state: WorryState) -> WorryState:
        """
        Node for the Overthinker Agent.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with overthinking response
        """
        # Process the worry through the Overthinker Agent
        response = self.overthinker.process_worry(state.original_worry)
        
        # Update the state
        state.overthinking_response = response
        
        # Add metadata
        state.metadata["overthinker_timestamp"] = "completed"
        
        return state
    
    def _therapist_node(self, state: WorryState) -> WorryState:
        """
        Node for the Therapist Agent.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with therapy response
        """
        # Process the overthinking through the Therapist Agent
        response = self.therapist.process_overthinking(
            state.original_worry,
            state.overthinking_response
        )
        
        # Update the state
        state.therapy_response = response
        
        # Add metadata
        state.metadata["therapist_timestamp"] = "completed"
        
        return state
    
    def _executive_node(self, state: WorryState) -> WorryState:
        """
        Node for the Executive Agent.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with executive summary
        """
        # Create the final summary through the Executive Agent
        summary = self.executive.create_summary(
            state.original_worry,
            state.overthinking_response,
            state.therapy_response
        )
        
        # Update the state
        state.executive_summary = summary
        
        # Add metadata
        state.metadata["executive_timestamp"] = "completed"
        state.metadata["workflow_completed"] = True
        
        return state
    
    def process_worry(self, worry: str) -> Dict[str, Any]:
        """
        Process a worry through the complete three-agent workflow.
        
        Args:
            worry: The user's worry statement
            
        Returns:
            Dictionary containing all agent responses and metadata
        """
        # Create initial state
        initial_state = WorryState(original_worry=worry)
        
        # Run the workflow
        final_state = self.workflow.invoke(initial_state)
        
        # Convert to dictionary for easy consumption
        result = {
            "original_worry": final_state.original_worry,
            "overthinker_response": final_state.overthinking_response,
            "therapist_response": final_state.therapy_response,
            "executive_summary": final_state.executive_summary,
            "metadata": final_state.metadata
        }
        
        return result
    
    def get_agent_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all agents in the system.
        
        Returns:
            List of dictionaries containing agent information
        """
        return [
            self.overthinker.get_agent_info(),
            self.therapist.get_agent_info(),
            self.executive.get_agent_info()
        ]
    
    def process_worry_json(self, worry: str) -> str:
        """
        Process a worry and return the result as a JSON string.
        
        Args:
            worry: The user's worry statement
            
        Returns:
            JSON string containing all agent responses
        """
        result = self.process_worry(worry)
        return json.dumps(result, indent=2, ensure_ascii=False)
