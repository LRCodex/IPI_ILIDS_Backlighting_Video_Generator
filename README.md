# Video Generator for Scientific Benchmarks

This repository provides tools to generate synthetic videos on Python for benchmarking video processing algorithms, from an easy to operate graphical interface.
- IPI Generator: Creates videos of moving circles with fringe patterns, simulating typical images produced by Interferometric Particle Imaging (IPI/ILIDS) methods.
- Bubble Generator: Simulates bubbles rising in columns, mimicking typical images produced by bubble imaging with back lighting.

Both tools output videos to be processed by your detection algorithm to test it, and associated data files for analysis and comparison of real data versus data measured by your detection algorithm. Example images of what these experimentals methods can produce are stored in the `ExamplesExperiments` folder.

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

2. Required Packages
This project relies on the following Python packages:
- **OpenCV (`opencv-python`)**: For video and image processing.
- **NumPy**: For numerical operations and array handling.
- **Tqdm**: For progress bars during video generation.
- **SciPy**: For statistical functions (e.g., log-normal distribution for fringe generation).
- **Names**: For generating random names for output files.
- **Dear PyGui**: For the graphical user interface (GUI).
- **Argparse**: For parsing command-line arguments.

Additionally, **FFmpeg** is required for video encoding. You can install it from [FFmpeg's official website](https://ffmpeg.org/).

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

For all available options, click on the question mark in the GUI, or run:
python IPI_generator.py --help
python bubble_generator.py --help

---
## Outputs
- IPI Generator: AVI video + fringe data files.
- Bubble Generator: MP4 video + CSV with bubble positions and velocities.

---
## Contact
For further inquiries, please email me at luke_84120@yahoo.fr.
