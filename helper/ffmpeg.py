import time
import os
import math
import json
import asyncio
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from helper.progress import TimeFormatter



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
    






# ======================================================================
# INTRO / OUTRO / WATERMARK ENGINE  (New, additive only)
# Single-pass FFmpeg pipeline: intro + main(+watermark) + outro
# Live progress edited on the same `ms` message every `update_interval` sec
# ======================================================================


async def get_video_info(path):
    """Probe a media file with ffprobe. Returns dict with duration/width/height/fps/audio info."""
    cmd = [
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_format", "-show_streams", path
    ]
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, _ = await process.communicate()
    try:
        info = json.loads(stdout.decode() or "{}")
    except Exception:
        info = {}

    duration = 0.0
    try:
        duration = float(info.get("format", {}).get("duration", 0) or 0)
    except Exception:
        pass

    width = height = 0
    fps = 25.0
    has_audio = False

    for s in info.get("streams", []):
        if s.get("codec_type") == "video" and not width:
            width = int(s.get("width", 0) or 0)
            height = int(s.get("height", 0) or 0)
            fr = s.get("r_frame_rate", "25/1")
            try:
                num, den = fr.split("/")
                fps = round(float(num) / float(den), 2) if float(den) else 25.0
            except Exception:
                fps = 25.0
        elif s.get("codec_type") == "audio":
            has_audio = True

    return {
        "duration": duration,
        "width": width,
        "height": height,
        "fps": fps,
        "has_audio": has_audio,
    }


async def _build_segment_filters(inputs, filter_parts, seg_index, info, target_w, target_h,
                                  target_fps, label, is_main=False, watermark=None):
    """Builds scale/pad/watermark/audio filters for one input segment. Returns (video_label, audio_label)."""
    v_scaled = f"v{label}s"
    filter_parts.append(
        f"[{seg_index}:v]scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,"
        f"pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={target_fps}[{v_scaled}]"
    )

    v_final = v_scaled
    if is_main and watermark:
        v_final = f"v{label}wm"
        if watermark["type"] == "image":
            wm_idx = watermark["_input_idx"]
            logo_h = max(int(target_h * 0.12), 24)
            filter_parts.append(f"[{wm_idx}:v]scale=-1:{logo_h}[wmimg]")
            filter_parts.append(f"[{v_scaled}][wmimg]overlay=W-w-24:24[{v_final}]")
        else:
            text = str(watermark["value"])
            text = text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\u2019").replace("%", "\\%")
            fontsize = max(int(target_h * 0.035), 18)
            filter_parts.append(
                f"[{v_scaled}]drawtext=text='{text}':fontcolor=white@0.9:fontsize={fontsize}:"
                f"box=1:boxcolor=black@0.35:boxborderw=10:x=w-tw-24:y=24[{v_final}]"
            )

    a_final = f"a{label}"
    if info["has_audio"]:
        filter_parts.append(f"[{seg_index}:a]aresample=async=1:first_pts=0[{a_final}]")
    else:
        dur = info["duration"] or 1
        filter_parts.append(f"anullsrc=channel_layout=stereo:sample_rate=44100:d={dur}[{a_final}]")

    return v_final, a_final


async def run_ffmpeg_with_progress(cmd, total_duration, ms, phase_boundaries, update_interval=10):
    """
    Runs the ffmpeg command, reading '-progress pipe:1' output and editing `ms`
    at most once every `update_interval` seconds with a live phase + progress bar.
    phase_boundaries: dict {label: (start_sec, end_sec)} in output timeline order.
    Returns (success: bool, error_text: str|None)
    """
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stderr_chunks = []

    async def read_stderr():
        while True:
            line = await process.stderr.readline()
            if not line:
                break
            stderr_chunks.append(line.decode(errors="ignore"))

    stderr_task = asyncio.create_task(read_stderr())

    last_update = 0.0
    out_time_sec = 0.0

    while True:
        line = await process.stdout.readline()
        if not line:
            break
        line = line.decode(errors="ignore").strip()

        if line.startswith("out_time_ms="):
            try:
                out_time_sec = max(0.0, int(line.split("=")[1]) / 1_000_000)
            except Exception:
                pass

        elif line.startswith("progress="):
            is_end = line.endswith("end")
            now = time.time()
            if ms and (now - last_update >= update_interval or is_end):
                last_update = now
                percent = 0.0
                if total_duration:
                    percent = min(100.0, (out_time_sec / total_duration) * 100)

                phase = "Processing"
                for name, (start, end) in phase_boundaries.items():
                    if start <= out_time_sec < end or (is_end and end == total_duration):
                        phase = name
                        break

                filled = math.floor(percent / 5)
                bar = "■" * filled + "□" * (20 - filled)
                elapsed_fmt = TimeFormatter(int(out_time_sec * 1000))
                total_fmt = TimeFormatter(int(total_duration * 1000))
                try:
                    await ms.edit(
                        f"🎬 <b>{phase}</b>\n\n{bar}\n\n"
                        f"<b>⏳ Done:</b> {round(percent, 1)}%\n"
                        f"<b>🕒 Time:</b> {elapsed_fmt or '0s'} / {total_fmt or '0s'}"
                    )
                except Exception:
                    pass

    await process.wait()
    await stderr_task

    if process.returncode != 0:
        return False, "".join(stderr_chunks[-40:])
    return True, None


