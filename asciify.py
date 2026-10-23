import json
import glob
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont

CHARS = " .:-=+*#%@"  # darkest -> lightest (dark pixels become spaces)

# --- Title settings ---
TITLE_TEXT = "~ I  Miss You ~"
FONT_PATH = "font.ttf"  # put your downloaded .ttf in this folder and set its name here
TITLE_WIDTH = 150        # title width in characters

# --- Mode settings ---
MODE = "photo"  # "video" or "photo" - chooses which function runs below
PHOTO_PATH = "kitten.png"


def frame_to_ascii(img, width=100, aspect=0.6):
    # Flatten any transparency onto black, then convert to grayscale
    img = img.convert("RGBA")
    background = Image.new("RGBA", img.size, "black")
    img = Image.alpha_composite(background, img).convert("L")

    # Treat near-black (h264 compression noise) as pure black
    img = img.point(lambda p: 0 if p < 25 else p)

    w, h = img.size
    height = max(1, int(width * (h / w) * aspect))
    img = img.resize((width, height))

    px = img.load()
    lines = []
    for y in range(height):
        row = ""
        for x in range(width):
            row += CHARS[px[x, y] * len(CHARS) // 256]
        lines.append(row)
    return "\n".join(lines)


def load_font(size=120):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except OSError:
        print(f"Could not load '{FONT_PATH}', using a fallback font.")
        try:
            return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", size)
        except OSError:
            return ImageFont.load_default()


def text_to_ascii(text, width=TITLE_WIDTH, aspect=0.6):
    font = load_font()
    left, top, right, bottom = font.getbbox(text)
    pad = 10
    img = Image.new("L", (right - left + pad * 2, bottom - top + pad * 2), 0)
    draw = ImageDraw.Draw(img)
    draw.text((pad - left, pad - top), text, font=font, fill=255)
    return frame_to_ascii(img, width, aspect)


def mov_to_ascii_frames(path, width=100, fps=12):
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            ["ffmpeg", "-y", "-i", path, "-vf", f"fps={fps}", f"{tmp}/f_%04d.png"],
            check=True,
        )
        files = sorted(glob.glob(f"{tmp}/f_*.png"))
        frames = [frame_to_ascii(Image.open(f), width) for f in files]
    durations = [int(1000 / fps)] * len(frames)
    return frames, durations


def save_animated_html(frames, durations, title_art, out="index.html"):
    # "<" escaped so ASCII characters can never break out of the script tag
    frames_json = json.dumps(frames).replace("<", "\\u003c")
    durations_json = json.dumps(durations)
    title_json = json.dumps(title_art).replace("<", "\\u003c")
    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>asciify</title>
<style>
  body {{ background: black; color: white; text-align: center; padding: 40px 0 80px; }}
  pre {{ font-family: monospace; font-size: 13px; line-height: 13px; display: inline-block; text-align: left; }}
  #title {{ font-size: 10px; line-height: 10px; margin: 60px 0 30px; animation: bob 1.2s ease-in-out infinite alternate; }}  @keyframes bob {{
    from {{ transform: translateY(-40px); }}
    to   {{ transform: translateY(40px); }}
  }}
</style>
</head>
<body>
<div><pre id="title"></pre></div>
<div><pre id="art"></pre></div>
<script>
  document.getElementById("title").textContent = {title_json};

  const frames = {frames_json};
  const durations = {durations_json};
  const art = document.getElementById("art");
  let i = 0;
  function play() {{
    art.textContent = frames[i];
    const wait = durations[i];
    i = (i + 1) % frames.length;
    setTimeout(play, wait);
  }}
  play();
</script>
</body>
</html>"""
    with open(out, "w") as f:
        f.write(html)


def run_video():
    frames, durations = mov_to_ascii_frames("video.mov", width=100, fps=12)
    title_art = text_to_ascii(TITLE_TEXT)
    save_animated_html(frames, durations, title_art)
    print(f"Wrote index.html with {len(frames)} frames")


def run_photo():
    frame = frame_to_ascii(Image.open(PHOTO_PATH), width=100)
    title_art = text_to_ascii(TITLE_TEXT)
    save_animated_html([frame], [1000], title_art)
    print("Wrote index.html with 1 frame (photo)")


if __name__ == "__main__":
    if MODE == "video":
        run_video()
    else:
        run_photo()