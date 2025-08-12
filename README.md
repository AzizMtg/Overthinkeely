# Anxiety Court ⚖️

*Put your worries on trial with AI agents*
| ![Prosecutor](https://github.com/user-attachments/assets/4c52602f-f161-4e55-8bee-c456bdefb943) | ![Defense Attorney](https://github.com/user-attachments/assets/778d6572-563f-4ffa-aa3a-55be1588d141) | ![Judge](https://github.com/user-attachments/assets/e777b83f-1dc7-49e2-9030-38cfd9c624d4) |
|----------------------------------------------------|-----------------------------------------------------------|------------------------------------------------------|
| Prosecutor                                         | Defense Attorney                                          | Judge                                                |
| ![Prosecutor Sprite](prosecutor-sprite.gif)        | ![Defense Attorney Sprite](attorney-sprite.gif)           | ![Judge Sprite](judge-sprite.gif)                    |


## What is Anxiety Court?

A simple AI system that helps you deal with anxiety by putting your worries through a courtroom trial. Three AI agents work together:

- **Prosecutor**: Takes your worry and argues for the worst-case scenarios
- **Defense Attorney**: Argues why your worry might not be as bad as you think  
- **Judge**: Makes the final decision and gives you advice

## How It Works

```
Your worry → Prosecutor argues worst-case → Attorney defends you → Judge decides → You get help
```

The agents talk to each other and share information to give you better support.

## Current Features

- Three specialized AI agents that collaborate
- Works with free local AI (Ollama)
- Agents can challenge each other's conclusions
- Web interface for easy use
- Stores conversation history

## Future Features

### Interactive Court
- Choose which evidence to focus on
- Add your own evidence to the case
- Appeal decisions if you disagree

### Smarter Memory
- Remembers patterns in your worries
- Learns what advice works best for you
- Tracks your progress over time

### Better Tools
- Research psychological techniques
- Connect to breathing exercises
- Integration with calendar for context

### Personality Options
- Detective could act like Sherlock Holmes
- Attorney could be like Phoenix Wright
- Customize how formal or casual they are

## Installation

```bash
git clone https://github.com/yourusername/anxiety-court
cd anxiety-court
pip install -r requirements.txt

# For free local AI
python setup_ollama.py

# For OpenAI (requires API key)
cp .env.example .env
# Add your API key to .env
```

## Usage

```python
from anxiety_court import AnxietyCourt

court = AnxietyCourt()
result = court.hear_case("I'm worried about my job interview tomorrow")
print(result.verdict)
```

## Web Interface

```bash
python app.py
# Go to http://localhost:8000
```

## Why This Matters

Most people can't afford therapy or don't know where to start. This makes mental health support:

- Free and available 24/7
- Less intimidating than traditional therapy
- Personalized to what actually helps you
- Fun to use instead of scary

## Project Structure

```
anxiety_court/
├── agents/          # Prosecutor, Attorney, Judge
├── core/           # Main logic
├── web/            # Web interface  
├── app.py          # Run the web server
└── main.py         # Command line version
```

## Contributing

Want to help? We need:

- Developers to improve the agents
- Mental health experts for better techniques
- Users to test and give feedback

## Credits & Disclaimer
This project uses character sprites directly from the Ace Attorney series, which are the property of Capcom and Nintendo. These assets are used strictly for non-commercial, educational, and creative purposes. No money is being made from the use of these sprites, and the project is not affiliated with or endorsed by Capcom or Nintendo in any way.

All rights to the original assets, characters, and trademarks belong to their respective owners. If you are a rights holder and wish for these assets to be removed, please contact me.

## License

MIT - Use this however you want.
