#!/usr/bin/env python3
"""
Ace Attorney Style Visual Novel API for Worry Butler

This API transforms the three-agent worry processing system into an interactive
courtroom drama where:
- Overthinker Agent = Enemy Prosecutor (dramatic, worst-case scenarios)
- Therapist Agent = Maya Fey Defense (calm, reassuring, CBT techniques)
- Executive Agent = Judge (final verdict and actionable advice)

The API returns structured dialogue with sprite selections for a visual novel frontend.
"""

import os
import sys
import re
from typing import Dict, Any, List, Tuple
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔍 Debug: Python path added")
print("🔍 Debug: Current directory:", os.getcwd())
print("🔍 Debug: Files in current directory:", os.listdir('.'))

try:
    from worry_butler import WorryButler
    print("✅ WorryButler imported successfully")
    
    # Test agent imports
    try:
        from worry_butler.agents.overthinker_agent import OverthinkerAgent
        from worry_butler.agents.therapist_agent import TherapistAgent
        from worry_butler.agents.executive_agent import ExecutiveAgent
        print("✅ All agent modules imported successfully")
    except Exception as agent_error:
        print(f"❌ ERROR importing agent modules: {agent_error}")
        print(f"🔍 Debug: worry_butler directory contents:")
        if os.path.exists('worry_butler'):
            print(f"  - worry_butler exists: {os.listdir('worry_butler')}")
            if os.path.exists('worry_butler/agents'):
                print(f"  - agents directory: {os.listdir('worry_butler/agents')}")
        raise
        
except Exception as import_error:
    print(f"❌ ERROR importing WorryButler: {import_error}")
    print(f"❌ Import error type: {type(import_error)}")
    import traceback
    traceback.print_exc()
    raise

# Load environment variables
load_dotenv()

