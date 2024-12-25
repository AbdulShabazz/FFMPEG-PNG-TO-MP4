#!/usr/bin/env python3
"""
composite_passes.py

This script composites Unreal Engine render passes using FFmpeg,
handling missing passes and missing frames.

Usage:
    python composite_passes.py --output output_composite.mp4 --framerate 120 --ext png --start_index 1481294 --last_index 1488519 --resolution 1920x1080

Optional Arguments:
    --output: Name of the output composite video file (default: output_composite.mp4)
    --framerate: Frame rate of the input and output videos (default: 120)
    --resolution: Resolution of the blank frames (default: 1920x1080)
    --passes: Comma-separated list of passes with blend modes in the format PassName:BlendMode
             Example: "Unlit:normal,LightingOnly:multiply,DetailLightingOnly:screen,PathTracer:overlay,ReflectionsOnly:screen"
             If not provided, defaults are used.
"""

import os
import sys
import glob
import subprocess
import argparse
from pathlib import Path

def parse_arguments():
    parser = argparse.ArgumentParser(description="Composite Unreal Engine render passes using FFmpeg.")
    parser.add_argument('--output', type=str, default='output_composite.mp4', help='Name of the output composite video file (e.g. "output_composite.mp4").')  
    parser.add_argument('--ext', type=str, default='png', help='File extension type of the input sequence for the output composite video file (e.g., "png").')
    parser.add_argument('--start_index', type=str, default='1', help='Start index for the composite sequence (e.g., 1).')  
    parser.add_argument('--last_index', type=str, default='1', help='Last index for the composite sequence (e.g., 1)')
    parser.add_argument('--framerate', type=str, default='120', help='[Optional] Frame rate of the input and output videos (e.g., 60).')
    parser.add_argument('--crf', type=str, default='0', help='[Optional] output video compression ratio factor (i.e., strength) (e.g., --crf 0). Valid Range: 0 to 51')
    parser.add_argument('--pix_fmt', type=str, default='yuv420p10le', help='[Optional] Defines how pixel data is stored and represented in video frames (e.g., --pix_fmt yuv420p10le). Valid Range: yuv420p yuv422p yuv44p rgb24 yuva420p yuv420p10le')
    parser.add_argument('--resolution', type=str, default='1920x1080', help='[Optional] Resolution of the blank frames (e.g., "1920x1080").')
    parser.add_argument('--passes', type=str, default='', help='[Optional] ffmpeg supported, comma-separated list of passes with blend modes in the format PassName:BlendMode. Example: "Unlit:normal,LightingOnly:multiply"')
    return parser.parse_args()

def get_available_passes(current_dir,passes_config,start_index,file_ext,last_frame):
    available_passes = {}
    for pass_conf in passes_config:
        pass_name, blend_mode = pass_conf.split(':')
        # Check if at least one frame exists for the pass
        padded_num = str(start_index).zfill(len(str(last_frame)))
        first_frame = f"{current_dir}.{pass_name}.{padded_num}.{file_ext}"
        if os.path.exists(first_frame):
            available_passes[pass_name] = blend_mode
            print(f"Render Pass '{pass_name}' is available with blend mode '{blend_mode}'.")
        else:
            print(f"Render Pass '{pass_name}' ({first_frame}) is missing. It will be skipped.")
    return available_passes

def get_all_frames(current_dir,pass_name,file_ext):
    pattern = f"{current_dir}.{pass_name}.*.{file_ext}"
    frames = sorted(glob.glob(pattern))
    return frames

def extract_frame_number(current_dir,filename, pass_name,file_ext):
    basename = os.path.basename(filename)
    number_part = basename.replace(f'{current_dir}.{pass_name}.', '').replace(f'.{file_ext}', '')
    try:
        return int(number_part)
    except ValueError:
        return None

