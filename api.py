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
    position: str = "center"  # left | right | center
    description: str = "A single line of dialogue with character, sprite, background, and position"

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
        # Map to actual available files
        self.prosecutor_sprites = {
            "angry": ["prosecutor.gif"],
            "smug": ["prosecutor.gif"],
            "worried": ["prosecutor.gif"],
            "dramatic": ["prosecutor.gif"],
            "intense": ["prosecutor.gif"],
            "default": ["prosecutor.gif"]
        }
        
        # Defense (Therapist) sprites - calm and supportive
        self.defense_sprites = {
            "calm": ["defense.gif"],
            "cheerful": ["defense.gif"],
            "reassuring": ["defense.gif"],
            "confident": ["defense.gif"],
            "gentle": ["defense.gif"],
            "default": ["defense.gif"]
        }
        
        # Judge sprites - authoritative and wise
        self.judge_sprites = {
            "neutral": ["judge.gif"],
            "speaking": ["judge.gif"],
            "serious": ["judge.gif"],
            "thoughtful": ["judge.gif"],
            "decisive": ["judge.gif"],
            "default": ["judgestand.png"]
        }
        
        # Background images for each character
        # Use actual available background images for left/right; judge uses style class
        self.backgrounds = {
            "prosecutor_left": "left.jpg",
            "prosecutor_right": "right.jpg",
            "defense_left": "left.jpg",
            "defense_right": "right.jpg",
            "judge": "judge"  # keyword so UI applies judge-bg gradient
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
    
    # Alternate positions for prosecutor/defense
    prosecutor_position = 'left'
    defense_position = 'right'

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
        background=sprite_selector.backgrounds[f"prosecutor_{prosecutor_position}"],
        position=prosecutor_position,
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
        background=sprite_selector.backgrounds[f"defense_{defense_position}"],
        position=defense_position,
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
        position='center',
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
        <title>Worry Butler - Ace Attorney Style Visual Novel 🏛️⚖️</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Crimson+Text:wght@400;600;700&display=swap');
            * { box-sizing: border-box; }
            body {
                font-family: 'Crimson Text', serif;
                margin: 0; padding: 0; background: #000; color: white;
                overflow: hidden; user-select: none;
            }
            .game-container { position: relative; width: 100vw; height: 100vh; background: #000; overflow: hidden; }
            /* Background System */
            .background-layer { position: absolute; top:0; left:0; width:100%; height:100%; z-index:1; transition: opacity 0.8s ease-in-out; }
            .courtroom-bg { background: linear-gradient(135deg, #2c1810 0%, #4a3728 25%, #3d2b1f 50%, #2c1810 75%, #1a1a1a 100%); }
            .prosecutor-bg { background: linear-gradient(135deg, #8b0000 0%, #dc143c 25%, #b22222 50%, #8b0000 75%, #2c0e0e 100%); }
            .defense-bg { background: linear-gradient(135deg, #000080 0%, #4169e1 25%, #1e90ff 50%, #000080 75%, #0e0e2c 100%); }
            .judge-bg { background: linear-gradient(135deg, #8b4513 0%, #daa520 25%, #b8860b 50%, #8b4513 75%, #2c1e0e 100%); }
            .background-layer::before {
                content:''; position:absolute; top:0; left:0; width:100%; height:100%;
                background: radial-gradient(circle at 20% 50%, rgba(255,255,255,0.03) 1px, transparent 1px),
                            radial-gradient(circle at 80% 50%, rgba(255,255,255,0.03) 1px, transparent 1px),
                            radial-gradient(circle at 40% 20%, rgba(255,255,255,0.02) 1px, transparent 1px);
                background-size: 50px 50px, 70px 70px, 30px 30px; opacity: 0.8;
            }
            /* Character Sprite System */
            .character-container { position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); width:100%; height:100%; z-index:2; display:flex; justify-content:center; align-items:center; transition:justify-content 0.3s ease, padding 0.3s ease; }
            .character-container.align-left { justify-content:center; padding-left:0; }
            .character-container.align-right { justify-content:center; padding-right:0; }
            .character-container.align-center { justify-content:center; padding:0; }
            .character-sprite { height:70vh; width:auto; max-width:90vw; object-fit:contain; filter:drop-shadow(0 20px 40px rgba(0,0,0,0.8)); transition:all 0.4s cubic-bezier(0.68,-0.55,0.265,1.55); }
            .sprite-animation { animation: spriteAppear 0.6s cubic-bezier(0.68,-0.55,0.265,1.55); }
            @keyframes spriteAppear { 0%{ transform: translateY(100px) scale(0.8); opacity:0; filter: drop-shadow(0 20px 40px rgba(0,0,0,0.8)) blur(2px);} 50%{ transform: translateY(-10px) scale(1.02); opacity:0.8; filter: drop-shadow(0 25px 50px rgba(0,0,0,0.9)) blur(1px);} 100%{ transform: translateY(0) scale(1); opacity:1; filter: drop-shadow(0 20px 40px rgba(0,0,0,0.8)) blur(0);} }
            .sprite-pulse { animation: spritePulse 0.3s ease-in-out; }
            @keyframes spritePulse { 0%,100%{ transform:scale(1);} 50%{ transform:scale(1.02);} }
            /* Text Box */
            .text-box-container { position:absolute; bottom:0; left:0; width:100%; height:35%; z-index:3; }
            .text-box { position:relative; width:100%; height:100%; background: linear-gradient(180deg, rgba(0,0,0,0.95) 0%, rgba(20,20,20,0.98) 100%); border-top:4px solid #ffd700; box-shadow: 0 -10px 30px rgba(0,0,0,0.8), inset 0 4px 10px rgba(255,215,0,0.1); }
            .text-box::before { content:''; position:absolute; top:0; left:0; width:100%; height:2px; background: linear-gradient(90deg, transparent 0%, #ffd700 20%, #ffed4e 50%, #ffd700 80%, transparent 100%); animation: shimmer 3s ease-in-out infinite; }
            @keyframes shimmer { 0%,100%{opacity:0.6;} 50%{opacity:1;} }
            .character-nameplate { position:absolute; top:15px; left:30px; background: linear-gradient(135deg, #ffd700, #ffed4e); color:#000; padding:8px 20px; border-radius:20px; font-weight:700; font-size:16px; text-transform:uppercase; letter-spacing:2px; box-shadow: 0 4px 15px rgba(255,215,0,0.4), inset 0 2px 5px rgba(255,255,255,0.3); transform:translateY(-50%); border:2px solid #e6c200; }
            .dialogue-text-area { padding:60px 40px 40px 40px; height:100%; display:flex; align-items:flex-start; justify-content:flex-start; }
            .dialogue-text { font-size:20px; line-height:1.6; color:#fff; text-shadow:2px 2px 4px rgba(0,0,0,0.8); max-height:calc(100% - 20px); overflow-y:auto; padding-right:20px; letter-spacing:0.5px; }
            .dialogue-text::-webkit-scrollbar{ width:8px; } .dialogue-text::-webkit-scrollbar-track{ background:rgba(255,215,0,0.1); border-radius:4px;} .dialogue-text::-webkit-scrollbar-thumb{ background:linear-gradient(180deg,#ffd700,#e6c200); border-radius:4px; box-shadow:0 2px 5px rgba(0,0,0,0.3);} 
            .text-continue-indicator { position:absolute; bottom:15px; right:30px; color:#ffd700; font-size:14px; animation: blink 1.5s infinite; font-weight:600; }
            @keyframes blink { 0%,50%{opacity:1;} 51%,100%{opacity:0.3;} }
            /* UI Controls */
            .ui-controls { position:absolute; top:20px; right:20px; z-index:5; display:flex; gap:10px; }
            .control-button { background: linear-gradient(135deg, rgba(255,215,0,0.9), rgba(230,194,0,0.9)); border:2px solid #ffd700; border-radius:25px; color:#000; padding:10px 18px; cursor:pointer; font-size:12px; font-weight:700; transition:all 0.3s cubic-bezier(0.25,0.46,0.45,0.94); text-transform:uppercase; letter-spacing:1px; box-shadow:0 4px 15px rgba(255,215,0,0.3); }
            .control-button:hover { transform: translateY(-2px); box-shadow:0 6px 20px rgba(255,215,0,0.5); background: linear-gradient(135deg, #ffd700, #ffed4e); }
            .control-button:active { transform: translateY(0); }
            .control-button.active { background: linear-gradient(135deg, #ff6b6b, #ee5a24); border-color:#ff6b6b; color:white; }
            /* Progress */
            .progress-container { position:absolute; top:20px; left:20px; z-index:5; background: rgba(0,0,0,0.8); padding:15px 20px; border-radius:15px; border:2px solid #ffd700; min-width:250px; }
            .progress-label { font-size:12px; color:#ffd700; margin-bottom:8px; text-transform:uppercase; letter-spacing:1px; font-weight:600; }
            .progress-bar { width:100%; height:8px; background: rgba(255,215,0,0.2); border-radius:4px; overflow:hidden; }
            .progress-fill { height:100%; background: linear-gradient(90deg, #ffd700, #ffed4e, #ffd700); background-size:200% 100%; animation: progressShine 2s ease-in-out infinite; transition: width 0.6s cubic-bezier(0.25,0.46,0.45,0.94); border-radius:4px; width:0%; }
            @keyframes progressShine { 0%{background-position:-200% 0;} 100%{background-position:200% 0;} }
            /* Test Overlay */
            .test-overlay { position:absolute; bottom:40%; left:20px; z-index:4; background: rgba(0,100,0,0.9); color:#00ff00; padding:20px; border-radius:15px; border:2px solid #00ff00; max-width:320px; font-size:13px; box-shadow:0 10px 30px rgba(0,100,0,0.3); }
            .test-overlay h3 { margin:0 0 12px 0; font-size:16px; text-transform:uppercase; letter-spacing:2px; }
            .test-overlay p { margin:8px 0; line-height:1.4; }
            .test-overlay strong { color:#7fff00; }
            /* Sound Effect Indicators */
            .sound-effect { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); z-index:6; pointer-events:none; font-size:24px; color:#ffd700; font-weight:bold; text-shadow:2px 2px 4px rgba(0,0,0,0.8); animation: soundPop 0.8s ease-out forwards; }
            @keyframes soundPop { 0%{ transform:translate(-50%,-50%) scale(0.5); opacity:0;} 30%{ transform:translate(-50%,-50%) scale(1.2); opacity:1;} 100%{ transform:translate(-50%,-50%) scale(1); opacity:0;} }
            /* Loading overlay */
            .loading-overlay { position:absolute; inset:0; display:none; align-items:center; justify-content:center; background:rgba(0,0,0,0.6); z-index:10; }
            .loading-overlay.active { display:flex; }
            .spinner { width:56px; height:56px; border:6px solid rgba(255,215,0,0.25); border-top-color:#ffd700; border-radius:50%; animation: spin 1s linear infinite; box-shadow:0 0 20px rgba(255,215,0,0.4); }
            @keyframes spin { to { transform: rotate(360deg);} }
            .control-button:disabled { opacity:0.5; cursor:not-allowed; filter:grayscale(30%); }
            .text-continue-indicator.loading { opacity:0.7; animation: none; }
        </style>
    </head>
    <body>
        <div class="game-container" id="gameContainer">
            <div id="backgroundLayer" class="background-layer courtroom-bg"></div>
            <div id="characterContainer" class="character-container align-center">
                <img id="characterSprite" class="character-sprite" alt="Character Sprite" src="/static/judge.gif">
            </div>
            <div class="text-box-container">
                <div class="text-box">
                    <div id="characterNameplate" class="character-nameplate">JUDGE</div>
                    <div class="dialogue-text-area">
                        <div id="dialogueText" class="dialogue-text">Welcome to the Worry Butler courtroom! Click anywhere to begin the trial...</div>
                    </div>
                    <div id="continueIndicator" class="text-continue-indicator">▶ Click to continue</div>
                </div>
            </div>
            <div class="ui-controls">
                <button class="control-button" id="skipBtn">⏭ Skip</button>
                <button id="autoButton" class="control-button">▶ Auto</button>
                <button class="control-button" id="resetBtn">🔄 Reset</button>
            </div>
            <div class="progress-container">
                <div class="progress-label">Trial Progress</div>
                <div class="progress-bar"><div id="progressFill" class="progress-fill"></div></div>
            </div>
            <div class="test-overlay">
                <h3>🧪 Test Mode Active</h3>
                <p><strong>Enhanced Ace Attorney Style!</strong></p>
                <p>• Character sprite with animations</p>
                <p>• Authentic text box styling</p>
                <p>• Dynamic backgrounds per character</p>
                <p>• Sound effect indicators</p>
                <p><strong>Click anywhere to advance dialogue!</strong></p>
            </div>
            <div id="loadingOverlay" class="loading-overlay"><div class="spinner" aria-label="Loading"></div></div>
        </div>
        <script>
            // Will be filled from API
            let dialogue = [];
            let idx = -1; let autoMode = false; let autoTimer = null;
            let isLoading = false;
            const nameplate = document.getElementById('characterNameplate');
            const dialogueText = document.getElementById('dialogueText');
            const spriteEl = document.getElementById('characterSprite');
            const characterContainer = document.getElementById('characterContainer');
            const bgLayer = document.getElementById('backgroundLayer');
            const progressFill = document.getElementById('progressFill');
            const autoBtn = document.getElementById('autoButton');
            const game = document.getElementById('gameContainer');
            const skipBtn = document.getElementById('skipBtn');
            const resetBtn = document.getElementById('resetBtn');
            const loadingOverlay = document.getElementById('loadingOverlay');
            const continueIndicator = document.getElementById('continueIndicator');

            function setBackgroundClass(filenameOrHint) {
                const hint = (filenameOrHint || '').toLowerCase();
                // If it's an image filename, use it directly
                if (/(\.jpg|\.jpeg|\.png|\.gif)$/i.test(hint)) {
                    let path = hint.startsWith('/static/') ? hint : `/static/${hint}`;
                    bgLayer.style.backgroundImage = `url('${path}')`;
                    bgLayer.style.backgroundSize = 'cover';
                    bgLayer.style.backgroundPosition = 'center';
                    bgLayer.className = 'background-layer'; // remove gradient classes
                    return;
                }
                // Otherwise, use gradient classes by role keyword
                let cls = 'courtroom-bg';
                if (hint.includes('prosecutor')) cls = 'prosecutor-bg';
                else if (hint.includes('defense')) cls = 'defense-bg';
                else if (hint.includes('judge')) cls = 'judge-bg';
                bgLayer.style.backgroundImage = '';
                bgLayer.className = `background-layer ${cls}`;
            }
            function playSfxIndicator(kind) {
                if (!kind) return; const el = document.createElement('div'); el.className='sound-effect';
                el.textContent = ({ gavel:'Gavel!⚖️', objection:'Objection!', 'hold-it':'Hold it!' }[kind] || 'SFX');
                document.body.appendChild(el); setTimeout(()=>el.remove(), 800);
            }
            function updateProgress() {
                const pct = Math.max(0, Math.min(100, Math.round(((idx + 1) / (dialogue.length||1)) * 100)));
                progressFill.style.width = pct + '%';
            }
            function render() {
                const node = dialogue[idx]; if (!node) return;
                nameplate.textContent = node.character || '';
                dialogueText.textContent = node.text || '';
                setBackgroundClass(node.background || node.bg || '');
                // Align character by position
                const pos = (node.position || 'center');
                characterContainer.classList.remove('align-left','align-right','align-center');
                if (pos === 'left') characterContainer.classList.add('align-left');
                else if (pos === 'right') characterContainer.classList.add('align-right');
                else characterContainer.classList.add('align-center');
                let spritePath = node.sprite || '';
                if (spritePath && !spritePath.startsWith('/static/')) spritePath = '/static/' + spritePath;
                if (spritePath) {
                    spriteEl.onerror = function() {
                        console.warn('Failed to load sprite:', spritePath);
                        // Fallback to judgestand.png if sprite fails to load
                        if (this.src !== '/static/judgestand.png') {
                            this.src = '/static/judgestand.png';
                        }
                    };
                    spriteEl.src = spritePath;
                }
                spriteEl.classList.remove('sprite-animation'); void spriteEl.offsetWidth; spriteEl.classList.add('sprite-animation');
                playSfxIndicator(node.character === 'JUDGE' ? 'gavel' : node.character === 'PROSECUTOR' ? 'objection' : 'hold-it');
                updateProgress();
            }
            function next() {
                if (isLoading) return;
                if (idx < dialogue.length - 1) { idx += 1; render(); if (autoMode) scheduleAuto(); }
                else { autoOff(); continueIndicator.textContent = 'End of trial'; }
            }
            function scheduleAuto() { clearTimeout(autoTimer); autoTimer = setTimeout(next, 2400); }
            function autoOn() { autoMode = true; autoBtn.classList.add('active'); scheduleAuto(); }
            function autoOff() { autoMode = false; autoBtn.classList.remove('active'); clearTimeout(autoTimer); }
            function toggleAuto() { autoMode ? autoOff() : autoOn(); }
            function skipDialogue() { if (dialogue.length>0){ idx = dialogue.length - 2; next(); }}
            function resetTrial() { autoOff(); idx = -1; document.getElementById('continueIndicator').textContent = '▶ Click to continue'; fetchAndStart(true); }

            function setLoading(on) {
                isLoading = !!on;
                loadingOverlay.classList.toggle('active', isLoading);
                autoBtn.disabled = isLoading;
                skipBtn.disabled = isLoading;
                resetBtn.disabled = isLoading;
                if (isLoading) {
                    continueIndicator.textContent = 'Processing...';
                    continueIndicator.classList.add('loading');
                } else {
                    continueIndicator.textContent = (idx < dialogue.length - 1 || dialogue.length === 0) ? '▶ Click to continue' : 'End of trial';
                    continueIndicator.classList.remove('loading');
                }
            }

            async function fetchAndStart(resetOnly=false) {
                try {
                    if (!resetOnly && dialogue.length === 0 && idx === -1) {
                        // First click: ask for worry
                        const worry = window.prompt("What's worrying you today?");
                        if (!worry) return;
                        setLoading(true);
                        const resp = await fetch('/process-worry', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ worry }) });
                        if (!resp.ok) throw new Error('HTTP '+resp.status);
                        const data = await resp.json();
                        dialogue = (data.dialogue_sequence || []).map(d => ({
                            character: d.character,
                            text: d.text,
                            sprite: d.sprite,
                            background: d.background,
                            position: d.position || 'center'
                        }));
                    }
                    if (dialogue.length > 0) next();
                } catch (e) {
                    console.error('Fetch error', e);
                    dialogue = [
                        { character:'JUDGE', text:'Service unavailable. Please check model provider and try again.', sprite:'judge.gif', background:'judge', position:'center' }
                    ];
                    next();
                } finally {
                    setLoading(false);
                }
            }

            // Wire events
            game.addEventListener('click', () => { if (!autoMode && !isLoading) fetchAndStart(); });
            autoBtn.addEventListener('click', (e) => { e.stopPropagation(); toggleAuto(); });
            skipBtn.addEventListener('click', (e) => { e.stopPropagation(); if (!isLoading) skipDialogue(); });
            resetBtn.addEventListener('click', (e) => { e.stopPropagation(); if (!isLoading) resetTrial(); });
            document.addEventListener('keydown', (e) => { if (e.key===' '||e.key==='Enter'){ e.preventDefault(); if (!autoMode && !isLoading) fetchAndStart(); }});

            // Start with the welcome line active
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

@app.get("/test-sprites")
async def test_sprites():
    """Test endpoint to verify sprite files are accessible."""
    import os
    sprite_dir = "worry_butler/sprites"
    if not os.path.exists(sprite_dir):
        return {"error": "Sprite directory not found", "path": sprite_dir}
    
    files = os.listdir(sprite_dir)
    return {
        "sprite_directory": sprite_dir,
        "available_files": files,
        "test_urls": {
            "judge": "/static/judge.gif",
            "prosecutor": "/static/prosecutor.gif", 
            "defense": "/static/defense.gif",
            "judgestand": "/static/judgestand.png",
            "left_bg": "/static/left.jpg",
            "right_bg": "/static/right.jpg"
        }
    }

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
