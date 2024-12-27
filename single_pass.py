#!/usr/bin/env python3
"""
composite_passes.py

This script composites Unreal Engine render passes using FFmpeg,
handling missing passes and missing frames.

Usage:
    python composite_passes.py --output output_composite.mp4 --framerate 120 --ext png --start_index 1481294 --last_index 1488519 --resolution 1920x1080
    python composite_passes.py --gpu 1 --output output_composite.mp4 --framerate 120 --ext png --start_index 1481294 --last_index 1488519 --resolution 2160x1080
    python composite_passes.py --gpu 1 --output output_composite.mp4 --framerate 120 --ext png --start_index 1481294 --last_index 1488519 --resolution 4096x2048 --passes Unlit:overlay,PathTracer:lighten,DetailLightingOnly:overlay,LightingOnly:multiply,ReflectionsOnly:overlay

Optional Arguments:
    --output: Name of the output composite video file (default: output_composite.mp4)
    --framerate: Frame rate of the input and output videos (default: 120)
    --resolution: Resolution of the blank frames (default: 1920x1080)
    --passes: Comma-separated list of passes with blend modes in the format PassName:BlendMode
             Example: "Unlit:normal,LightingOnly:multiply,DetailLightingOnly:screen,PathTracer:overlay,ReflectionsOnly:screen"
             If not provided, defaults are used.
"""

# import os
import sys
# import glob
import subprocess
import argparse
# from pathlib import Path

def parse_arguments():
    parser = argparse.ArgumentParser(description="Composite Unreal Engine render passes using FFmpeg.")
    parser.add_argument('--output', type=str, default='output_composite.mp4', help='Name of the output composite video file (e.g., --output output_composite.mp4).')  
    parser.add_argument('--i', type=str, default='Scene_1_04', help='File extension type of the input sequence for the output composite video file (e.g., --i "Scene_1_4.%07d.png").')
    parser.add_argument('--start_index', type=str, default='1', help='Start index for the composite sequence (e.g., --start_index 1).')  
    parser.add_argument('--last_index', type=str, default='1', help='Last index for the composite sequence (e.g., --last_index 1)')
    parser.add_argument('--framerate', type=str, default='120', help='[Optional] Frame rate of the input and output videos (e.g., --framerate 120).')
    parser.add_argument('--crf', type=str, default='0', help='[Optional] output video compression ratio factor (i.e., compression strength) (e.g., --crf 0). Valid Range: 0 to 51')
    parser.add_argument('--pix_fmt', type=str, default='yuv420p10le', help='[Optional] Defines how pixel data is stored and represented in video frames (e.g., --pix_fmt yuv420p10le). Valid Range: yuv420p yuv422p yuv44p rgb24 yuva420p yuv420p10le')
    parser.add_argument('--gpu', type=str, default='', help='[Optional] gpu flag (e.g., --gpu 1).')
    return parser.parse_args()

def main():
    global args
    args = parse_arguments()
    
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
        print("Error: Sequence last index (e.g., --last_index 1481294) not provided.")
        sys.exit(1)

    fn = args.i
    gpu = args.gpu
    crf = args.crf
    pix_fmt = args.pix_fmt
    framerate = args.framerate

    # Construct FFmpeg inputs
    ffmpeg_inputs = []
    seq_len = len(last_frame_w)

    # Unreal Engine image sequences usually include the name of the current directory folder...
    ffmpeg_inputs.extend([
        "-start_number", start_index_w,
        "-framerate", framerate,
        "-i", fn
    ])

    # Construct the final FFmpeg command
    ffmpeg_command = [
        'ffmpeg'
    ] + ffmpeg_inputs

    if len(gpu) > 0:
        print("\nGPU Processing enabled\n")
        pix_fmt = "p010le"
        ffmpeg_command.extend([
            '-c:v', 'hevc_nvenc',
            '-preset', 'slow',
            '-qp','0',
            '-framerate', framerate,
            '-pix_fmt', pix_fmt,
            '-profile:v', 'main10',
            '-colorspace', 'bt2020nc',
            '-color_primaries', 'bt2020',
            '-color_trc', 'smpte2084',
            '-cbr','0',
            '-rc', 'vbr',
            '-bf', '4',
            '-spatial_aq', '1',
            '-temporal_aq', '1',
            '-metadata:s:v:0', 'color_range=tv',
            args.output
        ])
    else:
        ffmpeg_command.extend([
            '-c:v', 'libx265',
            '-crf', crf,
            '-pix_fmt', pix_fmt,
            args.output
        ])

    ffmpeg_command = ' '.join(ffmpeg_command)

    print("Running FFmpeg command:\n")

    print(f"{ffmpeg_command}\n")

    try:
        # Execute FFmpeg
        ret = subprocess.run(ffmpeg_command)
        print(f"Video successfully created as {args.output}")
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