import os
import csv
import cv2
import numpy as np
from tqdm import tqdm
import argparse

def main():
    parser = argparse.ArgumentParser(description="Generate a video of bubbles rising in columns.")
    parser.add_argument("--width", type=int, default=1000)
    parser.add_argument("--height", type=int, default=1000)
    parser.add_argument("--fps", type=int, default=20)
    parser.add_argument("--duration", type=int, default=10)
    parser.add_argument("--spawn_interval", type=float, default=0.25)
    parser.add_argument("--large_radius_probability", type=float, default=0.2)
    parser.add_argument("--radius_decrease_factor", type=float, default=0.25)
    parser.add_argument("--video_path", type=str, default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "bubble_simulation.mp4"))
    parser.add_argument("--csv_path", type=str, default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "bubble_data.csv"))
    args = parser.parse_args()

    # Total frames
    total_frames = args.fps * args.duration
    bubble_spawn_interval = max(1, int(args.fps * args.spawn_interval))

    # Video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(args.video_path, fourcc, args.fps, (args.width, args.height), isColor=False)

    # CSV
    csv_file = open(args.csv_path, mode='w', newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['frame', 'bubble_id', 'x', 'y', 'radius', 'velocity'])

    class Bubble:
        def __init__(self, bubble_id, start_frame, column):
            self.id = bubble_id
            self.velocity = np.random.uniform(250, 350)
            self.velocity_per_frame = self.velocity / args.fps
            self.column = column
            self.x_base = args.width // 4 if column == 0 else (args.width // 2 if column == 1 else 3 * args.width // 4)
            self.y = args.height
            self.amplitude = np.random.uniform(20, 40)
            self.frequency = np.random.uniform(0.5, 1.0)
            self.phase = np.random.uniform(0, 2 * np.pi)
            self.start_frame = start_frame
            if np.random.random() < args.large_radius_probability:
                self.initial_radius = np.random.randint(50, 61)
            else:
                self.initial_radius = np.random.randint(20, 31)
            self.radius = self.initial_radius

        def update_position(self, frame_idx):
            t = (frame_idx - self.start_frame) / args.fps
            self.y -= self.velocity_per_frame
            x_offset = self.amplitude * np.sin(2 * np.pi * self.frequency * t + self.phase)
            x = np.clip(self.x_base + x_offset, self.radius, args.width - self.radius)
            normalized_y = max(0, self.y / args.height)
            self.radius = max(1, int(self.initial_radius * (normalized_y) ** args.radius_decrease_factor))
            return int(x), int(self.y)

    bubbles = []
    bubble_id_counter = 0

    with tqdm(total=total_frames, desc="Generating video") as pbar:
        for frame_idx in range(total_frames):
            frame = np.full((args.height, args.width), 255, dtype=np.uint8)
            if frame_idx % bubble_spawn_interval == 0:
                column = bubble_id_counter % 3
                bubbles.append(Bubble(bubble_id_counter, frame_idx, column))
                bubble_id_counter += 1

            active_bubbles = []
            for bubble in bubbles:
                if bubble.y - bubble.radius > 0:
                    x, y = bubble.update_position(frame_idx)
                    cv2.circle(frame, (x, y), bubble.radius, 0, -1)
                    csv_writer.writerow([frame_idx, bubble.id, x, y, bubble.radius, bubble.velocity])
                    active_bubbles.append(bubble)
            bubbles = active_bubbles
            video.write(frame)
            pbar.update(1)

    video.release()
    csv_file.close()

if __name__ == '__main__':
    main()
