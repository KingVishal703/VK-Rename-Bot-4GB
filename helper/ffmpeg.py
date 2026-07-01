import time
import os
import json
import asyncio
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser



async def fix_thumb(thumb):
    width = 0
    height = 0
    try:
        if thumb != None:
            metadata = extractMetadata(createParser(thumb))
            if metadata.has("width"):
                width = metadata.get("width")
            if metadata.has("height"):
                height = metadata.get("height")
                Image.open(thumb).convert("RGB").save(thumb)
                img = Image.open(thumb)
                img.resize((320, height))
                img.save(thumb, "JPEG")
    except Exception as e:
        print(e)
        thumb = None 
       
    return width, height, thumb
    
async def take_screen_shot(video_file, output_directory, ttl):
    out_put_file_name = f"{output_directory}/{time.time()}.jpg"
    file_genertor_command = [
        "ffmpeg",
        "-ss",
        str(ttl),
        "-i",
        video_file,
        "-vframes",
        "1",
        out_put_file_name
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    return None



async def add_metadata(input_path, output_path, metadata, ms):
    try:
        await ms.edit("<i>I Found Metadata, Adding Into Your File ⚡</i>")
        command = [
            'ffmpeg', '-y', '-i', input_path, '-map', '0', '-c:s', 'copy', '-c:a', 'copy', '-c:v', 'copy',
            '-metadata', f'title={metadata}',  # Set Title Metadata
            '-metadata', f'author={metadata}',  # Set Author Metadata
            '-metadata:s:s', f'title={metadata}',  # Set Subtitle Metadata
            '-metadata:s:a', f'title={metadata}',  # Set Audio Metadata
            '-metadata:s:v', f'title={metadata}',  # Set Video Metadata
            '-metadata', f'artist={metadata}',  # Set Artist Metadata
            output_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()
        print(e_response)
        print(t_response)

        
        if os.path.exists(output_path):
            await ms.edit("<i>Metadata Has Been Successfully Added To Your File ✅</i>")
            return output_path
        else:
            await ms.edit("<i>Failed To Add Metadata To Your File ❌</i>")
            return None
    except Exception as e:
        print(f"Error occurred while adding metadata: {str(e)}")
        await ms.edit("<i>An Error Occurred While Adding Metadata To Your File ❌</i>")
        return None
    




# ============================================================
# Intro / Outro Clip + Watermark Feature
# ============================================================

async def _ffprobe(path):
    """Run ffprobe and return parsed JSON info (streams + format) for a media file."""
    cmd = [
        "ffprobe", "-v", "error",
        "-print_format", "json",
        "-show_streams", "-show_format",
        path,
    ]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    try:
        return json.loads(stdout.decode())
    except Exception:
        return {"streams": [], "format": {}}


async def concat_videos(clip_paths, output_path, status_msg=None):
    """
    Concatenate multiple video files (e.g. [intro, main, outro]) into one output.
    None entries in clip_paths are skipped (so caller can pass intro/outro as
    None when not set, only main is compulsory).

    All clips are re-encoded and normalised to the MAIN video's resolution/fps
    so that clips with different resolution, codec or missing audio still work.
    """
    clips = [c for c in clip_paths if c]
    if len(clips) < 2:
        return None  # nothing to concat

    if status_msg:
        try:
            await status_msg.edit("🎬 Adding Intro/Outro Clip...  ⚡")
        except Exception:
            pass

    # Use the first non-intro/outro video (assumed to be main) for target resolution.
    # We just use clips[0] if only outro/intro pair not distinguishable; caller
    # should pass main video info separately when possible. Here we probe every
    # clip and pick the max width found among them as a safe common size.
    infos = []
    for c in clips:
        infos.append(await _ffprobe(c))

    width, height = 1280, 720
    for info in infos:
        for s in info.get("streams", []):
            if s.get("codec_type") == "video":
                w, h = int(s.get("width", 0)), int(s.get("height", 0))
                if w * h > width * height:
                    width, height = w, h
                break
    width -= width % 2
    height -= height % 2
    if width <= 0 or height <= 0:
        width, height = 1280, 720

    fps = 30
    for s in infos[0].get("streams", []):
        if s.get("codec_type") == "video":
            fr = s.get("r_frame_rate", "30/1")
            try:
                num, den = fr.split("/")
                den = int(den) or 1
                fps = int(round(int(num) / den)) or 30
            except Exception:
                fps = 30
            break

    inputs = []
    filter_parts = []
    concat_refs = ""
    idx = 0
    for c, info in zip(clips, infos):
        duration = 0.0
        has_audio = False
        for s in info.get("streams", []):
            if s.get("codec_type") == "audio":
                has_audio = True
            if s.get("codec_type") == "video" and s.get("duration"):
                try:
                    duration = float(s.get("duration"))
                except Exception:
                    pass
        if not duration:
            try:
                duration = float(info.get("format", {}).get("duration", 0)) or 1.0
            except Exception:
                duration = 1.0

        inputs += ["-i", c]
        filter_parts.append(
            f"[{idx}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps},format=yuv420p[v{idx}]"
        )
        if has_audio:
            filter_parts.append(
                f"[{idx}:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[a{idx}]"
            )
        else:
            # generate a silent audio track matching this clip's duration
            filter_parts.append(
                f"anullsrc=channel_layout=stereo:sample_rate=44100,atrim=0:{duration}[a{idx}]"
            )
        concat_refs += f"[v{idx}][a{idx}]"
        idx += 1

    filter_complex = ";".join(filter_parts) + ";" + concat_refs + f"concat=n={idx}:v=1:a=1[outv][outa]"

    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", filter_complex,
        "-map", "[outv]", "-map", "[outa]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        output_path,
    ]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if os.path.exists(output_path):
        return output_path

    print("concat_videos ffmpeg error:", stderr.decode().strip())
    if status_msg:
        try:
            await status_msg.edit("❌ Failed To Add Intro/Outro Clip.")
        except Exception:
            pass
    return None


async def add_watermark(input_path, watermark_path, output_path, position="bottom_right",
                         scale_percent=15, margin=10, status_msg=None):
    """
    Overlay an image watermark on top of a video.
    position: top_left | top_right | bottom_left | bottom_right | center
    scale_percent: watermark width as % of video width
    """
    if status_msg:
        try:
            await status_msg.edit("🖊️ Adding Watermark...  ⚡")
        except Exception:
            pass

    pos_map = {
        "top_left": f"{margin}:{margin}",
        "top_right": f"W-w-{margin}:{margin}",
        "bottom_left": f"{margin}:H-h-{margin}",
        "bottom_right": f"W-w-{margin}:H-h-{margin}",
        "center": "(W-w)/2:(H-h)/2",
    }
    overlay_pos = pos_map.get(position, pos_map["bottom_right"])

    filter_complex = (
        f"[1:v]scale=iw*{scale_percent/100}:-1[wm];"
        f"[0:v][wm]overlay={overlay_pos}"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-i", watermark_path,
        "-filter_complex", filter_complex,
        "-c:a", "copy",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        output_path,
    ]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if os.path.exists(output_path):
        return output_path

    print("add_watermark ffmpeg error:", stderr.decode().strip())
    if status_msg:
        try:
            await status_msg.edit("❌ Failed To Add Watermark.")
        except Exception:
            pass
    return None


async def apply_intro_outro_watermark(main_path, intro_path, outro_path, watermark_path,
                                       clips_enabled, watermark_enabled, work_dir, status_msg=None):
    """
    High level pipeline used by the rename handler:
      1. If watermark_enabled and watermark exists -> overlay watermark on MAIN video only
         (intro/outro clips stay clean, untouched by the watermark)
      2. If clips_enabled and (intro or outro exists) -> concat [intro, (watermarked) main, outro]
    Returns the path to the final processed file (may be main_path unchanged if
    neither feature is enabled/configured), and cleans up its own temp files
    except the final one.
    """
    current = main_path
    temp_files = []

    if watermark_enabled and watermark_path:
        wm_out = os.path.join(work_dir, f"watermarked_{int(time.time())}.mp4")
        result = await add_watermark(current, watermark_path, wm_out, status_msg=status_msg)
        if result:
            if current != main_path:
                temp_files.append(current)
            current = result

    if clips_enabled and (intro_path or outro_path):
        concat_out = os.path.join(work_dir, f"concat_{int(time.time())}.mp4")
        result = await concat_videos([intro_path, current, outro_path], concat_out, status_msg)
        if result:
            if current != main_path:
                temp_files.append(current)
            current = result

    # clean up intermediate files (never delete main_path or the final output)
    for f in temp_files:
        if f and f != current and os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass

    return current


# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Back-Up Channel @JishuBotz
# Developer @JishuDeveloper & @MadflixOfficials