def fill_missing_frames(current_dir, pass_name, start_index, last_frame, resolution, file_ext, framerate):
    frames = get_all_frames(current_dir,pass_name,file_ext)
    existing_frames = set()
    for f in frames:
        num = extract_frame_number(current_dir,f, pass_name,file_ext)
        if num:
            existing_frames.add(num)
    print(f"Processing Pass: {pass_name}")
    prev_frame = None
    for i in range(start_index, last_frame + 1):
        if i in existing_frames:
            prev_frame = f"{current_dir}.{pass_name}.{i:07}.{file_ext}"
        else:
            target_frame = f"{current_dir}.{pass_name}.{i:07d}.{file_ext}"
            if prev_frame and os.path.exists(prev_frame):
                # Duplicate previous frame
                subprocess.run(['copy', '/Y', prev_frame, target_frame], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"Filled missing frame: {target_frame} with {prev_frame}")
            else:
                # Create a blank frame using FFmpeg
                subprocess.run([
                    'ffmpeg', '-f', 'lavfi',
                    '-i', f'color=black:s={resolution}:d=1/{framerate}',
                    '-vframes', '1',
                    target_frame,
                    '-y'
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"Created blank frame: {target_frame}")

def construct_filter_complex(available_passes, total_passes_ordered, pix_fmt):
    """
    Constructs the filter_complex string based on available passes and their blend modes.
    Assumes 'Unlit' is the base layer.
    """
    filters = []
    input_labels = []
    tmp_labels = []

    for idx, pass_name in enumerate(total_passes_ordered):
        if pass_name in available_passes:
            blend_mode = available_passes[pass_name]
            if pass_name.lower() == 'unlit':
                filters.append(f"[{idx}:v]format=rgba, setpts=PTS-STARTPTS [base];")
                current_output = "[base]"
            else:
                filters.append(f"[{idx}:v]format=rgba, setpts=PTS-STARTPTS [{pass_name.lower()}];")
                tmp_label = f"tmp{idx}"
                filters.append(f"{current_output}[{pass_name.lower()}]blend=all_mode={blend_mode} [{tmp_label}];")
                current_output = f"[{tmp_label}]"
    filters.append(f"{current_output}format={pix_fmt} [final]")
    filter_complex = ' '.join(filters)
    return filter_complex

def main():
    global args
    args = parse_arguments()

    if args.ext:
        file_ext = args.ext.strip("'\'").lower()
    else:
        print("Error: Sequence file extension (e.g., --ext png) not provided.")
        sys.exit(1)
    
    if args.start_index:
        start_index_w = args.start_index
        start_index_z = int(args.start_index)
    else:
        print("Error: Sequence start index (e.g., --start_index 1481294) not provided.")
        sys.exit(1)

    if args.last_index:
        last_frame_w = args.last_index
        last_frame_z = int(args.last_index)
    else:
        print("Error: Sequence start index (e.g., --last_index 1481294) not provided.")
        sys.exit(1)

    resolution = args.resolution
    crf = args.crf
    pix_fmt = args.pix_fmt
    framerate = args.framerate

    # Default passes and blend modes if not provided
    if args.passes:
        passes_config = args.passes.split(',')
    else:
        passes_config = [
            "Unlit:normal",
            "LightingOnly:multiply",
            "DetailLightingOnly:screen",
            "PathTracer:overlay",
            "ReflectionsOnly:screen"
        ]

    current_dir = Path.cwd().name

    print('\nInitializing...\n')

    available_passes = get_available_passes(current_dir,passes_config,start_index_z,file_ext,last_frame_z)

    if 'Unlit' not in available_passes:
        print("Error: 'Unlit' pass is required as the base layer but is missing.")
        sys.exit(1)

    # Determine the maximum number of frames across all passes
    max_frame = 0
    for pass_name in available_passes:
        frames = get_all_frames(current_dir,pass_name,file_ext)
        frame_numbers = [extract_frame_number(current_dir,f, pass_name,file_ext) for f in frames]
        frame_numbers = [num for num in frame_numbers if num is not None]
        if frame_numbers:
            current_max = len(frame_numbers)
            if current_max > max_frame:
                max_frame = current_max

    print(f"\nTotal Frames Detected: {max_frame}\n")

    # Fill missing frames for each available pass
    for pass_name in available_passes:
        fill_missing_frames(current_dir, pass_name, start_index_z, last_frame_z, resolution, file_ext, framerate)

    # Construct FFmpeg inputs
    ffmpeg_inputs = []
    total_passes_ordered = [
        "Unlit",
        "LightingOnly",
        "DetailLightingOnly",
        "PathTracer",
        "ReflectionsOnly"
    ]
    seq_len = len(last_frame_w)
    # Unreal Engine image sequences usually include the name of the current directory folder...
    for pass_name in total_passes_ordered:
        if pass_name in available_passes:
            ffmpeg_inputs.extend([
                "-start_number", start_index_w,
                "-framerate", framerate,
                "-i", f"{current_dir}.{pass_name}.%0{seq_len}d.{file_ext}"
            ])

    # Construct filter_complex
    filter_complex = construct_filter_complex(available_passes, total_passes_ordered, pix_fmt)

    print("\nConstructed filter_complex:")
    print(f"\n{filter_complex}\n")

    # Construct the final FFmpeg command
    ffmpeg_command = [
        'ffmpeg'
    ] + ffmpeg_inputs + [
        '-filter_complex', f'"{filter_complex}"',
        '-map', '"[final]"',
        '-c:v', 'libx265',
        '-crf', crf,
        '-pix_fmt', pix_fmt,
        args.output
    ]

    ffmpeg_command = ' '.join(ffmpeg_command)

    print("Running FFmpeg command:\n")

    print(f"{ffmpeg_command}\n")

    try:
        # Execute FFmpeg
        ret = subprocess.run(ffmpeg_command)
        # if ret.returncode != 0:
        #    print(f"Error: {ret.stderr}")
        #    sys.exit(1)
        print(f"Composite video successfully created as {args.output}")
    except subprocess.CalledProcessError as e:
        print(f'An error occurred while executing the command:{e}')
        print(f'Stdout: {e.stdout}')
        print(f'Stderr: {e.stderr}')
    except FileNotFoundError:
        print('Command not found. Please ensure the command is correct and command-support is installed.')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')

if __name__ == "__main__":
    main()
