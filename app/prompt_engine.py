# app/prompt_engine.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple
import random
import re


# -----------------------------
# Romantic Kitchen: Music-only prompt generator (Suno-ready)
# -----------------------------

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


DEFAULT_INSTRUMENTS = "soft upright piano, brush drums, warm upright bass"
DEFAULT_RHYTHM = "gentle swing rhythm"
DEFAULT_TEXTURE = "intimate, cozy, warm"


# 키워드 → (scene, mood, purpose, bpm_range)
KEYWORD_MAP: Dict[str, Tuple[str, str, str, Tuple[int, int]]] = {
    "비": ("Rainy Evening Kitchen", "nostalgic warm", "Dinner Prep", (70, 74)),
    "햇살": ("Sunlit Kitchen Afternoon", "bright warm", "Cooking", (76, 80)),
    "와인": ("Candlelit Kitchen Night", "romantic tender", "Wine Time", (72, 76)),
    "파스타": ("Sunday Brunch Kitchen", "light romantic", "Brunch", (78, 82)),
    "버터": ("Sunlit Kitchen", "dreamy warm", "Cooking", (76, 80)),
    "커피": ("Morning Coffee Kitchen", "soft bright", "Morning Coffee", (78, 82)),
    "초콜릿": ("Late Night Dessert Kitchen", "sweet cozy", "Late Night Dessert", (72, 78)),
    "바질": ("Fresh Kitchen Afternoon", "fresh warm", "Cooking", (76, 82)),
    "빵": ("Warm Oven Kitchen", "homey warm", "Brunch", (74, 80)),
    "레몬": ("Bright Kitchen Morning", "clean bright", "Morning Coffee", (78, 82)),
}

# 영상/카메라 용어 자동 제거(혹시 keyword에 섞여도 방어)
VIDEO_WORDS = re.compile(
    r"\b(cinematic|lighting|35mm|close-up|rack focus|dolly|camera|shot|scene)\b",
    re.IGNORECASE,
)


def _sanitize_keyword(keyword: str) -> str:
    k = (keyword or "").strip()
    k = VIDEO_WORDS.sub("", k).strip()
    return k if k else "kitchen"


def _pick_bpm(rng: Tuple[int, int], i: int) -> int:
    lo, hi = rng
    # 12개 후보에서 BPM 분산(너무 단조롭지 않게)
    steps = [0, 1, 2, 3, 4, 2, 1, 3, 0, 4, 1, 2]
    base = lo + (i % max(1, hi - lo + 1))
    bpm = min(hi, max(lo, base + steps[i % len(steps)]))
    return bpm


def build_music_prompt(spec: PromptSpec) -> str:
    # Suno에 바로 붙여넣는 음악 디렉션 (시각 단어 없음)
    return (
        "Romantic kitchen jazz instrumental.\n"
        f"Scene: {spec.scene}.\n"
        f"Mood: {spec.mood}.\n"
        f"Instruments: {spec.instruments}.\n"
        f"Rhythm: {spec.rhythm}.\n"
        f"Tempo: BPM {spec.bpm}.\n"
        f"Texture: {spec.texture}.\n"
        "No sudden dynamic changes.\n"
        "No aggressive drums.\n"
        "No harsh high frequencies.\n"
        "Keep it smooth, background-friendly, and consistent."
    )


def generate_prompt_pack(
    keyword: str,
    scene: str | None = None,
    mood: str | None = None,
    purpose: str | None = None,
    tempo: str | None = None,
    count: int = 12,
) -> List[str]:
    """
    returns: list[str] length=count (music-only prompts for Suno)
    """
    k = _sanitize_keyword(keyword)

    # default mapping
    default_scene, default_mood, default_purpose, bpm_rng = KEYWORD_MAP.get(
        k, ("Sunlit Kitchen", "warm romantic", "Cooking", (72, 80))
    )

    final_scene = (scene or default_scene).strip() if scene else default_scene
    final_mood = (mood or default_mood).strip() if mood else default_mood
    final_purpose = (purpose or default_purpose).strip() if purpose else default_purpose

    # tempo select override (e.g., "70~80", "72-76", "76-80")
    if tempo:
        t = tempo.replace("~", "-").replace("–", "-").strip()
        m = re.findall(r"\d+", t)
        if len(m) >= 2:
            lo, hi = int(m[0]), int(m[1])
            if lo <= hi:
                bpm_rng = (lo, hi)

    prompts: List[str] = []
    for i in range(count):
        bpm = _pick_bpm(bpm_rng, i)
        # slight variation
        textures = [
            "intimate, cozy, warm",
            "soft, airy, warm",
            "cozy, homey, gentle",
            "warm, romantic, tender",
        ]
        rhythms = ["gentle swing rhythm", "soft laid-back groove", "subtle swing, steady pulse"]
        instruments = [
            "soft upright piano, brush drums, warm upright bass",
            "warm piano, light brush drums, mellow upright bass",
            "soft piano, gentle brushes, airy bass",
        ]

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
    scene=None,
    mood=None,
    purpose=None,
    tempo=None,
    count: int = 12,
):
    return generate_prompt_pack(
        keyword=keyword,
        scene=scene,
        mood=mood,
        purpose=purpose,
        tempo=tempo,
        count=count,
    )

