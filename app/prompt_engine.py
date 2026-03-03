# app/prompt_engine.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple
import re

@dataclass(frozen=True)
class PromptSpec:
    keyword: str
    scene: str
    mood: str
    purpose: str
    bpm: int
    instruments: str
    rhythm: str
    texture: str

# 키워드 → (scene, mood, purpose, bpm_range)
KEYWORD_MAP: Dict[str, Tuple[str, str, str, Tuple[int, int]]] = {
    "비": ("Rainy Window Evening", "nostalgic warm", "Relax", (60, 66)),
    "햇살": ("Sunlit Room Afternoon", "bright warm", "Focus", (64, 72)),
    "와인": ("Candlelit Evening", "romantic tender", "Relax", (60, 68)),
    "파스타": ("Quiet Dinner Prep", "warm romantic", "Focus", (62, 70)),
    "커피": ("Morning Light", "soft bright", "Focus", (66, 74)),
}

# 촬영 기술 용어만 제거 (cinematic은 유지)
VIDEO_WORDS = re.compile(
    r"\b(lighting|35mm|close-up|rack focus|dolly|camera|shot)\b",
    re.IGNORECASE,
)

def _sanitize_keyword(keyword: str) -> str:
    k = (keyword or "").strip()
    k = VIDEO_WORDS.sub("", k).strip()
    return k if k else "moment"

def _pick_bpm(rng: Tuple[int, int], i: int) -> int:
    lo, hi = rng
    span = max(1, hi - lo)
    return lo + (i % (span + 1))

def build_music_prompt(spec: PromptSpec) -> str:
    return (
        "Cinematic romantic classical instrumental.\n"
        f"Scene: {spec.scene}.\n"
        f"Mood: {spec.mood}.\n"
        f"Purpose: {spec.purpose}.\n"
        f"Instruments: {spec.instruments}.\n"
        f"Rhythm: {spec.rhythm}.\n"
        f"Tempo: BPM {spec.bpm}.\n"
        f"Texture: {spec.texture}.\n"
        "No sudden dynamic changes.\n"
        "No aggressive percussion.\n"
        "No harsh high frequencies.\n"
        "No swing, no jazz, no cafe vibe.\n"
        "Keep it intimate, warm, and emotionally cinematic (end-credit feeling)."
    )

def generate_prompt_pack(
    keyword: str,
    scene: str | None = None,
    mood: str | None = None,
    purpose: str | None = None,
    tempo: str | None = None,
    count: int = 12,
) -> List[str]:
    k = _sanitize_keyword(keyword)

    default_scene, default_mood, default_purpose, bpm_rng = KEYWORD_MAP.get(
        k, ("Quiet Room", "warm nostalgic", "Relax", (60, 70))
    )

    final_scene = (scene or default_scene).strip() if scene else default_scene
    final_mood = (mood or default_mood).strip() if mood else default_mood
    final_purpose = (purpose or default_purpose).strip() if purpose else default_purpose

    if tempo:
        t = tempo.replace("~", "-").replace("–", "-").strip()
        m = re.findall(r"\d+", t)
        if len(m) >= 2:
            lo, hi = int(m[0]), int(m[1])
            if lo <= hi:
                bpm_rng = (lo, hi)

    textures = [
        "warm, intimate, nostalgic",
        "soft, airy, cinematic",
        "quiet, tender, end-credit mood",
        "minimal, calm, romantic",
    ]
    rhythms = [
        "steady gentle pulse, no swing",
        "slow flowing rhythm, no swing",
        "calm sustained motion, no swing",
    ]
    instruments = [
        "intimate piano, soft strings, subtle pad",
        "piano melody with warm strings, minimal percussion",
        "soft felt piano, gentle strings, ambient pad",
    ]

    prompts: List[str] = []
    for i in range(count):
        bpm = _pick_bpm(bpm_rng, i)
        spec = PromptSpec(
            keyword=k,
            scene=final_scene,
            mood=final_mood,
            purpose=final_purpose,
            bpm=bpm,
            instruments=instruments[i % len(instruments)],
            rhythm=rhythms[i % len(rhythms)],
            texture=textures[i % len(textures)],
        )
        prompts.append(build_music_prompt(spec))

    return prompts

# Backward-compat for existing main.py import
def generate_prompt_candidates(
    keyword: str,
    total: int = 12,
    scene=None,
    mood=None,
    purpose=None,
    tempo=None,
):
    return generate_prompt_pack(
        keyword=keyword,
        scene=scene,
        mood=mood,
        purpose=purpose,
        tempo=tempo,
        count=total,
    )
