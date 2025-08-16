import cv2
import numpy as np
import random
import os
from scipy.stats import lognorm
from tqdm import tqdm
import names
import argparse

class CircleImageCreator:
    def __init__(self, rmin=30, rmax=80, vitx=20, vity=10, fps=30, video_duration=4,
                 n_circles=20, n_blobs=5, apply_blur=True, blur_radius=5, apply_rotation=True,
                 use_background_image=False, background_image_path=None,
                 save_path=None, output_video_path=None):
        # Get the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Set paths for input/output files using script directory if not provided
        self.path = background_image_path or os.path.join(script_dir, "AVG_bg.tif")
        self.save_path = save_path or os.path.join(script_dir, "Images")
        self.output_video_path = output_video_path or script_dir

        # Background options
        self.use_background_image = use_background_image
        self.background_resolution = (2*1024, 1024)
        # Circle parameters
        self.rmin = rmin
        self.rmax = rmax
        self.vitx = vitx
        self.vity = vity
        # Video parameters
        self.video_duration = video_duration
        self.fps = fps
        self.n_pic = self.fps * self.video_duration
        self.dt = 1 / self.fps
        # Image generation parameters
        self.n_circles = n_circles
        self.n_blobs = n_blobs
        self.save = True
        self.make_video = True
        # Post-processing options
        self.apply_blur = apply_blur
        self.blur_radius = blur_radius
        self.blur_kernel = (blur_radius * 2 + 1, blur_radius * 2 + 1)
        self.apply_rotation = apply_rotation
        self.rotation_angle = cv2.ROTATE_90_CLOCKWISE
        # Fringe probability distribution parameters
        self.fringe_mean = 1.5
        self.fringe_sigma = 0.5

    def create_background(self):
        """Create background image based on settings"""
        if self.use_background_image:
            image = cv2.imread(self.path)
            if image is None:
                image = np.zeros((self.background_resolution[1], self.background_resolution[0], 3), dtype=np.uint8)
        else:
            image = np.zeros((self.background_resolution[1], self.background_resolution[0], 3), dtype=np.uint8)
        return image

    def unique_circle_creator(self, taille):
        """Create a unique circle with random properties"""
        plx = np.random.randint(self.rmax * 1.5, taille[0] - self.rmax * 1.5)
        ply = np.random.randint(self.rmax * 1.5, taille[1] - self.rmax * 1.5)
        radius = np.random.randint(self.rmin, self.rmax)
        color = 170 + np.random.randint(0, 70)
        nf = int(np.round(lognorm.rvs(s=self.fringe_sigma, scale=np.exp(self.fringe_mean))))
        IB = np.random.rand() * self.rmax / radius
        return plx, ply, radius, nf, IB, color

    def unique_blob_creator(self, taille):
        """Create a unique blob with random properties"""
        plx = np.random.randint(self.rmax * 1.5, taille[0] - self.rmax * 1.5)
        ply = np.random.randint(self.rmax * 1.5, taille[1] - self.rmax * 1.5)
        radius = np.random.randint(self.rmin, self.rmax)
        color_b = np.random.randint(50, 200)
        color_g = np.random.randint(50, 200)
        color_r = np.random.randint(50, 200)
        IB = np.random.rand()
        return plx, ply, radius, color_b, color_g, color_r, IB

    def create_images(self):
        """Generate sequence of images with circles and blobs"""
        print("Starting image generation...")
        ext = names.get_first_name(gender='male')
        image = self.create_background()
        taille = (image.shape[1], image.shape[0])
        circles_register = np.zeros([self.n_circles, 6])
        blobs_register = np.zeros([self.n_blobs, 7])
        with open(os.path.join(self.output_video_path, f"circles_properties_synth_noduplicate_{ext}.txt"), "w") as f2:
            for i in range(self.n_circles):
                circles_register[i] = np.array(self.unique_circle_creator(taille))
                f2.write(f"{circles_register[i, 3]} ")
            for i in range(self.n_blobs):
                blobs_register[i] = np.array(self.unique_blob_creator(taille))
            for count in tqdm(range(self.n_pic), desc="Generating images"):
                image = self.create_background()
                for i in range(self.n_circles):
                    circles_register[i, 0] = int(circles_register[i, 0] + self.vitx * self.dt * circles_register[i, 4] * 10 * np.random.rand())
                    circles_register[i, 1] = int(circles_register[i, 1] + self.vity * self.dt * circles_register[i, 4] * 10 * np.random.rand())
                    if (circles_register[i, 0] > taille[0] or circles_register[i, 0] < 0 or
                        circles_register[i, 1] > taille[1] or circles_register[i, 1] < 0 or
                        np.random.rand() < 0.05):
                        circles_register[i] = np.array(self.unique_circle_creator(taille))
                        f2.write(f"{circles_register[i, 3]} ")
                for i in range(self.n_blobs):
                    blobs_register[i, 0] = int(blobs_register[i, 0] + self.vitx * self.dt * blobs_register[i, 6] * 10 * np.random.rand())
                    blobs_register[i, 1] = int(blobs_register[i, 1] + self.vity * self.dt * blobs_register[i, 6] * 10 * np.random.rand())
                    if (blobs_register[i, 0] > taille[0] or blobs_register[i, 0] < 0 or
                        blobs_register[i, 1] > taille[1] or blobs_register[i, 1] < 0 or
                        np.random.rand() < 0.05):
                        blobs_register[i] = np.array(self.unique_blob_creator(taille))
                for i in range(self.n_circles):
                    image = cv2.circle(image, (int(circles_register[i, 0]), int(circles_register[i, 1])), int(circles_register[i, 2]),
                                       (int(circles_register[i, 5]), 100, 0), -1)
                    dl = 2 * circles_register[i, 2] / (circles_register[i, 3] + 1)
                    for j in range(1, int(circles_register[i, 3]) + 1):
                        d0 = abs(circles_register[i, 2] - int(j * dl))
                        dy = int(np.sqrt(int(circles_register[i, 2]) ** 2 - d0 ** 2)) - 2
                        x, y = int(circles_register[i, 0]), int(circles_register[i, 1])
                        dx = int(circles_register[i, 2]) - int(j * dl)
                        start_point, end_point = (x + dx, y - dy), (x + dx, y + dy)
                        color, th = (15, 5, 5), max(1, int(dl / 2))
                        image = cv2.line(image, start_point, end_point, color, th)
                for i in range(self.n_blobs):
                    plx, ply, radius, color_b, color_g, color_r, IB = blobs_register[i]
                    color = (int(color_b), int(color_g), int(color_r))
                    cv2.circle(image, (int(plx), int(ply)), int(radius), color, -1)
                    gradient = np.linspace(0, 1, int(radius))
                    colors = np.zeros((int(radius), 3), dtype=int)
                    colors[:, 0] = (color[0] * (1 - gradient)).astype(int)
                    colors[:, 1] = (color[1] * (1 - gradient)).astype(int)
                    colors[:, 2] = (color[2] * gradient).astype(int)
                    for x in range(int(plx) - int(radius), int(plx) + int(radius)):
                        for y in range(int(ply) - int(radius), int(ply) + int(radius)):
                            if ((x - plx) ** 2 + (y - ply) ** 2) <= radius ** 2:
                                distance_from_center = np.sqrt((x - plx) ** 2 + (y - ply) ** 2)
                                color_index = int(radius) - int(distance_from_center)
                                if color_index < 0:
                                    color_index = 0
                                elif color_index >= int(radius):
                                    color_index = int(radius) - 1
                                image[y, x] = colors[color_index]
                    num_points = 10
                    points = []
                    while len(points) < num_points:
                        x = random.randint(int(plx) - int(radius), int(plx) + int(radius))
                        y = random.randint(int(ply) - int(radius), int(ply) + int(radius))
                        if ((x - plx) ** 2 + (y - ply) ** 2) <= radius ** 2:
                            points.append((x, y))
                    pts = np.array(points, np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    cv2.fillPoly(image, [pts], (250, 250, 250))
                if self.apply_blur:
                    image = cv2.GaussianBlur(image, self.blur_kernel, cv2.BORDER_DEFAULT)
                if self.apply_rotation:
                    image = cv2.rotate(image, self.rotation_angle)
                if self.save:
                    filename = os.path.join(self.save_path, f'creator{str(count).zfill(3)}.png')
                    cv2.imwrite(filename, image, [cv2.IMWRITE_PNG_COMPRESSION, 3])
                    with open(os.path.join(self.output_video_path, f"circles_properties_synth_{ext}.txt"), "a") as f:
                        f.write(" ".join(map(str, circles_register[:, 3])) + "\n")
        print("Image generation completed.")
        return ext

    def make_video_file(self, ext):
        """Create video from generated image frames"""
        print("Starting video creation...")
        os.system(
            f'ffmpeg -framerate {self.fps} -i {os.path.join(self.save_path, "creator%03d.png")} '
            f'-pattern_type glob -c:v libx264 -pix_fmt yuv420p {os.path.join(self.output_video_path, f"Vid_{ext}.avi")} -y')
        print("Video creation completed.")
        print("Cleaning up temporary files...")
        for f in os.listdir(self.save_path):
            if f.endswith('.png'):
                os.remove(os.path.join(self.save_path, f))
        print("Cleanup completed.")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description="Generate a video with circles and blobs.")
    parser.add_argument("--rmin", type=int, default=30)
    parser.add_argument("--rmax", type=int, default=80)
    parser.add_argument("--vitx", type=int, default=20)
    parser.add_argument("--vity", type=int, default=10)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--video_duration", type=int, default=4)
    parser.add_argument("--n_circles", type=int, default=20)
    parser.add_argument("--n_blobs", type=int, default=5)
    parser.add_argument("--apply_blur", type=int, default=1)
    parser.add_argument("--blur_radius", type=int, default=5)
    parser.add_argument("--apply_rotation", type=int, default=1)
    parser.add_argument("--use_background_image", type=int, default=0)
    parser.add_argument("--background_image_path", type=str, default=os.path.join(script_dir, "AVG_bg.tif"))
    parser.add_argument("--save_path", type=str, default=os.path.join(script_dir, "Images"))
    parser.add_argument("--output_video_path", type=str, default=script_dir)
    args = parser.parse_args()

    creator = CircleImageCreator(
        rmin=args.rmin,
        rmax=args.rmax,
        vitx=args.vitx,
        vity=args.vity,
        fps=args.fps,
        video_duration=args.video_duration,
        n_circles=args.n_circles,
        n_blobs=args.n_blobs,
        apply_blur=bool(args.apply_blur),
        blur_radius=args.blur_radius,
        apply_rotation=bool(args.apply_rotation),
        use_background_image=bool(args.use_background_image),
        background_image_path=args.background_image_path,
        save_path=args.save_path,
        output_video_path=args.output_video_path
    )
    ext = creator.create_images()
    if creator.make_video:
        creator.make_video_file(ext)

if __name__ == '__main__':
    main()
