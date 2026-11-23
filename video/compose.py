"""Renders the Kagaz Saathi demo video at 3840x2160 (4K UHD), 30 fps, from 4K app screenshots,
title cards and the voice-over. Also writes a 1080p copy and an .srt file.

python compose_4k.py
"""
import json
import re
import subprocess
from pathlib import Path

import cv2
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from demo_script import SCENES

HERE = Path(__file__).parent
WORK = HERE / "work"
SHOTS = HERE / "shots"
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 3840, 2160, 30
TIMING = json.loads((WORK / "timing.json").read_text(encoding="utf-8"))
OUT4K = HERE / "Kagaz_Saathi_Demo_4K.mp4"

PINE, PINE2, MINT = (27, 39, 102), (14, 21, 48), (255, 168, 104)
TEXT, MUTED, CORAL = (244, 245, 252), (170, 178, 220), (255, 99, 110)
F = "C:/Windows/Fonts/"
LEAD, GAP, TAIL, XF = 0.25, 0.5, 1.8, 0.45   # voice lead-in, gap between scenes, end hold, crossfade


def font(size, w="regular"):
    return ImageFont.truetype(F + {"bold": "segoeuib.ttf", "semi": "seguisb.ttf", "regular": "segoeui.ttf",
                                   "mono": "consola.ttf"}[w], size)


def to_bgr(img):
    return cv2.cvtColor(np.asarray(img.convert("RGB")), cv2.COLOR_RGB2BGR)


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


# ---------------------------------------------------------------- backgrounds and cards
def background():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    t = y / H
    glow = np.clip(1 - ((x / W) ** 2 + (y / H) ** 2) * 1.5, 0, 1)
    glow2 = np.clip(1 - (((x - W) / W) ** 2 + ((y - H) / H) ** 2) * 2.2, 0, 1)
    img = np.zeros((H, W, 3), np.float32)
    for i in range(3):
        img[..., i] = PINE[i] * (1 - t) + PINE2[i] * t
    img[..., 0] += 18 * glow + 6 * glow2
    img[..., 1] += 58 * glow + 22 * glow2
    img[..., 2] += 48 * glow + 18 * glow2
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


BG = background()


def card(kind):
    img = BG.copy()
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([240, 200, 344, 304], radius=28, fill=(255, 138, 76))
    d.text((292, 254), "K", font=font(72, "bold"), fill=(42, 20, 5), anchor="mm")
    d.text((380, 252), "Kagaz Saathi", font=font(70, "bold"), fill=TEXT, anchor="lm")
    if kind == "problem":
        d.text((240, 600), "THE PROBLEM", font=font(64, "bold"), fill=MINT)
        d.text((240, 710), "Who do you ask when a message", font=font(170, "bold"), fill=TEXT)
        d.text((240, 910), "looks wrong?", font=font(170, "bold"), fill=MINT)
        for i, r in enumerate(["Your account will be blocked today", "You are under digital arrest", "You have won a prize"]):
            y = 1290 + i * 200
            d.ellipse([244, y + 52, 290, y + 98], fill=CORAL)
            d.text((350, y), r, font=font(112, "semi"), fill=(210, 216, 242))
    elif kind == "intro":
        d.text((240, 640), "CAMPUS TO CLOUD HACKATHON  ·  TEAM HACKBOTS", font=font(64, "bold"), fill=MINT)
        d.text((240, 760), "Is this message real?", font=font(250, "bold"), fill=TEXT)
        d.text((240, 1060), "Ask Kagzi first.", font=font(250, "bold"), fill=MINT)
        d.text((240, 1500), "Scam check, plain-language explanation and family alert, in Hindi, Marathi and English", font=font(76), fill=MUTED)
    elif kind == "aws":
        d.text((240, 600), "LIVE ON AWS", font=font(64, "bold"), fill=MINT)
        d.text((240, 710), "One function. One table.", font=font(200, "bold"), fill=TEXT)
        rows = [("AWS Lambda + Function URL", "the whole app behind one HTTPS address"), ("Amazon DynamoDB", "accounts, history, family circle, alert outbox"),
                ("Amazon CloudWatch", "logs and errors"), ("AWS IAM", "a least-privilege role for the function"), ("AWS SAM", "one template deploys everything")]
        for i, (a, b) in enumerate(rows):
            y = 1060 + i * 176
            d.ellipse([244, y + 44, 288, y + 88], fill=MINT)
            d.text((340, y), a, font=font(100, "semi"), fill=TEXT)
            d.text((340 + d.textlength(a, font=font(100, "semi")) + 60, y + 18), b, font=font(72), fill=MUTED)
    elif kind == "outro":
        d.text((240, 760), "Kagaz Saathi.", font=font(270, "bold"), fill=TEXT)
        d.text((240, 1090), "Ask Kagzi first.", font=font(270, "bold"), fill=MINT)
        d.text((240, 1560), "Team HackBots  ·  Campus to Cloud Hackathon, Techfest IIT Bombay 2026-27", font=font(70), fill=MUTED)
    return to_bgr(img)


