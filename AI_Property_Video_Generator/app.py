import os
import tempfile
from pathlib import Path
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2

APP_DIR = Path(__file__).parent
OUTPUT_DIR = APP_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="AI Property Video Generator", page_icon="🏡", layout="wide")
st.title("🏡 AI Property Video Generator")
st.caption("Turn property details and photos into a share-ready MP4 promotional video.")

def script_for(details):
    # Template-based copy: deliberately uses only user-provided facts.
    features = [x.strip() for x in details["features"].split(",") if x.strip()]
    scenes = []
    scenes.append((details["name"], f'{details["location"]}  •  {details["property_type"]}'))
    if details["price"].strip():
        scenes.append(("Price", details["price"].strip()))
    for feature in features[:5]:
        scenes.append(("A feature to love", feature))
    scenes.append(("Interested?", details["cta"].strip() or "Contact us for more information"))
    voice = [f'Welcome to {details["name"]}, located in {details["location"]}.']
    if details["price"].strip():
        voice.append(f'This {details["property_type"]} is listed at {details["price"]}.')
    if features:
        voice.append("Key features include " + ", ".join(features[:5]) + ".")
    voice.append(details["cta"].strip() or "Contact us for more information.")
    return scenes, " ".join(voice)

def load_font(size):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()

def fit_cover(img, size):
    w, h = size
    iw, ih = img.size
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left, top = (nw - w) // 2, (nh - h) // 2
    return img.crop((left, top, left + w, top + h))

def make_frame(img, heading, subtitle, width=1280, height=720):
    img = fit_cover(img.convert("RGB"), (width, height))
    # darken image slightly to improve overlay contrast
    arr = np.array(img).astype(np.float32)
    arr *= 0.68
    img = Image.fromarray(np.clip(arr, 0, 255).astype("uint8"))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle((0, height-205, width, height), fill=(0, 0, 0, 165))
    title_font = load_font(48)
    sub_font = load_font(30)
    # wrap long title/subtitle
    def wrap(text, font, max_width):
        words, lines, line = text.split(), [], ""
        for word in words:
            test = (line + " " + word).strip()
            if draw.textbbox((0,0), test, font=font)[2] <= max_width:
                line = test
            else:
                if line: lines.append(line)
                line = word
        if line: lines.append(line)
        return lines[:2]
    y = height - 170
    for line in wrap(heading, title_font, width-100):
        draw.text((55, y), line, font=title_font, fill=(255,255,255,255), stroke_width=1, stroke_fill=(0,0,0,150))
        y += 58
    for line in wrap(subtitle, sub_font, width-100):
        draw.text((58, y+4), line, font=sub_font, fill=(240,240,240,255))
        y += 38
    draw.text((width-260, 25), "PROPERTY SHOWCASE", font=load_font(18), fill=(255,255,255,220))
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def generate_video(details, image_files, out_path, seconds_per_scene=4, fps=24):
    scenes, voiceover = script_for(details)
    # Pair supplied photos with scenes; repeat photos only if fewer than scenes.
    if not image_files:
        raise ValueError("Please upload at least one property image.")
    decoded = []
    for f in image_files:
        try:
            f.seek(0)
            decoded.append(Image.open(f).convert("RGB"))
        except Exception:
            continue
    if not decoded:
        raise ValueError("The uploaded files could not be read as images.")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_path), fourcc, fps, (1280, 720))
    if not writer.isOpened():
        raise RuntimeError("Could not initialize MP4 writer. Check that OpenCV/codec support is installed.")
    try:
        for idx, (heading, subtitle) in enumerate(scenes):
            img = decoded[min(idx, len(decoded)-1)]
            base_frame = make_frame(img, heading, subtitle)
            total_frames = seconds_per_scene * fps
            for frame_idx in range(total_frames):
                # Gentle zoom-in effect, reset per scene
                progress = frame_idx / max(total_frames-1, 1)
                scale = 1.0 + 0.035 * progress
                h, w = base_frame.shape[:2]
                nw, nh = int(w*scale), int(h*scale)
                enlarged = cv2.resize(base_frame, (nw, nh), interpolation=cv2.INTER_LINEAR)
                x, y = (nw-w)//2, (nh-h)//2
                frame = enlarged[y:y+h, x:x+w]
                # fade in/out at each scene boundary
                fade = min(1.0, (frame_idx+1)/(fps*0.35), (total_frames-frame_idx)/(fps*0.35))
                frame = np.clip(frame.astype(np.float32)*max(0.12, fade), 0, 255).astype(np.uint8)
                writer.write(frame)
    finally:
        writer.release()
    return scenes, voiceover

with st.sidebar:
    st.header("Property details")
    name = st.text_input("Property name", "Maple Heights Residence")
    location = st.text_input("Location", "New Chandigarh, Punjab")
    price = st.text_input("Price", "₹85 lakh")
    property_type = st.selectbox("Property type", ["Apartment", "Villa", "Independent house", "Plot", "Commercial property"])
    features = st.text_area("Key features (comma-separated)", "2 bedrooms, Modular kitchen, Covered parking, Balcony")
    cta = st.text_input("Contact / CTA text", "Book a site visit today")
    duration = st.slider("Seconds per scene", 3, 6, 4)
    uploaded = st.file_uploader("Upload property photos (4–8 recommended)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

st.info("This prototype creates a captioned MP4 using template logic. It does not invent property facts and does not generate an AI voice-over.")
if uploaded and len(uploaded) < 4:
    st.warning("For the best result, upload 4–8 photos. You can still generate a preview with fewer images.")
if uploaded and len(uploaded) > 8:
    st.warning("Only the first 8 uploaded photos will be used.")
if not uploaded:
    st.write("Upload property photos in the sidebar, enter the details, then click **Generate property video**.")

if st.button("🎬 Generate property video", type="primary"):
    if not name.strip() or not location.strip() or not property_type:
        st.error("Please enter at least the property name, location, and property type.")
    elif not uploaded:
        st.error("Please upload at least one image before generating the video.")
    else:
        details = {"name": name.strip(), "location": location.strip(), "price": price,
                   "property_type": property_type, "features": features, "cta": cta}
        target = OUTPUT_DIR / "property_promo.mp4"
        with st.spinner("Building your video... this may take a little while."):
            try:
                scenes, voiceover = generate_video(details, uploaded[:8], target, duration)
                st.success("Video generated successfully!")
                st.video(str(target))
                st.download_button("⬇️ Download MP4", data=target.read_bytes(),
                                   file_name="property_promo.mp4", mime="video/mp4")
                st.subheader("Generated scene captions")
                for i, (heading, subtitle) in enumerate(scenes, 1):
                    st.write(f"**Scene {i}: {heading}** — {subtitle}")
                st.subheader("Suggested voice-over script")
                st.write(voiceover)
                st.caption("The script is template-generated from the supplied details. Review all claims before publishing.")
            except Exception as exc:
                st.error(f"Video generation failed: {exc}")
