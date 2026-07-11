import json
import os
import shutil
import subprocess
import tempfile
import uuid

from fastapi import FastAPI, Form, UploadFile
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))


def call_claude_prompt(prompt: str, timeout: int = 300) -> str:
    """claude -p 구독 방식으로 프롬프트를 호출하고 result 텍스트만 반환한다."""
    if len(prompt.encode("utf-8")) > 8_000_000:
        tmp_path = os.path.join(tempfile.gettempdir(), f"amvg_{uuid.uuid4().hex}.txt")
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        prompt = f"Read the file at {tmp_path} and follow its instructions."

    claude_bin = shutil.which("claude")
    proc = subprocess.run(
        [claude_bin or "claude", "-p", prompt, "--output-format", "json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"claude -p failed: {proc.stderr[:500]}")

    data = json.loads(proc.stdout)
    if data.get("is_error"):
        raise RuntimeError(f"claude -p error: {data.get('result')}")
    return data["result"]


def extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def generate_storyline(lyrics: str, mood: str = "") -> dict:
    """가사와 분위기에서 뮤직비디오 전체 스토리라인 JSON을 만든다."""
    prompt = f"""You are an experienced AI music video director.
Read the song lyrics below and design the overall storyline for a music video.

Return ONLY valid JSON (no markdown fences, no commentary) with exactly these fields:
{{
  "concept": "one paragraph: the core concept of the music video",
  "theme": "the emotional/narrative theme in one sentence",
  "visual_style": "overall visual style, color palette, cinematography mood",
  "narrative_arc": "how the story moves from beginning to middle to end",
  "storyline": "a short story treatment describing what happens across the video"
}}

Mood/genre hints (optional, may be empty): {mood or "none provided"}

Lyrics:
{lyrics}
"""
    raw = call_claude_prompt(prompt)
    return extract_json(raw)


def generate_scenes(storyline: dict, lyrics: str, mood: str = "") -> list:
    """스토리라인을 노래 구간별 AI 뮤직비디오 씬 카드로 나눈다."""
    prompt = f"""You are an experienced AI music video director.
Break the following music video storyline into a sequence of scenes (shots),
aligned with the song's lyric segments (intro / verse / chorus / bridge / outro).

Storyline JSON:
{json.dumps(storyline, ensure_ascii=False)}

Mood/genre hints (optional, may be empty): {mood or "none provided"}

Full lyrics:
{lyrics}

For mise-en-scene, decide these six elements in order for every scene: objects, background,
colors, lighting, arrangement (characters/action), camera shot. Include at least one scene
where the main character is singing (has_singing: true) so the video feels alive — mark which
scenes those are and keep the original-language lyric line for that segment.

Return ONLY valid JSON (no markdown fences, no commentary): a JSON array of scene objects,
each with exactly these fields:
{{
  "scene_number": 1,
  "lyric_segment": "e.g. Verse 1",
  "shot_type": "e.g. wide shot / close-up / tracking shot",
  "setting": "location description",
  "characters": "who is in frame",
  "action": "what happens/moves in this scene",
  "objects": "key objects in frame",
  "background": "background description",
  "colors": "color palette for this scene",
  "lighting": "lighting description",
  "camera_movement": "how the camera moves",
  "mood": "emotional mood of this scene",
  "has_singing": true or false,
  "singing_lyrics": "original-language lyric line if has_singing is true, else empty string"
}}
"""
    raw = call_claude_prompt(prompt)
    return extract_json(raw)


def build_image_prompt(scene: dict, global_style: str = "") -> str:
    """씬 하나를 GPT이미지2/나노바나나2에 붙여넣을 영어 이미지 프롬프트로 바꾼다.
    순서: Background/scene -> Subject -> Key details -> Style -> Constraints.
    """
    background = f"{scene['setting']}, {scene['background']}."
    subject = f"{scene['characters']}: {scene['action']}."
    key_details = (
        f"Key details: {scene['objects']}, {scene['colors']} color palette, "
        f"{scene['lighting']} lighting, {scene['shot_type']}."
    )
    style_bits = [b for b in [global_style, scene.get("mood")] if b]
    style = f"Style: {', '.join(style_bits)}, cinematic film still."
    constraints = "Constraints: no text, no watermark, no subtitles, 16:9 cinematic frame."
    return " ".join([background, subject, key_details, style, constraints])


def build_video_prompt(scene: dict, target_model: str = "KLING", global_style: str = "") -> str:
    """씬 하나를 KLING/VEO3.1/GROK용 대사 없는 영어 영상 프롬프트로 바꾼다.
    순서: Scene -> Characters -> Action -> Camera -> Style. 모든 프롬프트에 대사 금지 문구를 넣는다.
    """
    scene_desc = (
        f"Scene: {scene['setting']}, {scene['background']}, "
        f"{scene['lighting']} lighting, {scene['colors']} color palette."
    )
    characters = f"Characters: {scene['characters']}."

    action_text = scene["action"].rstrip(".") + "."
    if scene.get("has_singing") and scene.get("singing_lyrics"):
        action_text += (
            f' The character lip-syncs to the original lyric line: "{scene["singing_lyrics"]}", '
            "natural mouth movement and emotive facial performance, no audible speech."
        )
    action_text += f" Hands and body stay anchored to {scene['objects']}, never floating in empty space."
    action = f"Action: {action_text}"

    camera = (
        f"Camera: {scene['camera_movement']}, {scene['shot_type']}, "
        "then naturally comes to a still pause at the end of the motion."
    )

    style_bits = [b for b in [global_style, scene.get("mood")] if b]
    style = f"Style: {', '.join(style_bits)}, cinematic, coherent motion for {target_model}."

    constraints = "Constraints: NO dialogue, NO speech text, NO on-screen lyrics, NO subtitles."

    return " ".join([scene_desc, characters, action, camera, style, constraints])


def save_upload(audio: UploadFile) -> str:
    ext = os.path.splitext(audio.filename or "")[1] or ".mp3"
    dest_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}{ext}")
    with open(dest_path, "wb") as out:
        shutil.copyfileobj(audio.file, out)
    return dest_path


@app.post("/generate")
async def generate(audio: UploadFile, lyrics: str = Form(...), mood: str = Form("")):
    audio_path = save_upload(audio)

    storyline = generate_storyline(lyrics, mood)
    scenes = generate_scenes(storyline, lyrics, mood)

    global_style = storyline.get("visual_style", "")
    for scene in scenes:
        scene["image_prompt"] = build_image_prompt(scene, global_style)
        scene["video_prompts"] = {
            model: build_video_prompt(scene, model, global_style)
            for model in ("KLING", "VEO3.1", "GROK")
        }

    return JSONResponse(
        {
            "received": {
                "audio_file": os.path.basename(audio_path),
                "lyrics_preview": lyrics[:120],
                "mood": mood,
            },
            "storyline": storyline,
            "scenes": scenes,
        }
    )
