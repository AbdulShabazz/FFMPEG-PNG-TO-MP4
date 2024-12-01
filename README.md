# FFMPEG-PNG-TO-MP4
Commandline to convert PNG series to MPEG4 video.

## FFmpeg Usage Example

Below is an example of an FFmpeg command for creating a video from a sequence of images, along with a detailed breakdown of each parameter.

## Command

```bash
$ ffmpeg -framerate 60 -start_number 2086939 -i "Desert_A.%07d.png" \
-c:v libx264 -crf 18 -preset veryslow -pix_fmt yuv444p \
-movflags +faststart \
-vf "unsharp=5:5:1.0:5:5:0.0, eq=contrast=1.2" \
output.mp4
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
