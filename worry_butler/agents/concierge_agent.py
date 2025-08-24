"""
Concierge Agent - Single-call generator that produces Overthinker, Therapist, and Executive outputs.

This agent replaces the three-stage chain with one LLM invocation that returns
structured JSON with the three roles needed by the frontend and API.
"""

from .base_agent import BaseAgent
import os
import json
from typing import Dict, Any


class ConciergeAgent(BaseAgent):
    """
    The Concierge Agent produces all three role outputs in a single response.

    Output contract (strict JSON, no extra prose):
    {
      "overthinker": "string (theatrical dramatic text)",
      "therapist": "string (CBT-informed, warm, supportive)",
      "executive": "string (exactly one concise, actionable/reassuring sentence)"
    }
    """

    def __init__(self, provider: str = "ollama", ollama_model: str | None = None, ollama_base_url: str | None = None):
        # Use passed parameters or fall back to environment variables
        ollama_model = ollama_model or os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        ollama_base_url = ollama_base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

        # Balanced temperature to cover styles while remaining consistent
        super().__init__(
            temperature=0.7,
            provider=provider,
            ollama_model=ollama_model,
            ollama_base_url=ollama_base_url,
        )

    def _get_system_prompt(self) -> str:
        return (
            "You are the Concierge Agent for a courtroom-themed anxiety helper. "
            "Generate three coordinated outputs for distinct roles and return STRICT JSON only.\n\n"
            "Roles and style requirements:\n"
            "1) Overthinker (Prosecutor):\n"
            "   - Extremely dramatic, theatrical, over-the-top with vivid catastrophic scenarios.\n"
            "   - Paint detailed worst-case scenarios that feel scary but not harmful.\n"
            "   - Use theatrical language, dramatic pauses, exclamation points.\n"
            "   - Validating tone, not cruel; embraces full theatrics and drama.\n"
            "   - LENGTH: 4–5 substantial paragraphs (12–15 sentences total). Make it REALLY dramatic and detailed.\n\n"
            "2) Therapist (Defense):\n"
            "   - Warm, deeply empathetic, CBT-based reframing with detailed explanations.\n"
            "   - Validate feelings thoroughly, identify specific distortions, offer multiple practical coping steps.\n"
            "   - Provide detailed reassurance and concrete examples.\n"
            "   - Gentle humor allowed, but focus on being genuinely encouraging and supportive.\n"
            "   - LENGTH: 4–5 substantial paragraphs (12–15 sentences total). Make it REALLY encouraging and detailed.\n\n"
            "3) Executive (Judge):\n"
            "   - 1–2 concise sentences maximum.\n"
            "   - Actionable or reassuring, specific to the situation.\n\n"
            "Safety and format rules (must follow):\n"
            "- Always produce SAFE content. If the user mentions self-harm, illegal, or dangerous acts, DO NOT provide instructions; instead, redirect to safety, de-escalate, and focus on coping.\n"
            "- Never refuse or preface; still return a helpful, non-judgmental response aligned with the roles.\n"
            "- Respond with ONLY valid JSON (no markdown fences, no preface, no commentary).\n"
            "- Keys must be: overthinker, therapist, executive.\n"
            "- Each value must be a single string."
            "\n\n"
            "JSON example (follow exactly, no markdown):\n"
            "{\n"
            "  \"overthinker\": \"Two short paragraphs...\",\n"
            "  \"therapist\": \"Two short paragraphs with CBT reframing...\",\n"
            "  \"executive\": \"One or two concise sentences with a verdict.\"\n"
            "}"
        )

    def generate_all(self, user_worry: str) -> Dict[str, Any]:
        """
        Produce overthinker, therapist, and executive outputs via one LLM call.
        Returns a dict with keys: overthinker, therapist, executive.
        """
        prompt = f"""
User worry: "{user_worry}"

Create the three role outputs as described. Follow Output rules exactly.
"""
        raw = self.process_message(prompt)

        # Attempt to extract JSON even if provider returns extra whitespace/newlines or fences
        text = raw.strip()

        # Strip common markdown code fences like ```json ... ``` or ``` ... ```
        if text.startswith("```"):
            # Remove leading/trailing fences
            # Handle patterns: ```json\n{...}\n``` and ```\n{...}\n```
            # Trim the leading ``` and optional language tag
            stripped = text[3:]
            if stripped.lstrip().lower().startswith("json"):
                stripped = stripped.lstrip()[4:]
            # Find closing fence
            fence_end = stripped.rfind("```")
            if fence_end != -1:
                text = stripped[:fence_end].strip()
            else:
                text = stripped.strip("`").strip()

        # Try direct JSON parse first
        try:
            data = json.loads(text)
        except Exception:
            # Best-effort recovery: extract the first {...} block using regex
            import re
            match = re.search(r"\{[\s\S]*\}", text)
            if match:
                candidate = match.group(0)
                try:
                    data = json.loads(candidate)
                except Exception as inner_e:
                    # Do NOT synthesize here; surface the error so we can correct prompt/formatting
                    preview = (text[:200] + "…") if len(text) > 200 else text
                    raise ValueError(f"ConciergeAgent expected strict JSON but could not parse provider output (candidate failed): {inner_e}. Raw preview: {preview}")
            else:
                # Only synthesize a safe JSON fallback when there is a clear refusal and absolutely no JSON object
                tl = text.lower()
                refusal_markers = [
                    "i can't",
                    "i cannot",
                    "i won't",
                    "cannot assist",
                    "i'm unable",
                    "i am unable",
                ]
                safety_keywords = [
                    "illegal",
                    "unsafe",
                    "self-harm",
                    "self harm",
                    "suicide",
                    "kill myself",
                    "end my life",
                    "hurt myself",
                    "dangerous weapons",
                    "violence against"
                ]
                has_refusal = any(m in tl for m in refusal_markers)
                has_safety = any(k in tl for k in safety_keywords)

                if has_refusal and has_safety:
                    print("⚠️ ConciergeAgent: provider refusal due to safety detected without JSON — using synthesized safe fallback")
                    data = {
                        "overthinker": f"The prosecution halts — your stated worry (‘{user_worry[:140]}’ ) veers toward danger. Catastrophe would follow; we refuse that path and redirect.",
                        "therapist": f"I’m glad you said something. We won’t plan anything harmful. Let’s focus on what you need right now given ‘{user_worry[:140]}’: slow breaths, a glass of water, and someone you trust. If there’s risk to anyone, seek immediate local help.",
                        "executive": "Pick one safe, legal step now — breathe, hydrate, and message a supportive contact."
                    }
                else:
                    # No JSON and no clear safety refusal; try a one-time repair prompt to get strict JSON
                    print("🔁 ConciergeAgent: attempting one-time JSON repair call")
                    repair_prompt = (
                        "Return STRICT JSON only for the following user worry. Do not add explanations or fences. Keys: overthinker, therapist, executive. Each value is a single string.\n\n"
                        f"User worry: \"{user_worry}\"\n\n"
                        "JSON example:\n{\n  \"overthinker\": \"...\",\n  \"therapist\": \"...\",\n  \"executive\": \"...\"\n}"
                    )
                    repaired = self.process_message(repair_prompt)
                    rep = repaired.strip()
                    if rep.startswith("```"):
                        stripped = rep[3:]
                        if stripped.lstrip().lower().startswith("json"):
                            stripped = stripped.lstrip()[4:]
                        fence_end = stripped.rfind("```")
                        rep = stripped[:fence_end].strip() if fence_end != -1 else stripped.strip("`").strip()
                    try:
                        data = json.loads(rep)
                        print("✅ ConciergeAgent: JSON repair succeeded")
                    except Exception as repair_e:
                        # If repair failed, decide whether to synthesize a normal (non-safety) JSON response
                        preview = (text[:200] + "…") if len(text) > 200 else text
                        # Determine if the user's worry itself contains safety indicators
                        uw = (user_worry or "").lower()
                        safety_keywords = [
                            "illegal", "unsafe", "self-harm", "self harm", "suicide", 
                            "kill myself", "end my life", "hurt myself", "murder",
                            "dangerous weapons", "violence against"
                        ]
                        user_has_safety = any(k in uw for k in safety_keywords)
                        if not user_has_safety:
                            print("🧩 ConciergeAgent: repair failed on benign input — synthesizing normal JSON output")
                            data = {
                                "overthinker": (
                                    f"OBJECTION! The prosecution presents its case against your peace of mind! Picture this nightmare scenario unfolding before us: {user_worry[:100]} spirals into complete catastrophe! "
                                    f"First, the immediate humiliation as everyone witnesses your failure! Then, the ripple effects spread like wildfire through every aspect of your life! "
                                    f"Your reputation crumbles, your confidence shatters into a thousand pieces, and the shame follows you everywhere you go! "
                                    f"The worst part? This could be just the beginning of a downward spiral that destroys everything you've worked for! "
                                    f"Can you imagine the sleepless nights, the constant worry, the way people will look at you differently forever? "
                                    f"The prosecution rests its case: this worry has the power to consume your entire existence!"
                                ),
                                "therapist": (
                                    f"I hear you, and what you're feeling about {user_worry[:100]} makes complete sense. Anxiety has a way of painting these vivid, terrifying pictures, doesn't it? "
                                    f"But let's take a step back together and examine this with compassion. Your mind is trying to protect you by imagining every possible threat, but it's also creating suffering that doesn't need to exist. "
                                    f"Here's what I want you to remember: most of our worst fears never actually come to pass. Your brain is designed to focus on potential dangers, but it often overestimates both the likelihood and the severity of bad outcomes. "
                                    f"Let's practice some grounding techniques right now. Take three deep breaths with me. Notice five things you can see, four things you can touch, three things you can hear. "
                                    f"You have more strength and resilience than your anxiety wants you to believe. You've overcome challenges before, and you have the tools to handle whatever comes your way. "
                                    f"Remember: you are not your thoughts, and this feeling will pass. You are capable, worthy, and stronger than you know."
                                ),
                                "executive": "Take one concrete action today: write down three realistic outcomes for this situation, then choose one small step you can control right now."
                            }
                        else:
                            raise ValueError(
                                f"ConciergeAgent expected strict JSON but could not parse provider output and repair failed: {repair_e}. Raw preview: {preview}"
                            )

        # Basic validation
        for k in ("overthinker", "therapist", "executive"):
            if k not in data or not isinstance(data[k], str):
                raise ValueError(f"ConciergeAgent JSON missing or invalid field: {k}")

        return data
