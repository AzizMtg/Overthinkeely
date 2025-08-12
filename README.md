# Worry Butler 🤖🧠💭

A multi-agent AI system designed to help users process anxiety and worry through a unique three-stage approach.

## What is Worry Butler?

Worry Butler takes your anxiety statement and processes it through three specialized AI agents:

1. **Overthinker Agent** 🎭 - Takes your worry to the extreme, exploring worst-case scenarios (safely)
2. **Therapist Agent** 🧘‍♀️ - Calms, reframes, and challenges the overthinking using CBT techniques and humor
3. **Executive Agent** 📋 - Summarizes everything into one actionable or reassuring sentence

## How It Works

```
User Input → Overthinker → Therapist → Executive → Final Response
```

The system uses LangGraph for agent orchestration, ensuring each agent builds upon the previous one's work to provide comprehensive anxiety processing.

## Features

- **Multi-Agent Architecture**: Each agent has a distinct personality and expertise
- **Modular Design**: Easy to extend with voice, visual tracking, and other features
- **JSON Output**: Structured responses for easy integration
- **Environment Configuration**: Secure API key management
- **FastAPI Interface**: Ready for web deployment

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `env_example.txt` to `.env` and add your OpenAI API key
4. Run the system:
   ```bash
   python main.py
   ```

## Usage

### Basic Usage
```python
from worry_butler import WorryButler

butler = WorryButler()
response = butler.process_worry("I'm worried about my presentation tomorrow")
print(response)
```

### Web Interface
Start the FastAPI server:
```bash
python api.py
```

Then visit `http://localhost:8000` to use the web interface.

## Project Structure

```
worry_butler/
├── agents/           # Individual AI agents
├── core/            # Core system logic
├── api/             # FastAPI web interface
├── main.py          # Main entry point
├── api.py           # Web API server
└── requirements.txt # Dependencies
```

## Future Extensions

- Voice input/output integration
- Visual tracking and analysis
- Multi-language support
- Customizable agent personalities
- Integration with mental health apps

## Contributing

Feel free to contribute! The modular design makes it easy to add new agents or features.

## License

MIT License - feel free to use this for personal or commercial projects.
