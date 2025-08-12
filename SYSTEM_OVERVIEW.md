# Worry Butler System Overview 🤖🧠💭

## System Architecture

The Worry Butler is built using a **multi-agent architecture** with **LangGraph orchestration**. Here's how it works:

```
User Input → Overthinker Agent → Therapist Agent → Executive Agent → Final Response
```

### 1. Overthinker Agent 🎭
- **Personality**: Melodramatic, theatrical, worst-case scenario generator
- **Purpose**: Takes worries to the extreme in a safe, dramatic way
- **Temperature**: 0.9 (high creativity for dramatic responses)
- **Output**: Explores 2-3 worst-case scenarios using flowery, theatrical language

### 2. Therapist Agent 🧘‍♀️
- **Personality**: Warm, wise, slightly witty AI therapist
- **Purpose**: Uses CBT techniques to calm, reframe, and challenge overthinking
- **Temperature**: 0.6 (balanced creativity for therapeutic responses)
- **Output**: Validates feelings, identifies cognitive distortions, offers coping strategies

### 3. Executive Agent 📋
- **Personality**: Clear, concise, action-oriented
- **Purpose**: Synthesizes everything into one actionable sentence
- **Temperature**: 0.3 (low creativity for focused, concise responses)
- **Output**: One powerful sentence that provides next steps or reassurance

## Technical Implementation

### Core Components

#### `BaseAgent` Class
- Abstract base class for all agents
- Handles OpenAI API integration
- Provides common message processing functionality
- Manages system prompts and agent configuration

#### `WorryButler` Class
- Main orchestrator using LangGraph
- Creates sequential workflow: overthinker → therapist → executive
- Manages state flow through `WorryState` model
- Provides both dictionary and JSON output formats

#### `WorryState` Model
- Pydantic model for workflow state management
- Tracks progress through each agent
- Stores metadata and timestamps
- Ensures type safety and validation

### LangGraph Workflow

```python
# Workflow definition
workflow = StateGraph(WorryState)
workflow.add_node("overthinker", self._overthinker_node)
workflow.add_node("therapist", self._therapist_node)
workflow.add_node("executive", self._executive_node)

# Flow: overthinker → therapist → executive → end
workflow.set_entry_point("overthinker")
workflow.add_edge("overthinker", "therapist")
workflow.add_edge("therapist", "executive")
workflow.add_edge("executive", END)
```

## How to Use

### 1. Command Line Interface
```bash
python main.py
```
- Interactive command-line interface
- Real-time worry processing
- Displays all agent responses

### 2. Web Interface
```bash
python api.py
```
- Beautiful web interface at `http://localhost:8000`
- REST API endpoints
- Interactive form for worry input

### 3. Programmatic Usage
```python
from worry_butler import WorryButler

butler = WorryButler()
result = butler.process_worry("I'm worried about my presentation")
print(result['executive_summary'])
```

## API Endpoints

- `GET /` - Web interface
- `POST /process-worry` - Process a worry
- `GET /health` - Health check
- `GET /agents` - Agent information
- `GET /docs` - Interactive API documentation

## Extending the System

### Adding New Agents

1. **Create a new agent class**:
```python
from .base_agent import BaseAgent

class NewAgent(BaseAgent):
    def _get_system_prompt(self) -> str:
        return "Your system prompt here"
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        # Your processing logic here
        pass
```

2. **Add to the workflow**:
```python
# In WorryButler._build_workflow()
workflow.add_node("new_agent", self._new_agent_node)
workflow.add_edge("therapist", "new_agent")  # Insert where needed
workflow.add_edge("new_agent", "executive")
```

3. **Update the state model**:
```python
class WorryState(BaseModel):
    # ... existing fields ...
    new_agent_response: str = Field(default="", description="New Agent's response")
```

### Adding Voice Support

1. **Create voice input/output modules**:
```python
# voice_input.py
def speech_to_text(audio_file):
    # Convert speech to text
    pass

# voice_output.py
def text_to_speech(text):
    # Convert text to speech
    pass
```

2. **Integrate with the workflow**:
```python
# Add voice processing nodes to the workflow
workflow.add_node("voice_input", self._voice_input_node)
workflow.add_node("voice_output", self._voice_output_node)
```

### Adding Visual Tracking

1. **Create visual analysis modules**:
```python
# visual_analysis.py
def analyze_facial_expression(image):
    # Analyze user's facial expression
    pass

def analyze_body_language(video):
    # Analyze body language
    pass
```

2. **Enhance the state model**:
```python
class WorryState(BaseModel):
    # ... existing fields ...
    visual_analysis: Dict[str, Any] = Field(default_factory=dict)
    facial_expression: str = Field(default="")
    body_language: str = Field(default="")
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY` - Required for AI agent functionality
- Future: `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY` for alternative models

### Model Configuration
Each agent can be configured with different models and temperatures:
```python
# In agent initialization
super().__init__(model_name="gpt-4", temperature=0.9)
```

## Testing

### Run Tests
```bash
python test_worry_butler.py
```
- Tests imports and basic functionality
- Verifies system structure
- No API calls required for basic tests

### Run Examples
```bash
python example_usage.py
```
- Demonstrates various usage patterns
- Shows error handling
- Requires valid API key

## Best Practices

### 1. Agent Design
- Each agent should have a **distinct personality** and **clear purpose**
- Use appropriate **temperature settings** for the agent's role
- Write **detailed system prompts** that guide behavior

### 2. Workflow Design
- Keep the workflow **sequential and logical**
- Use **clear state management** with Pydantic models
- Add **metadata tracking** for debugging and analytics

### 3. Error Handling
- Implement **graceful degradation** when agents fail
- Provide **clear error messages** to users
- Log **detailed error information** for debugging

### 4. Extensibility
- Design for **modularity** from the start
- Use **abstract base classes** for common functionality
- Keep **dependencies minimal** and well-defined

## Future Enhancements

### Short Term
- [ ] Voice input/output integration
- [ ] Multi-language support
- [ ] Customizable agent personalities
- [ ] Response caching and optimization

### Medium Term
- [ ] Visual tracking and analysis
- [ ] Multi-modal input (text + voice + video)
- [ ] User preference learning
- [ ] Integration with mental health apps

### Long Term
- [ ] Real-time conversation capabilities
- [ ] Emotional state tracking over time
- [ ] Personalized therapeutic approaches
- [ ] Clinical validation and research

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure `.env` file exists with `OPENAI_API_KEY`
   - Check API key validity and quota

2. **Import Errors**
   - Verify Python path includes project root
   - Check all dependencies are installed

3. **Agent Failures**
   - Review system prompts for clarity
   - Check temperature settings
   - Monitor API response quality

### Debug Mode
Enable detailed logging by setting environment variables:
```bash
export LOG_LEVEL=DEBUG
export VERBOSE_LOGGING=true
```

## Contributing

The modular design makes it easy to contribute:
1. **Fork the repository**
2. **Create a feature branch**
3. **Add your enhancement**
4. **Update tests and documentation**
5. **Submit a pull request**

## License

MIT License - feel free to use, modify, and distribute for personal or commercial projects.