async def add_intro_outro_watermark(main_path, output_path, intro_path=None, outro_path=None,
                                     watermark=None, ms=None, update_interval=10):
    """
    Single-pass pipeline: [intro?] + [main + watermark?] + [outro?] -> output_path
    watermark: None OR {"type": "text", "value": "..."} OR {"type": "image", "value": "/path/logo.png"}
    Returns (success: bool, error_text: str|None)
    """
    main_info = await get_video_info(main_path)
    if not main_info["width"]:
        return False, "Main video ki info nahi mil payi (file corrupt ho sakti hai)."

    target_w = main_info["width"]
    target_h = main_info["height"]
    target_fps = main_info["fps"] or 25.0

    inputs = []
    filter_parts = []
    seq_v, seq_a = [], []
    phase_boundaries = {}
    cursor = 0.0

    # Intro
    if intro_path and os.path.exists(intro_path):
        idx = len(inputs)
        inputs.append(intro_path)
        info = await get_video_info(intro_path)
        v, a = await _build_segment_filters(inputs, filter_parts, idx, info, target_w, target_h,
                                             target_fps, "intro")
        seq_v.append(v)
        seq_a.append(a)
        dur = info["duration"] or 0
        phase_boundaries["Intro clip add ho rahi hai"] = (cursor, cursor + dur)
        cursor += dur

    # Main (+ watermark)
    main_idx = len(inputs)
    inputs.append(main_path)

    wm_conf = None
    if watermark:
        wm_conf = dict(watermark)
        if wm_conf["type"] == "image":
            wm_idx = len(inputs)
            inputs.append(wm_conf["value"])
            wm_conf["_input_idx"] = wm_idx

    v, a = await _build_segment_filters(inputs, filter_parts, main_idx, main_info, target_w, target_h,
                                         target_fps, "main", is_main=True, watermark=wm_conf)
    seq_v.append(v)
    seq_a.append(a)
    dur = main_info["duration"] or 0
    main_label = "Watermark lag raha hai" if watermark else "Video process ho raha hai"
    phase_boundaries[main_label] = (cursor, cursor + dur)
    cursor += dur

    # Outro
    if outro_path and os.path.exists(outro_path):
        idx = len(inputs)
        inputs.append(outro_path)
        info = await get_video_info(outro_path)
        v, a = await _build_segment_filters(inputs, filter_parts, idx, info, target_w, target_h,
                                             target_fps, "outro")
        seq_v.append(v)
        seq_a.append(a)
        dur = info["duration"] or 0
        phase_boundaries["Outro clip add ho rahi hai"] = (cursor, cursor + dur)
        cursor += dur

    n = len(seq_v)
    concat_inputs = "".join(f"[{v}][{a}]" for v, a in zip(seq_v, seq_a))
    filter_parts.append(f"{concat_inputs}concat=n={n}:v=1:a=1[outv][outa]")
    filter_complex = ";".join(filter_parts)

    total_duration = cursor or (main_info["duration"] or 1)

    cmd = ["ffmpeg", "-y"]
    for inp in inputs:
        cmd += ["-i", inp]
    cmd += [
        "-filter_complex", filter_complex,
        "-map", "[outv]", "-map", "[outa]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "160k",
        "-movflags", "+faststart",
        "-threads", "0",
        "-progress", "pipe:1", "-nostats",
        output_path,
    ]

    if ms:
        try:
            await ms.edit("🎬 <b>Processing shuru ho rahi hai...</b>")
        except Exception:
            pass

    ok, err = await run_ffmpeg_with_progress(cmd, total_duration, ms, phase_boundaries, update_interval)

    if not ok:
        return False, err
    if not os.path.exists(output_path):
        return False, "Output file generate nahi hui."
    return True, None


# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Back-Up Channel @JishuBotz
# Developer @JishuDeveloper & @MadflixOfficials
