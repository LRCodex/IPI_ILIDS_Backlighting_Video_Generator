# Video Generator for Scientific Benchmarks

This repository provides tools to generate synthetic videos for benchmarking video processing algorithms.
- IPI Generator: Creates videos of moving circles with fringe patterns, simulating typical images produced by Interferometric Particle Imaging (IPI) methods.
- Bubble Generator: Simulates bubbles rising in columns, mimicking typical images produced by bubble imaging with back lighting.

Both tools output videos and associated data files for analysis. Example images of what these methods can produce are stored in the `ExampleExperiment` folder.

---
## Features
- Customizable circle/bubble properties (size, speed, spawn rate, etc.).
- Post-processing options (blur, rotation, background images).
- Data files for ground truth and benchmarking.

---
## Installation

1. Clone this repository:
   git clone https://github.com/yourusername/video-generator.git
   cd video-generator

2. Install dependencies:
   pip install opencv-python numpy tqdm scipy names dearpygui argparse

3. Ensure FFmpeg is installed for video encoding. You can download it from https://ffmpeg.org/.

---
## Usage

You can use the provided GUI to configure and generate videos, or run the scripts individually from the command line:

### IPI Generator
python IPI_generator.py \
  --rmin 30 --rmax 80 \
  --vitx 20 --vity 10 \
  --fps 30 --video_duration 4 \
  --n_circles 20 --n_blobs 5 \
  --save_path ./Images \
  --output_video_path ./Output

### Bubble Generator
python bubble_generator.py \
  --width 1000 --height 1000 \
  --fps 20 --duration 10 \
  --spawn_interval 0.25 \
  --video_path ./bubble_simulation.mp4 \
  --csv_path ./bubble_data.csv

For all available options, run:
python IPI_generator.py --help
python bubble_generator.py --help

---
## Outputs
- IPI Generator: AVI video + fringe data files.
- Bubble Generator: MP4 video + CSV with bubble positions and velocities.

---
## Contact
For further inquiries, please email me at luke_84120@yahoo.fr.