def rounded(img, r):
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, img.width - 1, img.height - 1], radius=r, fill=255)
    out = Image.new("RGBA", img.size)
    out.paste(img, (0, 0), mask)
    return out


def phones(files):
    img = BG.copy().convert("RGBA")
    ph_h = 1780
    ims = []
    for f in files:
        p = Image.open(SHOTS / f).convert("RGB")
        p = p.resize((round(p.width * ph_h / p.height), ph_h), Image.LANCZOS)
        bez = Image.new("RGB", (p.width + 44, p.height + 44), (12, 14, 14))
        bez.paste(p, (22, 22))
        ims.append(rounded(bez, 96))
    gap = 260
    total = sum(i.width for i in ims) + gap * (len(ims) - 1)
    x = (W - total) // 2
    y = (H - ims[0].height) // 2 + 40
    for im in ims:
        sh = Image.new("RGBA", (im.width + 200, im.height + 200), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([100, 130, im.width + 100, im.height + 130], radius=110, fill=(0, 0, 0, 150))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(45)), (x - 100, y - 100))
        img.alpha_composite(im, (x, y))
        x += im.width + gap
    return to_bgr(img)


def pill(label):
    f = font(60, "semi")
    w = int(ImageDraw.Draw(Image.new("RGB", (8, 8))).textlength(label, font=f)) + 190
    img = Image.new("RGBA", (w, 124), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, 123], radius=62, fill=(14, 21, 48, 238))
    d.ellipse([36, 40, 80, 84], fill=MINT)
    d.text((112, 62), label, font=f, fill=TEXT, anchor="lm")
    return img


def subtitle_img(text):
    f = font(70, "semi")
    tw = int(ImageDraw.Draw(Image.new("RGB", (8, 8))).textlength(text, font=f))
    img = Image.new("RGBA", (tw + 110, 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, img.width - 1, 149], radius=34, fill=(8, 10, 28, 210))
    d.text((img.width / 2, 74), text, font=f, fill=(255, 255, 255), anchor="mm")
    return img


def rgba_layer(img):
    a = np.asarray(img)
    bgr = cv2.cvtColor(a[..., :3], cv2.COLOR_RGB2BGR).astype(np.float32)
    alpha = a[..., 3:4].astype(np.float32) / 255.0
    return bgr, alpha


def overlay(frame, layer, x, y, strength=1.0):
    bgr, alpha = layer
    h, w = alpha.shape[:2]
    roi = frame[y:y + h, x:x + w].astype(np.float32)
    a = alpha * strength
    frame[y:y + h, x:x + w] = (roi * (1 - a) + bgr * a).astype(np.uint8)


# ---------------------------------------------------------------- timeline
def build_timeline():
    segs, subs, audio = [], [], []
    t = 0.0
    for idx, (name, _, visuals) in enumerate(SCENES):
        tm = TIMING[name]
        length = LEAD + tm["duration"] + (TAIL if idx == len(SCENES) - 1 else GAP)
        audio.append((tm["audio"], t + LEAD))
        starts = [t] + [t + LEAD + tm["cues"][c] - 0.15 for c, _ in visuals[1:]]
        for i, (_, v) in enumerate(visuals):
            end = starts[i + 1] if i + 1 < len(visuals) else t + length
            segs.append({"start": starts[i], "end": end, "v": v})
        # subtitles: align spoken words with the clean text to keep punctuation
        tokens = tm["text"].split()
        words = tm["words"]
        chunk, cs = [], None
        for k, (ws, we, _) in enumerate(words):
            tok = tokens[k] if k < len(tokens) else words[k][2]
            if cs is None:
                cs = ws
            chunk.append(tok)
            brk = tok[-1] in ".,:;!?" or len(chunk) >= 8
            if brk or k == len(words) - 1:
                subs.append((t + LEAD + cs, t + LEAD + we + 0.12, " ".join(chunk)))
                chunk, cs = [], None
        t += length
    return segs, subs, audio, t


SEGS, SUBS, AUDIO, TOTAL = build_timeline()
for i in range(len(SUBS) - 1):   # no overlaps, small gaps closed
    s, e, txt = SUBS[i]
    ns = SUBS[i + 1][0]
    SUBS[i] = (s, min(max(e, ns - 0.25), ns), txt) if ns - e < 0.4 else (s, e, txt)

cache = {}


def asset(v):
    key = repr(v[:2]) if v[0] != "shot" else v[1]
    if key not in cache:
        if v[0] == "card":
            cache[key] = card(v[1])
        elif v[0] == "phones":
            cache[key] = phones(v[1])
        else:
            cache[key] = cv2.imread(str(SHOTS / v[1]), cv2.IMREAD_COLOR)
    return cache[key]


