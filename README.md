# FFMPEG-PNG-TO-MP4
Commandline to convert PNG series to MPEG4 video.

## FFmpeg Usage Example

Below is an example of an FFmpeg command for creating a video from a sequence of images, along with a detailed breakdown of each parameter.

## Command

```bash
$ ffmpeg -framerate 60 -start_number 2086939 -i "Desert_A.%07d.png" -c:v libx264 -crf 18 -preset veryslow -pix_fmt yuv444p -movflags +faststart -vf "unsharp=5:5:1.0:5:5:0.0, eq=contrast=1.2" output.mp4
```

## Breakdown of the Command

### General Options

- **`-framerate 60`**
  
  Sets the input frame rate to **60 frames per second (fps)**. This determines how many images are processed per second in the resulting video.

- **`-start_number 2086939`**
  
  Specifies the starting number for the input sequence. In this case, the first image is `Desert_A.2086939.png`.

- **`-i "Desert_A.%07d.png"`**
  
  Defines the input files using a numbered sequence. The `%07d` indicates a seven-digit number with leading zeros (e.g., `Desert_A.2086939.png`).

### Video Encoding Options

- **`-c:v libx264`**
  
  Uses the **H.264** codec for video encoding. This codec is widely supported and offers a good balance between quality and file size.

- **`-crf 18`**
  
  Sets the **Constant Rate Factor (CRF)** to **18**, which provides high-quality output. Lower values produce higher quality (and larger file sizes), while higher values reduce quality.

- **`-preset veryslow`**
  
  Chooses the **`veryslow`** preset for encoding. Slower presets optimize compression efficiency, resulting in smaller file sizes at the expense of longer encoding times. Common presets include `slow`, `medium` (default), and `veryslow`.

- **`-pix_fmt yuv444p`**
  
  Sets the pixel format to **YUV 4:4:4 planar**. This format retains full color information and is useful for high-quality video output. Alternatively, `yuv420p` is commonly used for better compatibility with most players, including YouTube.

### File Optimization

- **`-movflags +faststart`**
  
  Enables **fast start** by moving the metadata to the beginning of the file. This allows the video to start playing before it is fully downloaded, which is beneficial for streaming.

### Video Filters

- **`-vf "unsharp=5:5:1.0:5:5:0.0, eq=contrast=1.2"`**
  
  Applies a series of video filters to enhance the output:
  
  - **`unsharp=5:5:1.0:5:5:0.0`**
    
    Applies an **unsharp mask** to sharpen the video. The parameters control the size and amount of sharpening.
  
  - **`eq=contrast=1.2`**
    
    Adjusts the **contrast** of the video, increasing it by a factor of **1.2** to make edges more prominent.

### Output File

- **`output.mp4`**
  
  Specifies the **name of the output video file**. In this case, the resulting video will be saved as `output.mp4`.

## Additional Notes

- **Sharpening Filters**
  
  You can choose between different sharpening filters based on your preference:
  
  - **`unsharp`**: Applies an initial sharpening effect.
  
  - **`sharpen`**: Applies an alternative sharpening method. You may use either `unsharp` or `sharpen` depending on the desired effect.

- **Adjusting Frame Rate and Quality**
  
  - **Frame Rate (`-framerate`)**: Adjust according to your project's requirements. Common values are `24`, `30`, or `60` fps.
  
  - **CRF (`-crf`)**: Fine-tune the quality by selecting a value between **18-23**. Lower values yield higher quality.

- **Pixel Format Compatibility**
  
  While `yuv444p` offers better color fidelity, using `yuv420p` can enhance compatibility with a wider range of players and platforms, including YouTube.

## Example with Common Parameters

Here's an example with more commonly used parameters for broader compatibility:

```bash
$ ffmpeg -framerate 30 -start_number 1 -i "frame%03d.png" \
-c:v libx264 -crf 20 -preset slow -pix_fmt yuv420p \
-movflags +faststart \
-vf "unsharp=5:5:1.0:5:5:0.0, eq=contrast=1.2" \
output.mp4
```

### Explanation of Changes

- **`-framerate 30`**: Sets input frame rate to 30 fps.
- **`-start_number 1`**: Starts numbering from 1 (e.g., `frame001.png`).
- **`-i "frame%03d.png"`**: Inputs files with three-digit numbering.
- **`-crf 20`**: Slightly lower quality setting for smaller file size.
- **`-preset slow`**: Faster encoding compared to `veryslow`.
- **`-pix_fmt yuv420p`**: Ensures better compatibility with most players.

Feel free to adjust these parameters based on your specific needs and the desired balance between quality, encoding speed, and file size.

## Python Script

### Overview

The Python script provides a more flexible and robust approach to handling missing passes and frames. It performs the following:

**Detect Available Passes:** Identifies which render passes are present in the specified directory.
* **Fill Missing Frames:** For each pass, it ensures that all frames are present by duplicating the previous frame or inserting a blank frame using FFmpeg.
* **Construct FFmpeg Command:** Dynamically builds the FFmpeg command based on available passes and their blend modes.
* **Execute FFmpeg:** Runs the FFmpeg command to generate the final composite video.

**Prerequisites**

* **Python Installed:** Ensure Python 3.x is installed on your system. You can download it from here.
* **FFmpeg Installed:** As with the batch script, ensure FFmpeg is installed and added to the system's PATH.
* **Python Libraries:** The script uses standard libraries (os, subprocess, glob). No additional installations are required.

Consistent Naming Convention: Render passes should follow a naming pattern like `PassName_0001.png, PassName_0002.png`, etc.

```python
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

```

Run the script

```
python composite_passes.py --output output_composite.mp4 --framerate 30
```

Optional arguments

```
--passes Unlit:normal,LightingOnly:multiply,DetailLightingOnly:screen,PathTracer:overlay,ReflectionsOnly:screen
```

Custom passes

```
python composite_passes.py --output output_composite.mp4 --framerate 120 --ext png --start_index 1481294 --last_index 1488519 --resolution 1920x1080
```
```
python composite_passes.py --output output_composite.mp4 --framerate 120 --ext png --start_index 8798040 --last_index 8804833 --resolution 2160x1080
```