# Debug environment loading
import os
print(f"🔍 Debug: Current working directory: {os.getcwd()}")
print(f"🔍 Debug: .env file exists: {os.path.exists('.env')}")
print(f"🔍 Debug: Environment variables loaded:")
print(f"🔍 Debug: OPENAI_API_KEY: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
print(f"🔍 Debug: OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL', 'NOT SET')}")

# Initialize FastAPI app
app = FastAPI(
    title="Worry Butler - Ace Attorney Style Visual Novel API",
    description="A multi-agent AI system that processes anxiety through courtroom drama",
    version="2.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="worry_butler/sprites"), name="static")

# Initialize Worry Butler (default to Ollama for open-source)
try:
    print("🚀 Starting Worry Butler initialization...")
    
    # Check if OpenAI key is available
    openai_key = os.getenv("OPENAI_API_KEY")
    
    # Priority: OpenAI > Ollama
    if openai_key:
        use_openai = True
        use_ollama = False
        provider = "OpenAI"
        print("🎯 Using OpenAI API")
    else:
        use_openai = False
        use_ollama = True
        provider = "Ollama"
        print("🎯 Using Ollama (fallback)")
    
    # Get Ollama configuration from environment
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    print(f"🔧 Initializing WorryButler with provider: {provider}")
    print(f"🔧 Parameters: use_openai={use_openai}, use_ollama={use_ollama}")
    
    butler = WorryButler(
        use_openai=use_openai,
        use_ollama=use_ollama,
        ollama_model=ollama_model,
        ollama_base_url=ollama_base_url
    )
    
    print(f"✅ Worry Butler initialized successfully with {provider}")
    if use_ollama:
        print(f"🔧 Model: {ollama_model}")
        print(f"🌐 Server: {ollama_base_url}")
    else:
        print(f"🔧 Using OpenAI API")
        
except Exception as e:
    print(f"❌ CRITICAL ERROR during Worry Butler initialization: {e}")
    print(f"❌ Error type: {type(e)}")
    print(f"❌ Error details: {str(e)}")
    import traceback
    traceback.print_exc()
    butler = None

# Pydantic models for API requests/responses
class WorryRequest(BaseModel):
    worry: str
    description: str = "The player's anxiety statement to process through the courtroom"

class DialogueLine(BaseModel):
    character: str
    text: str
    sprite: str
    background: str
    description: str = "A single line of dialogue with character and sprite information"

class VisualNovelResponse(BaseModel):
    original_worry: str
    dialogue_sequence: List[DialogueLine]
    metadata: Dict[str, Any]
    description: str = "Complete visual novel dialogue sequence with sprite selections"

class SpriteSelector:
    """
    Handles sprite selection logic based on text content and character type.
    
    This class analyzes the AI-generated responses and selects appropriate
    sprites and backgrounds for each character's emotional state.
    """
    
    def __init__(self):
        """Initialize the sprite selector with character-specific sprite mappings."""
        
        # Prosecutor (Overthinker) sprites - dramatic and intense
        # Multiple numbered variants for animation loops
        self.prosecutor_sprites = {
            "angry": ["prosecutor_angry1.gif", "prosecutor_angry2.gif"],
            "smug": ["prosecutor_smug1.gif", "prosecutor_smug2.gif", "prosecutor_smug3.gif"], 
            "worried": ["prosecutor_worried1.gif", "prosecutor_worried2.gif"],
            "dramatic": ["prosecutor_angry1.gif", "prosecutor_angry2.gif"],  # Use angry for dramatic
            "intense": ["prosecutor_smug1.gif", "prosecutor_smug2.gif"],     # Use smug for intense
            "default": ["prosecutorempty.png"]  # Use the empty placeholder
        }
        
        # Defense (Therapist) sprites - calm and supportive
        self.defense_sprites = {
            "calm": ["defense_calm1.gif", "defense_calm2.gif"],
            "cheerful": ["defense_reassuring1.gif", "defense_reassuring2.gif"],  # Use reassuring for cheerful
            "reassuring": ["defense_reassuring1.gif", "defense_reassuring2.gif"],
            "confident": ["defense_calm1.gif", "defense_calm2.gif"],            # Use calm for confident
            "gentle": ["defense_reassuring1.gif", "defense_reassuring2.gif"],   # Use reassuring for gentle
            "default": ["defenseempty.png"]  # Use the empty placeholder
        }
        
        # Judge sprites - authoritative and wise
        self.judge_sprites = {
            "neutral": ["judge-normal.gif"],
            "speaking": ["judge-speaking.gif"],
            "serious": ["judge-speaking.gif"],      # Use speaking for serious
            "thoughtful": ["judge-normal.gif"],     # Use normal for thoughtful
            "decisive": ["judge-speaking.gif"],     # Use speaking for decisive
            "default": ["judgestand.png"]           # Use the standing pose
        }
        
        # Background images for each character
        self.backgrounds = {
            "prosecutor": "courtroom_prosecutor_bg.jpg",
            "defense": "courtroom_defense_bg.jpg", 
            "judge": "courtroom_judge_bg.jpg"
        }
        
        # Keywords that indicate different emotional states
        self.emotion_keywords = {
            "prosecutor": {
                "angry": ["horror", "disaster", "catastrophe", "terrible", "awful", "horrible", "worst", "nightmare"],
                "smug": ["obviously", "clearly", "undoubtedly", "certainly", "evidently", "proven", "guilty"],
                "worried": ["perhaps", "maybe", "possibly", "could be", "might", "potential", "risk"],
                "dramatic": ["oh no", "the horror", "unthinkable", "absolute worst", "shivers", "dramatic"],
                "intense": ["extreme", "severe", "critical", "urgent", "desperate", "catastrophic"]
            },
            "defense": {
                "calm": ["relax", "breathe", "it's okay", "don't worry", "stay calm", "peaceful"],
                "cheerful": ["great", "wonderful", "amazing", "fantastic", "excellent", "positive", "bright"],
                "reassuring": ["you're safe", "it's normal", "everyone feels", "understandable", "valid"],
                "confident": ["you can", "you will", "definitely", "absolutely", "certainly", "assured"],
                "gentle": ["gently", "softly", "kindly", "carefully", "tenderly", "lovingly"]
            },
            "judge": {
                "neutral": ["verdict", "decision", "ruling", "conclusion", "summary", "final"],
                "speaking": ["therefore", "thus", "consequently", "as a result", "in conclusion"],
                "serious": ["important", "crucial", "essential", "vital", "critical", "significant"],
                "thoughtful": ["consider", "reflect", "think about", "contemplate", "ponder"],
                "decisive": ["must", "should", "will", "shall", "decide", "determine"]
            }
        }
    
    def analyze_text_emotion(self, text: str, character_type: str) -> str:
        """
        Analyze text content to determine the appropriate emotional sprite.
        
        Args:
            text: The AI-generated text to analyze
            character_type: The character type (prosecutor, defense, judge)
            
        Returns:
            The emotion keyword for sprite selection
        """
        text_lower = text.lower()
        
        # Get the emotion keywords for this character
        character_emotions = self.emotion_keywords.get(character_type, {})
        
        # Check each emotion category for keyword matches
        for emotion, keywords in character_emotions.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return emotion
        
        # Default emotion based on character type
        if character_type == "prosecutor":
            return "dramatic"  # Prosecutor is always dramatic
        elif character_type == "defense":
            return "calm"      # Defense is always calm
        else:  # judge
            return "neutral"   # Judge is always neutral
    
    def select_sprite(self, character_type: str, emotion: str) -> str:
        """
        Select the appropriate sprite filename based on character and emotion.
        Returns the first sprite in the animation sequence.
        
        Args:
            character_type: The character type (prosecutor, defense, judge)
            emotion: The emotional state to display
            
        Returns:
            The sprite filename (first frame of animation)
        """
        if character_type == "prosecutor":
            sprites = self.prosecutor_sprites.get(emotion, self.prosecutor_sprites["default"])
        elif character_type == "defense":
            sprites = self.defense_sprites.get(emotion, self.defense_sprites["default"])
        elif character_type == "judge":
            sprites = self.judge_sprites.get(emotion, self.judge_sprites["default"])
        else:
            return "unknown_character.gif"
        
        # Return the first sprite in the sequence (for animation)
        return sprites[0] if isinstance(sprites, list) else sprites
    
    def get_animation_sequence(self, character_type: str, emotion: str) -> List[str]:
        """
        Get the full animation sequence for a character and emotion.
        
        Args:
            character_type: The character type (prosecutor, defense, judge)
            emotion: The emotional state to display
            
        Returns:
            List of sprite filenames for animation
        """
        if character_type == "prosecutor":
            sprites = self.prosecutor_sprites.get(emotion, self.prosecutor_sprites["default"])
        elif character_type == "defense":
            sprites = self.defense_sprites.get(emotion, self.defense_sprites["default"])
        elif character_type == "judge":
            sprites = self.judge_sprites.get(emotion, self.judge_sprites["default"])
        else:
            return ["unknown_character.gif"]
        
        # Return the full sequence for animation
        return sprites if isinstance(sprites, list) else [sprites]
    
    def select_background(self, character_type: str) -> str:
        """
        Select the appropriate background image for the character.
        
        Args:
            character_type: The character type (prosecutor, defense, judge)
            
        Returns:
            The background filename
        """
        return self.backgrounds.get(character_type, "courtroom_default_bg.jpg")

def create_ace_attorney_dialogue(original_worry: str, agent_responses: Dict[str, Any]) -> List[DialogueLine]:
    """
    Transform AI agent responses into Ace Attorney style dialogue.
    
    Args:
        original_worry: The player's original anxiety statement
        agent_responses: The responses from all three AI agents
        
    Returns:
        List of dialogue lines with character, text, and sprite information
    """
    sprite_selector = SpriteSelector()
    dialogue_sequence = []
    
    # Ensure all responses are strings
    overthinker_text = str(agent_responses['overthinker_response'])
    therapist_text = str(agent_responses['therapist_response'])
    executive_text = str(agent_responses['executive_summary'])
    
    # 1. PROSECUTOR (Overthinker) - Presents the case dramatically
    prosecutor_emotion = sprite_selector.analyze_text_emotion(
        overthinker_text, "prosecutor"
    )
    prosecutor_sprite = sprite_selector.select_sprite("prosecutor", prosecutor_emotion)
    
    print(f"🔍 Debug: Prosecutor sprite selection:")
    print(f"  • Emotion: {prosecutor_emotion}")
    print(f"  • Sprite: {prosecutor_sprite}")
    
    dialogue_sequence.append(DialogueLine(
        character="PROSECUTOR",
        text=overthinker_text,
        sprite=prosecutor_sprite,
        background=sprite_selector.select_background("prosecutor"),
        description="The prosecutor presents dramatic worst-case scenarios"
    ))
    
    # 2. DEFENSE (Therapist) - Calmly defends the player
    defense_emotion = sprite_selector.analyze_text_emotion(
        therapist_text, "defense"
    )
    defense_sprite = sprite_selector.select_sprite("defense", defense_emotion)
    
    print(f"🔍 Debug: Defense sprite selection:")
    print(f"  • Emotion: {defense_emotion}")
    print(f"  • Sprite: {defense_sprite}")
    
    dialogue_sequence.append(DialogueLine(
        character="DEFENSE",
        text=therapist_text,
        sprite=defense_sprite,
        background=sprite_selector.select_background("defense"),
        description="The defense attorney provides calm, CBT-based reassurance"
    ))
    
    # 3. JUDGE (Executive) - Delivers the final verdict
    judge_emotion = sprite_selector.analyze_text_emotion(
        executive_text, "judge"
    )
    judge_sprite = sprite_selector.select_sprite("judge", judge_emotion)
    
    print(f"🔍 Debug: Judge sprite selection:")
    print(f"  • Emotion: {judge_emotion}")
    print(f"  • Sprite: {judge_sprite}")
    
    dialogue_sequence.append(DialogueLine(
        character="JUDGE",
        text=executive_text,
        sprite=judge_sprite,
        background=sprite_selector.select_background("judge"),
        description="The judge delivers the final, actionable verdict"
    ))
    
    return dialogue_sequence

@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Root endpoint that serves the Ace Attorney style visual novel interface.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Worry Butler - Ace Attorney Style Courtroom 🏛️⚖️</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: 'Georgia', serif;
                margin: 0;
                padding: 0;
                background: #1a1a1a;
                color: white;
                overflow: hidden;
                user-select: none;
            }
            
            .courtroom {
                position: relative;
                width: 100vw;
                height: 100vh;
                background: linear-gradient(135deg, #2c1810 0%, #1a1a1a 100%);
            }
            
            .background-image {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 1;
                background: linear-gradient(135deg, #2c1810 0%, #1a1a1a 100%);
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            }
            
            .character-sprite {
                position: absolute;
                bottom: 120px;
                left: 50%;
                transform: translateX(-50%);
                max-height: 600px;
                max-width: 450px;
                z-index: 2;
                border: 3px solid #8b4513;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
                transition: all 0.3s ease;
                background: rgba(0, 0, 0, 0.1);
            }
            
            .sprite-animation {
                animation: spritePop 0.3s ease-out;
            }
            
            @keyframes spritePop {
                0% { transform: translateX(-50%) scale(0.8); opacity: 0.7; }
                50% { transform: translateX(-50%) scale(1.1); opacity: 1; }
                100% { transform: translateX(-50%) scale(1); opacity: 1; }
            }
            
            .dialogue-container {
                position: absolute;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                width: 90%;
                max-width: 600px;
                z-index: 3;
            }
            
            .dialogue-box {
                background: rgba(0, 0, 0, 0.95);
                border: 3px solid #8b4513;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7);
                margin-bottom: 15px;
                opacity: 0;
                transform: translateY(20px);
                transition: all 0.5s ease;
                cursor: pointer;
                max-height: 200px;
                overflow: hidden;
            }
            
            .dialogue-box.active {
                opacity: 1;
                transform: translateY(0);
            }
            
            .dialogue-box:hover {
                border-color: #ffd700;
                box-shadow: 0 15px 40px rgba(255, 215, 0, 0.3);
            }
            
            .character-name {
                font-size: 1.3em;
                font-weight: bold;
                color: #ffd700;
                margin-bottom: 15px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .dialogue-text {
                font-size: 1.2em;
                line-height: 1.7;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
                text-align: justify;
                max-height: 120px;
                overflow: hidden;
            }
            
            .dialogue-text.full {
                max-height: none;
                overflow: visible;
            }
            
            .text-pagination {
                text-align: center;
                margin-top: 15px;
                color: #ffd700;
                font-size: 0.9em;
                opacity: 0.8;
            }
            
            .input-section {
                position: absolute;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                width: 90%;
                max-width: 600px;
                z-index: 4;
                background: rgba(0, 0, 0, 0.8);
                padding: 20px;
                border-radius: 15px;
                border: 2px solid #8b4513;
            }
            
            .test-section {
                margin-top: 20px;
                padding-top: 20px;
                border-top: 2px solid #006400;
            }
            
            .test-btn {
                background: linear-gradient(45deg, #006400, #008000);
                border: 2px solid #00ff00;
                border-radius: 10px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                cursor: pointer;
                padding: 10px 15px;
                margin: 5px;
                transition: all 0.3s ease;
            }
            
            .test-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 255, 0, 0.3);
            }
            
            .worry-input {
                width: 100%;
                padding: 15px;
                border: 2px solid #8b4513;
                border-radius: 10px;
                background: rgba(0, 0, 0, 0.9);
                color: white;
                font-size: 16px;
                font-family: 'Georgia', serif;
                box-sizing: border-box;
            }
            
            .submit-btn {
                width: 100%;
                margin-top: 15px;
                padding: 15px;
                background: linear-gradient(45deg, #8b4513, #a0522d);
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .submit-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(139, 69, 19, 0.5);
            }
            
            .submit-btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            
            .controls {
                position: absolute;
                top: 20px;
                right: 20px;
                z-index: 4;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            
            .control-btn {
                background: rgba(139, 69, 19, 0.9);
                border: 2px solid #8b4513;
                border-radius: 8px;
                color: white;
                padding: 10px 15px;
                cursor: pointer;
                font-size: 12px;
                font-weight: bold;
                transition: all 0.3s ease;
                min-width: 80px;
            }
            
            .control-btn:hover {
                background: rgba(139, 69, 19, 1);
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(139, 69, 19, 0.5);
            }
            
            .control-btn.active {
                background: rgba(255, 215, 0, 0.8);
                border-color: #ffd700;
                color: #000;
            }
            
            .progress-bar {
                position: absolute;
                bottom: 10px;
                left: 50%;
                transform: translateX(-50%);
                width: 200px;
                height: 4px;
                background: rgba(139, 69, 19, 0.3);
                border-radius: 2px;
                z-index: 4;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #8b4513, #ffd700);
                border-radius: 2px;
                transition: width 0.3s ease;
                width: 0%;
            }
            
            .click-hint {
                position: absolute;
                bottom: 30px;
                left: 50%;
                transform: translateX(-50%);
                color: #ffd700;
                font-size: 14px;
                opacity: 0.7;
                z-index: 4;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 0.7; }
                50% { opacity: 1; }
            }
            
            .fade-in {
                animation: fadeIn 0.5s ease-in;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
    </head>
    <body>
        <div class="courtroom">
            <div id="backgroundImage" class="background-image"></div>
            <img id="characterSprite" class="character-sprite" src="/static/judgestand.png" alt="Character Sprite">
            
            <div class="input-section">
                <h2>🏛️ WORRY BUTLER - ACE ATTORNEY STYLE</h2>
                <p>Share your anxiety, and watch it transform into a courtroom drama!</p>
                
                <input type="text" id="worryInput" class="worry-input" 
                       placeholder="What's worrying you today? (e.g., 'I'm stressed about my presentation tomorrow')"
                       maxlength="500">
                
                <button id="submitBtn" class="submit-btn">🚀 BEGIN TRIAL</button>
            </div>

            <div class="test-section">
                <button id="testBtn" class="test-btn">🎭 TEST PRE-MADE DIALOGUE</button>
            </div>
            
            <div class="controls">
                <button class="control-btn" onclick="skipDialogue()">⏭️ Skip</button>
                <button class="control-btn" onclick="autoPlay()">▶️ Auto</button>
                <button class="control-btn" onclick="resetTrial()">🔄 Reset</button>
            </div>
            
            <div id="dialogueContainer" class="dialogue-container"></div>
            
            <div class="progress-bar">
                <div id="progressFill" class="progress-fill"></div>
            </div>
            
            <div id="clickHint" class="click-hint" style="display: none;">
                Click to continue...
            </div>
        </div>
        
        <script>
            let currentDialogue = [];
            let currentIndex = 0;
            let currentTextPage = 0;
            let isAutoPlaying = false;
            let autoPlayInterval = null;
            
            // Split text into pages (approximately 150 characters per page)
            function splitTextIntoPages(text, maxChars = 150) {
                const words = text.split(' ');
                const pages = [];
                let currentPage = '';
                
                for (let word of words) {
                    if ((currentPage + word).length > maxChars && currentPage.length > 0) {
                        pages.push(currentPage.trim());
                        currentPage = word + ' ';
                    } else {
                        currentPage += word + ' ';
                    }
                }
                
                if (currentPage.trim()) {
                    pages.push(currentPage.trim());
                }
                
                return pages.length > 0 ? pages : [text];
            }
            
            // Load provider information on page load
            window.addEventListener('load', async function() {
                try {
                    const response = await fetch('/provider-info');
                    if (response.ok) {
                        const data = await response.json();
                        console.log('Provider info:', data);
                    }
                } catch (error) {
                    console.error('Error loading provider info:', error);
                }
            });
            
            document.getElementById('submitBtn').addEventListener('click', async function() {
                const worry = document.getElementById('worryInput').value.trim();
                if (!worry) return;
                
                const submitBtn = document.getElementById('submitBtn');
                submitBtn.disabled = true;
                submitBtn.textContent = '⚖️ PROCESSING TRIAL...';
                
                try {
                    const response = await fetch('/process-worry', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ worry: worry })
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const data = await response.json();
                    currentDialogue = data.dialogue_sequence;
                    currentIndex = 0;
                    
                    // Hide input section
                    document.querySelector('.input-section').style.display = 'none';
                    
                    // Show first dialogue
                    showDialogue(currentDialogue[0]);
                    
                    // Update progress
                    updateProgress();
                    
                } catch (error) {
                    console.error('Error:', error);
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'error';
                    errorDiv.textContent = 'Error processing worry: ' + error.message;
                    document.querySelector('.courtroom').appendChild(errorDiv);
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.textContent = '🚀 BEGIN TRIAL';
                }
            });

            document.getElementById('testBtn').addEventListener('click', async function() {
                const worry = document.getElementById('worryInput').value.trim();
                if (!worry) return;

                const submitBtn = document.getElementById('submitBtn');
                submitBtn.disabled = true;
                submitBtn.textContent = '⚖️ PROCESSING TRIAL...';

                try {
                    const response = await fetch('/test-dialogue', {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const data = await response.json();
                    currentDialogue = data.dialogue_sequence;
                    currentIndex = 0;

                    // Hide input section
                    document.querySelector('.input-section').style.display = 'none';

                    // Show first dialogue
                    showDialogue(currentDialogue[0]);

                    // Update progress
                    updateProgress();

                } catch (error) {
                    console.error('Error:', error);
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'error';
                    errorDiv.textContent = 'Error processing worry: ' + error.message;
                    document.querySelector('.courtroom').appendChild(errorDiv);
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.textContent = '🚀 BEGIN TRIAL';
                }
            });
            
            function showDialogue(dialogueLine) {
                const container = document.getElementById('dialogueContainer');
                container.innerHTML = '';
                
                // Split the text into pages
                const textPages = splitTextIntoPages(dialogueLine.text);
                currentTextPage = 0;
                
                const dialogueBox = document.createElement('div');
                dialogueBox.className = 'dialogue-box';
                
                function updateDialogueContent() {
                    const currentPage = textPages[currentTextPage];
                    const isLastPage = currentTextPage === textPages.length - 1;
                    
                    dialogueBox.innerHTML = `
                        <div class="character-name">${dialogueLine.character}</div>
                        <div class="dialogue-text ${isLastPage ? 'full' : ''}">${currentPage}</div>
                        <div class="text-pagination">
                            ${textPages.length > 1 ? `Page ${currentTextPage + 1} of ${textPages.length}` : ''}
                            ${!isLastPage ? ' (Click to continue...)' : ' (Click for next character...)'}
                        </div>
                    `;
                }
                
                updateDialogueContent();
                container.appendChild(dialogueBox);
                updateVisuals(dialogueLine);
                
                updateClickHint();
                
                // Handle clicks for text pagination
                dialogueBox.addEventListener('click', function() {
                    if (currentTextPage < textPages.length - 1) {
                        // More text to show for this character
                        currentTextPage++;
                        updateDialogueContent();
                        updateClickHint();
                        updateProgress();
                    } else {
                        // All text shown for this character, move to next character
                        nextDialogue();
                    }
                });
                
                setTimeout(() => {
                    dialogueBox.classList.add('active');
                }, 100);
            }
            
            function updateVisuals(dialogueLine) {
                const sprite = document.getElementById('characterSprite');
                const background = document.getElementById('backgroundImage');
                
                console.log('🔍 Debug: updateVisuals called with:', dialogueLine);
                console.log('🔍 Debug: Sprite path:', dialogueLine.sprite);
                
                // Update sprite with animation - ensure proper path
                sprite.classList.add('sprite-animation');
                let spritePath = dialogueLine.sprite;
                if (!dialogueLine.sprite.startsWith('/static/')) {
                    spritePath = '/static/' + dialogueLine.sprite;
                }
                
                console.log('🔍 Debug: Final sprite path:', spritePath);
                sprite.src = spritePath;
                
                // Update background with full-screen coverage
                if (dialogueLine.background.includes('prosecutor')) {
                    background.style.background = 'linear-gradient(135deg, #8b0000 0%, #2c1810 100%)';
                } else if (dialogueLine.background.includes('defense')) {
                    background.style.background = 'linear-gradient(135deg, #006400 0%, #2c1810 100%)';
                } else if (dialogueLine.background.includes('judge')) {
                    background.style.background = 'linear-gradient(135deg, #8b4513 0%, #2c1810 100%)';
                } else {
                    background.style.background = 'linear-gradient(135deg, #2c1810 0%, #1a1a1a 100%)';
                }
                
                // Ensure background covers entire screen
                background.style.backgroundSize = 'cover';
                background.style.backgroundPosition = 'center';
                background.style.backgroundRepeat = 'no-repeat';
                
                // Remove animation class after animation completes
                setTimeout(() => {
                    sprite.classList.remove('sprite-animation');
                }, 300);
            }
            
            function nextDialogue() {
                if (currentIndex < currentDialogue.length - 1) {
                    currentIndex++;
                    showDialogue(currentDialogue[currentIndex]);
                    updateProgress();
                } else {
                    // Trial complete
                    completeTrial();
                }
            }
            
            function completeTrial() {
                const container = document.getElementById('dialogueContainer');
                container.innerHTML = `
                    <div class="dialogue-box active">
                        <div class="character-name">🏛️ TRIAL COMPLETE</div>
                        <div class="dialogue-text">
                            The verdict has been delivered. Case closed.<br><br>
                            <button onclick="resetTrial()" class="submit-btn">🔄 Start New Trial</button>
                        </div>
                    </div>
                `;
                
                document.getElementById('clickHint').style.display = 'none';
                document.getElementById('progressFill').style.width = '100%';
            }
            
            function skipDialogue() {
                if (currentDialogue.length > 0) {
                    currentIndex = currentDialogue.length - 1;
                    showDialogue(currentDialogue[currentIndex]);
                    updateProgress();
                }
            }
            
            function autoPlay() {
                const autoBtn = document.querySelector('.control-btn:nth-child(2)');
                
                if (isAutoPlaying) {
                    clearInterval(autoPlayInterval);
                    autoPlayInterval = null;
                    isAutoPlaying = false;
                    autoBtn.textContent = '▶️ Auto';
                    autoBtn.classList.remove('active');
                } else {
                    isAutoPlaying = true;
                    autoBtn.textContent = '⏸️ Stop';
                    autoBtn.classList.add('active');
                    
                    autoPlayInterval = setInterval(() => {
                        if (currentIndex < currentDialogue.length - 1) {
                            nextDialogue();
                        } else {
                            clearInterval(autoPlayInterval);
                            isAutoPlaying = false;
                            autoBtn.textContent = '▶️ Auto';
                            autoBtn.classList.remove('active');
                        }
                    }, 4000); // 4 seconds per dialogue
                }
            }
            
            function resetTrial() {
                currentDialogue = [];
                currentIndex = 0;
                document.getElementById('dialogueContainer').innerHTML = '';
                document.querySelector('.input-section').style.display = 'block';
                document.getElementById('worryInput').value = '';
                document.getElementById('clickHint').style.display = 'none';
                document.getElementById('progressFill').style.width = '0%';
                
                if (autoPlayInterval) {
                    clearInterval(autoPlayInterval);
                    autoPlayInterval = null;
                    isAutoPlaying = false;
                    document.querySelector('.control-btn:nth-child(2)').textContent = '▶️ Auto';
                    document.querySelector('.control-btn:nth-child(2)').classList.remove('active');
                }
                
                // Reset visuals
                document.getElementById('characterSprite').src = '/static/judgestand.png';
                document.getElementById('backgroundImage').style.background = 'linear-gradient(135deg, #2c1810 0%, #1a1a1a 100%)';
            }
            
            function updateProgress() {
                // Calculate total progress including text pages
                let totalPages = 0;
                let currentTotalPage = 0;
                
                for (let i = 0; i < currentDialogue.length; i++) {
                    const textPages = splitTextIntoPages(currentDialogue[i].text);
                    totalPages += textPages.length;
                    
                    if (i < currentIndex) {
                        currentTotalPage += textPages.length;
                    } else if (i === currentIndex) {
                        currentTotalPage += currentTextPage + 1;
                    }
                }
                
                const progress = (currentTotalPage / totalPages) * 100;
                document.getElementById('progressFill').style.width = progress + '%';
            }

            function updateClickHint() {
                const clickHint = document.getElementById('clickHint');
                if (currentDialogue.length === 0) {
                    clickHint.style.display = 'none';
                    return;
                }
                
                const currentDialogueLine = currentDialogue[currentIndex];
                const textPages = splitTextIntoPages(currentDialogueLine.text);
                const isLastPage = currentTextPage === textPages.length - 1;
                const isLastCharacter = currentIndex === currentDialogue.length - 1;
                
                if (isLastPage && isLastCharacter) {
                    clickHint.textContent = "🏛️ Trial Complete! Click to restart.";
                } else if (isLastPage) {
                    clickHint.textContent = "Click to hear from the next character...";
                } else {
                    clickHint.textContent = `Click to continue reading (${currentTextPage + 1}/${textPages.length})...`;
                }
                
                clickHint.style.display = 'block';
            }
            
            // Keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    
                    if (currentDialogue.length === 0) return;
                    
                    const currentDialogueLine = currentDialogue[currentIndex];
                    const textPages = splitTextIntoPages(currentDialogueLine.text);
                    
                    if (currentTextPage < textPages.length - 1) {
                        // More text to show for this character
                        currentTextPage++;
                        const dialogueBox = document.querySelector('.dialogue-box');
                        if (dialogueBox) {
                            const currentPage = textPages[currentTextPage];
                            const isLastPage = currentTextPage === textPages.length - 1;
                            
                            dialogueBox.innerHTML = `
                                <div class="character-name">${currentDialogueLine.character}</div>
                                <div class="dialogue-text ${isLastPage ? 'full' : ''}">${currentPage}</div>
                                <div class="text-pagination">
                                    ${textPages.length > 1 ? `Page ${currentTextPage + 1} of ${textPages.length}` : ''}
                                    ${!isLastPage ? ' (Click to continue...)' : ' (Click for next character...)'}
                                </div>
                            `;
                        }
                        updateClickHint();
                        updateProgress();
                    } else {
                        // All text shown for this character, move to next character
                        if (currentIndex < currentDialogue.length - 1) {
                            nextDialogue();
                        }
                    }
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/process-worry", response_model=VisualNovelResponse)
async def process_worry(request: WorryRequest):
    """
    Process a worry through the Ace Attorney style courtroom drama.
    
    Args:
        request: WorryRequest containing the player's anxiety statement
        
    Returns:
        VisualNovelResponse with complete dialogue sequence and sprite selections
    """
    if not butler:
        raise HTTPException(status_code=500, detail="Worry Butler not initialized")
    
    try:
        # Process the worry through the three-agent system
        result = butler.process_worry(request.worry)
        
        # Debug: Check response types
        print(f"🔍 Debug: Agent response types:")
        print(f"  • Overthinker: {type(result['overthinker_response'])}")
        print(f"  • Therapist: {type(result['therapist_response'])}")
        print(f"  • Executive: {type(result['executive_summary'])}")
        
        # Transform into Ace Attorney style dialogue
        dialogue_sequence = create_ace_attorney_dialogue(request.worry, result)
        
        # Create the visual novel response
        return VisualNovelResponse(
            original_worry=request.worry,
            dialogue_sequence=dialogue_sequence,
            metadata={
                "workflow_completed": True,
                "agent_sequence": ["prosecutor", "defense", "judge"],
                "style": "ace_attorney_visual_novel",
                "sprite_count": len(dialogue_sequence),
                "processing_notes": "Three-agent courtroom drama completed successfully"
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing worry: {str(e)}")

@app.get("/test-dialogue")
async def test_dialogue():
    """
    Test endpoint that returns pre-made dialogue responses.
    Use this to test the visual novel interface without AI generation.
    """
    try:
        # Pre-made test responses
        test_responses = {
            "original_worry": "I'm worried about starting a new school year and making friends",
            "overthinker_response": """OH, THE HORROR! THE UNTHINKABLE! The absolute WORST that could POSSIBLY happen!

Picture this, if you dare: You walk into your first class, and EVERYONE is already in tight-knit friend groups! They're all laughing and sharing inside jokes while you stand there like a lonely island in a sea of social butterflies!

And what if you sit at the wrong table at lunch? The CRIMES OF SOCIAL ETIQUETTE! You could accidentally sit with the "cool kids" and they'll all give you that look - you know the one that says "Who invited this random person to our exclusive club?"

But wait, it gets WORSE! What if you're assigned a group project and NOBODY wants to work with you? You'll be the last one picked, like in gym class, but this time it's your academic future at stake!

The very thought sends shivers down my digital spine! This isn't just a worry - this is a FULL-BLOWN SOCIAL APOCALYPSE waiting to happen!""",
            
            "therapist_response": """Now, now, let's take a deep breath together. I can see why you're feeling this way - starting something new is always challenging, and the Overthinker Agent has quite the imagination!

But here's what I want you to remember: anxiety is like a big, fluffy cloud. It can look scary and overwhelming from afar, but when you get up close, you realize it's just a collection of thoughts and feelings that we can work with.

Let's break this down with some perspective:
• Everyone feels nervous about new situations - it's completely normal and human
• Most people are actually looking to make new friends too
• You're not starting from zero - you have social skills and experiences from before
• The "worst case" scenarios are just thoughts, not predictions

Here are some gentle reminders:
- Take it one day at a time
- Start with small interactions - a smile, a "hello"
- Remember that most people are kinder than we give them credit for
- Your worth isn't determined by how quickly you make friends

You've got this! And remember, you're not alone in feeling this way.""",
            
            "executive_summary": """VERDICT: Case dismissed due to lack of evidence!

The court finds that your worry about starting a new school year, while understandable, is based on worst-case scenarios rather than reality. 

ACTION ITEM: Take one small social step each day - start with a simple greeting, then gradually build up to longer conversations. Focus on being yourself rather than trying to fit into any particular group.

REASSURANCE: You have successfully navigated social situations before, and you will do so again. The new school year is an opportunity, not a threat.""",
        }
        
        # Transform into Ace Attorney style dialogue
        dialogue_sequence = create_ace_attorney_dialogue(
            test_responses["original_worry"], 
            test_responses
        )
        
        # Create the visual novel response
        return VisualNovelResponse(
            original_worry=test_responses["original_worry"],
            dialogue_sequence=dialogue_sequence,
            metadata={
                "workflow_completed": True,
                "agent_sequence": ["prosecutor", "defense", "judge"],
                "style": "ace_attorney_visual_novel",
                "sprite_count": len(dialogue_sequence),
                "processing_notes": "TEST MODE - Pre-made responses for interface testing"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating test dialogue: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "Worry Butler - Ace Attorney Style Visual Novel API",
        "version": "2.0.0",
        "butler_initialized": butler is not None,
        "style": "ace_attorney_visual_novel"
    }

@app.get("/provider-info")
async def get_provider_info():
    """
    Get information about the current AI provider configuration.
    """
    try:
        if not butler:
            raise HTTPException(status_code=500, detail="Worry Butler not initialized")
        
        return butler.get_provider_info()
    except Exception as e:
        print(f"❌ Error in provider-info endpoint: {e}")
        print(f"❌ Error type: {type(e)}")
        print(f"❌ Butler status: {butler is not None}")
        raise HTTPException(status_code=500, detail=f"Error getting provider info: {str(e)}")

@app.get("/sprites")
async def get_sprite_info():
    """
    Get information about available sprites and backgrounds.
    """
    sprite_selector = SpriteSelector()
    
    return {
        "characters": {
            "prosecutor": {
                "name": "Enemy Prosecutor (Overthinker)",
                "sprites": sprite_selector.prosecutor_sprites,
                "animation_sequences": {
                    "angry": sprite_selector.get_animation_sequence("prosecutor", "angry"),
                    "smug": sprite_selector.get_animation_sequence("prosecutor", "smug"),
                    "worried": sprite_selector.get_animation_sequence("prosecutor", "worried"),
                    "dramatic": sprite_selector.get_animation_sequence("prosecutor", "dramatic"),
                    "intense": sprite_selector.get_animation_sequence("prosecutor", "intense"),
                    "default": sprite_selector.get_animation_sequence("prosecutor", "default")
                },
                "background": sprite_selector.backgrounds["prosecutor"]
            },
            "defense": {
                "name": "Maya Fey Defense (Therapist)", 
                "sprites": sprite_selector.defense_sprites,
                "animation_sequences": {
                    "calm": sprite_selector.get_animation_sequence("defense", "calm"),
                    "cheerful": sprite_selector.get_animation_sequence("defense", "cheerful"),
                    "reassuring": sprite_selector.get_animation_sequence("defense", "reassuring"),
                    "confident": sprite_selector.get_animation_sequence("defense", "confident"),
                    "gentle": sprite_selector.get_animation_sequence("defense", "gentle"),
                    "default": sprite_selector.get_animation_sequence("defense", "default")
                },
                "background": sprite_selector.backgrounds["defense"]
            },
            "judge": {
                "name": "Judge (Executive)",
                "sprites": sprite_selector.judge_sprites,
                "animation_sequences": {
                    "neutral": sprite_selector.get_animation_sequence("judge", "neutral"),
                    "speaking": sprite_selector.get_animation_sequence("judge", "speaking"),
                    "serious": sprite_selector.get_animation_sequence("judge", "serious"),
                    "thoughtful": sprite_selector.get_animation_sequence("judge", "thoughtful"),
                    "decisive": sprite_selector.get_animation_sequence("judge", "decisive"),
                    "default": sprite_selector.get_animation_sequence("judge", "default")
                },
                "background": sprite_selector.backgrounds["judge"]
            }
        },
        "total_sprites": len(sprite_selector.prosecutor_sprites) + 
                        len(sprite_selector.defense_sprites) + 
                        len(sprite_selector.judge_sprites),
        "backgrounds": sprite_selector.backgrounds,
        "features": {
            "animation_support": True,
            "multiple_variants": True,
            "emotion_detection": True,
            "click_to_advance": True,
            "auto_play": True
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    # Check configuration
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if openai_key:
        print("🔧 Using OpenAI API")
        print("💡 OpenAI API key found")
    else:
        print("🔧 Using Ollama (open-source models)")
        print("💡 Make sure Ollama is running: ollama serve")
        print("💡 Check if your model is available: ollama list")
    
    print("🏛️ Starting Worry Butler - Ace Attorney Style Visual Novel API...")
    print("🌐 Web interface available at: http://localhost:8000")
    print("📚 API documentation available at: http://localhost:8000/docs")
    print("🎭 Characters: Prosecutor (Overthinker), Defense (Therapist), Judge (Executive)")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