pill_cache = {}


def render(seg, t):
    v = seg["v"]
    u = (t - seg["start"]) / max(seg["end"] - seg["start"], 0.01)
    img = asset(v)
    if v[0] == "shot":
        (x0, y0, w0), (x1, y1, w1) = v[2], v[3]
        e = ease(u)
        x, y, w = x0 + (x1 - x0) * e, y0 + (y1 - y0) * e, w0 + (w1 - w0) * e
        s = W / w
        M = np.float32([[s, 0, -x * s], [0, s, -y * s]])
        frame = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        label = v[4]
    else:
        z = 1.0 + 0.045 * ease(u)
        s = z
        M = np.float32([[s, 0, (1 - s) * W / 2], [0, s, (1 - s) * H / 2]])
        frame = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        label = v[2] if v[0] == "phones" else None
    if label:
        if label not in pill_cache:
            pill_cache[label] = rgba_layer(pill(label))
        fade = min(1.0, (t - seg["start"]) / 0.5)
        overlay(frame, pill_cache[label], 110, 110, fade)
    return frame


sub_cache = {}


def frame_at(t):
    cur = next((i for i, s in enumerate(SEGS) if s["start"] <= t < s["end"]), len(SEGS) - 1)
    seg = SEGS[cur]
    frame = render(seg, t)
    if cur > 0 and t - seg["start"] < XF:
        prev = render(SEGS[cur - 1], t)
        a = (t - seg["start"]) / XF
        frame = cv2.addWeighted(prev, 1 - a, frame, a, 0)
    if seg["v"][0] != "card":
        for s, e, txt in SUBS:
            if s <= t < e:
                if txt not in sub_cache:
                    sub_cache[txt] = rgba_layer(subtitle_img(txt))
                layer = sub_cache[txt]
                w = layer[1].shape[1]
                overlay(frame, layer, (W - w) // 2, H - 290, min(1.0, (t - s) / 0.12))
                break
    # fade in from black at start, out at the end
    if t < 0.5:
        frame = (frame * (t / 0.5)).astype(np.uint8)
    if t > TOTAL - 0.8:
        frame = (frame * max(0.0, (TOTAL - t) / 0.8)).astype(np.uint8)
    return frame


def build_audio(path):
    args = [FF, "-y", "-loglevel", "error"]
    for a, _ in AUDIO:
        args += ["-i", a]
    parts = "".join(f"[{i}:a]aresample=48000,adelay={int(st * 1000)}|{int(st * 1000)}[a{i}];" for i, (_, st) in enumerate(AUDIO))
    mix = "".join(f"[a{i}]" for i in range(len(AUDIO)))
    flt = parts + f"{mix}amix=inputs={len(AUDIO)}:normalize=0,apad,atrim=0:{TOTAL:.3f},loudnorm=I=-15:TP=-1.5:LRA=9,aresample=48000[out]"
    subprocess.run(args + ["-filter_complex", flt, "-map", "[out]", "-ac", "2", "-c:a", "pcm_s16le", str(path)], check=True)


def write_srt():
    def ts(x):
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    lines = []
    for i, (s, e, txt) in enumerate(SUBS, 1):
        lines += [str(i), f"{ts(s)} --> {ts(e)}", txt, ""]
    (HERE / "Kagaz_Saathi_Demo.srt").write_text("\n".join(lines), encoding="utf-8")


def main():
    WORK.mkdir(exist_ok=True)
    wav = WORK / "demo_audio.wav"
    build_audio(wav)
    write_srt()
    n = int(round(TOTAL * FPS))
    print(f"duration {TOTAL:.1f}s, {n} frames at {W}x{H}")
    enc = subprocess.Popen([FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-i", str(wav), "-map", "0:v", "-map", "1:a",
                            "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p",
                            "-profile:v", "high", "-level:v", "5.2", "-tune", "stillimage",
                            "-x264-params", "keyint=60:min-keyint=30",
                            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                            "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", "-shortest", str(OUT4K)],
                           stdin=subprocess.PIPE)
    for i in range(n):
        enc.stdin.write(frame_at(i / FPS).tobytes())
        if i % 300 == 0:
            print(f"  frame {i}/{n}", flush=True)
    enc.stdin.close()
    enc.wait()
    print("wrote", OUT4K)



if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        for t in [float(x) for x in sys.argv[2:]]:
            cv2.imwrite(str(WORK / f"prev_{t:05.1f}.jpg"), cv2.resize(frame_at(t), (1280, 720), interpolation=cv2.INTER_AREA))
        print("total", round(TOTAL, 1))
        for s in SEGS:
            print(round(s["start"], 2), round(s["end"], 2), s["v"][0], s["v"][1] if s["v"][0] != "phones" else s["v"][1][0])
    else:
        main()
