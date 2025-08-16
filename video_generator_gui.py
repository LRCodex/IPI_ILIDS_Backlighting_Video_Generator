import dearpygui.dearpygui as dpg
import subprocess
import threading
import os

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Global dictionary to store user parameters
user_params = {
    "script": "IPI_generator.py",
    "rmin": 30,
    "rmax": 80,
    "vitx": 15,
    "vity": 15,
    "fps": 30,
    "video_duration": 2,
    "n_circles": 20,
    "n_blobs": 0,
    "apply_blur": False,
    "blur_radius": 5,
    "apply_rotation": True,
    "use_background_image": False,
    "background_image_path": os.path.join(script_dir, "AVG_bg.tif"),
    "save_path": os.path.join(script_dir, "Images"),
    "output_video_path": script_dir,
    # Bubble simulation parameters
    "bubble_width": 1000,
    "bubble_height": 1000,
    "bubble_fps": 20,
    "bubble_duration": 10,
    "bubble_spawn_interval": 0.25,
    "large_radius_probability": 0.2,
    "radius_decrease_factor": 0.25,
    "bubble_video_path": os.path.join(script_dir, "bubble_simulation.mp4"),
    "bubble_csv_path": os.path.join(script_dir, "bubble_data.csv"),
}

script_descriptions = {
    "IPI_generator.py": "Generates synthetic videos of moving disks, simulating typical Interferometric Particle Imaging (IPI) patterns. \n" \
                        "Customize disk size, speed, transparency, background, and post-processing effects. \n" \
                        "Optional blobs can be added to increase detection difficulty for benchmarking algorithms.",
    "bubble_generator.py": "Generates a video of bubbles rising in columns. Customize bubble properties, spawn rate, and radius behavior."
}

def update_param(sender, app_data, user_data):
    """Update user_params when a UI element is changed."""
    param_name = user_data
    user_params[param_name] = app_data
    update_ui_visibility()

def update_ui_visibility():
    """Show or hide UI elements based on the selected script."""
    selected_script = user_params["script"]
    if selected_script == "IPI_generator.py":
        dpg.hide_item("bubble_parameters_group")
        dpg.show_item("circle_parameters_group")
    else:
        dpg.hide_item("circle_parameters_group")
        dpg.show_item("bubble_parameters_group")
    dpg.set_value("script_description", script_descriptions[selected_script])

def show_help():
    """Show help window with user manual."""
    manual_path = os.path.join(script_dir, "user_manual.txt")
    try:
        with open(manual_path, "r") as f:
            manual_text = f.read()
        if not dpg.does_item_exist("help_window"):
            with dpg.window(label="Help - User Manual", width=600, height=500, tag="help_window", modal=True, no_scrollbar=True):
                dpg.add_text(manual_text)
                dpg.add_button(label="Close", callback=lambda: dpg.hide_item("help_window"))
        else:
            dpg.show_item("help_window")
    except FileNotFoundError:
        dpg.set_value("status", f"Error: Could not find user_manual.txt at {manual_path}")

def generate_video():
    """Run the selected script with the current parameters."""
    script_path = os.path.join(script_dir, user_params["script"])
    command = ["python", script_path]
    if user_params["script"] == "IPI_generator.py":
        command.extend([
            "--rmin", str(user_params["rmin"]),
            "--rmax", str(user_params["rmax"]),
            "--vitx", str(user_params["vitx"]),
            "--vity", str(user_params["vity"]),
            "--fps", str(user_params["fps"]),
            "--video_duration", str(user_params["video_duration"]),
            "--n_circles", str(user_params["n_circles"]),
            "--n_blobs", str(user_params["n_blobs"]),
            "--apply_blur", "1" if user_params["apply_blur"] else "0",
            "--blur_radius", str(user_params["blur_radius"]),
            "--apply_rotation", "1" if user_params["apply_rotation"] else "0",
            "--use_background_image", "1" if user_params["use_background_image"] else "0",
            "--background_image_path", user_params["background_image_path"],
            "--save_path", user_params["save_path"],
            "--output_video_path", user_params["output_video_path"],
        ])
    else:
        command.extend([
            "--width", str(user_params["bubble_width"]),
            "--height", str(user_params["bubble_height"]),
            "--fps", str(user_params["bubble_fps"]),
            "--duration", str(user_params["bubble_duration"]),
            "--spawn_interval", str(user_params["bubble_spawn_interval"]),
            "--large_radius_probability", str(user_params["large_radius_probability"]),
            "--radius_decrease_factor", str(user_params["radius_decrease_factor"]),
            "--video_path", user_params["bubble_video_path"],
            "--csv_path", user_params["bubble_csv_path"],
        ])
    dpg.set_value("status", "Generating video...")
    dpg.set_value("log_window", "")
    def run():
        try:
            result = subprocess.run(
                command,
                check=True,
                text=True,
                capture_output=True,
                cwd=script_dir
            )
            dpg.set_value("log_window", result.stdout)
            dpg.set_value("status", "Video generated successfully!")
        except subprocess.CalledProcessError as e:
            dpg.set_value("log_window", e.stderr)
            dpg.set_value("status", "Error generating video.")
    threading.Thread(target=run).start()

def create_ui():
    with dpg.window(label="Video Generator", width=800, height=900, no_scrollbar=True):
        # Create a drawing for the title
        with dpg.drawlist(width=770, height=100):  # Increased height from 60 to 80
            # Draw a blue rectangle as background
            dpg.draw_rectangle((0, 0), (770, 100), fill=(30, 30, 50))  # Adjusted rectangle height
            # Draw title text
            dpg.draw_text((20, 20), "SYNTHETIC VIDEO GENERATOR", color=(200, 200, 255), size=24)
            dpg.draw_text((20, 45), "Generate Videos for Algorithm Testing & Benchmarking", color=(150, 200, 255), size=16)
            dpg.draw_text((20, 65), "Lucas Rotily", color=(100, 200, 255), size=16)
        # Add some space
        dpg.add_text("")
        # Help button and script selection in the same row
        with dpg.group(horizontal=True):
            dpg.add_text("Select Script:")
            dpg.add_combo(
                ["IPI_generator.py", "bubble_generator.py"],
                default_value="IPI_generator.py",
                tag="script_selector",
                callback=update_param,
                user_data="script"
            )
            dpg.add_button(label="?", callback=show_help, width=30)
        dpg.add_text("", tag="script_description")
        # Circle Video Parameters
        with dpg.group(tag="circle_parameters_group"):
            dpg.add_text("Circle Parameters:")
            dpg.add_slider_int(
                label="Minimum Radius (rmin)",
                tag="rmin_slider",
                min_value=10,
                max_value=100,
                default_value=user_params["rmin"],
                callback=update_param,
                user_data="rmin"
            )
            dpg.add_slider_int(
                label="Maximum Radius (rmax)",
                tag="rmax_slider",
                min_value=10,
                max_value=100,
                default_value=user_params["rmax"],
                callback=update_param,
                user_data="rmax"
            )
            dpg.add_slider_int(
                label="Vertical Velocity (vitx)",
                tag="vitx_slider",
                min_value=1,
                max_value=50,
                default_value=user_params["vitx"],
                callback=update_param,
                user_data="vitx"
            )
            dpg.add_slider_int(
                label="Horizontal Velocity (vity)",
                tag="vity_slider",
                min_value=1,
                max_value=50,
                default_value=user_params["vity"],
                callback=update_param,
                user_data="vity"
            )
            dpg.add_text("Video Parameters:")
            dpg.add_slider_int(
                label="FPS",
                tag="fps_slider",
                min_value=1,
                max_value=60,
                default_value=user_params["fps"],
                callback=update_param,
                user_data="fps"
            )
            dpg.add_slider_int(
                label="Video Duration (seconds)",
                tag="duration_slider",
                min_value=1,
                max_value=10,
                default_value=user_params["video_duration"],
                callback=update_param,
                user_data="video_duration"
            )
            dpg.add_text("Image Parameters:")
            dpg.add_slider_int(
                label="Number of Circles",
                tag="n_circles_slider",
                min_value=1,
                max_value=50,
                default_value=user_params["n_circles"],
                callback=update_param,
                user_data="n_circles"
            )
            dpg.add_slider_int(
                label="Number of Blobs",
                tag="n_blobs_slider",
                min_value=0,
                max_value=20,
                default_value=user_params["n_blobs"],
                callback=update_param,
                user_data="n_blobs"
            )
            dpg.add_text("Background Image:")
            dpg.add_checkbox(
                label="Use Background Image",
                tag="bg_checkbox",
                default_value=user_params["use_background_image"],
                callback=update_param,
                user_data="use_background_image"
            )
            dpg.add_input_text(
                label="Background Image Path",
                tag="bg_path_input",
                default_value=user_params["background_image_path"],
                callback=update_param,
                user_data="background_image_path"
            )
            dpg.add_text("Post-Processing:")
            dpg.add_checkbox(
                label="Apply Blur",
                tag="blur_checkbox",
                default_value=user_params["apply_blur"],
                callback=update_param,
                user_data="apply_blur"
            )
            dpg.add_slider_int(
                label="Gaussian Blur Radius",
                tag="blur_radius_slider",
                min_value=1,
                max_value=20,
                default_value=user_params["blur_radius"],
                callback=update_param,
                user_data="blur_radius"
            )
            dpg.add_checkbox(
                label="Apply Rotation",
                tag="rotation_checkbox",
                default_value=user_params["apply_rotation"],
                callback=update_param,
                user_data="apply_rotation"
            )
            dpg.add_text("Paths:")
            dpg.add_input_text(
                label="Save Path",
                tag="save_path_input",
                default_value=user_params["save_path"],
                callback=update_param,
                user_data="save_path"
            )
            dpg.add_input_text(
                label="Output Video Path",
                tag="output_path_input",
                default_value=user_params["output_video_path"],
                callback=update_param,
                user_data="output_video_path"
            )
        # Bubble Simulation Parameters
        with dpg.group(tag="bubble_parameters_group", show=False):
            dpg.add_text("Video Parameters:")
            dpg.add_slider_int(
                label="Width",
                tag="bubble_width_slider",
                min_value=200,
                max_value=2000,
                default_value=user_params["bubble_width"],
                callback=update_param,
                user_data="bubble_width"
            )
            dpg.add_slider_int(
                label="Height",
                tag="bubble_height_slider",
                min_value=200,
                max_value=2000,
                default_value=user_params["bubble_height"],
                callback=update_param,
                user_data="bubble_height"
            )
            dpg.add_slider_int(
                label="FPS",
                tag="bubble_fps_slider",
                min_value=1,
                max_value=60,
                default_value=user_params["bubble_fps"],
                callback=update_param,
                user_data="bubble_fps"
            )
            dpg.add_slider_int(
                label="Duration (seconds)",
                tag="bubble_duration_slider",
                min_value=1,
                max_value=30,
                default_value=user_params["bubble_duration"],
                callback=update_param,
                user_data="bubble_duration"
            )
            dpg.add_text("Bubble Parameters:")
            dpg.add_slider_float(
                label="Spawn Interval (seconds)",
                tag="bubble_spawn_interval_slider",
                min_value=0.1,
                max_value=2.0,
                default_value=user_params["bubble_spawn_interval"],
                callback=update_param,
                user_data="bubble_spawn_interval"
            )
            dpg.add_slider_float(
                label="Large Radius Probability",
                tag="large_radius_probability_slider",
                min_value=0.0,
                max_value=1.0,
                default_value=user_params["large_radius_probability"],
                callback=update_param,
                user_data="large_radius_probability"
            )
            dpg.add_slider_float(
                label="Radius Decrease Factor",
                tag="radius_decrease_factor_slider",
                min_value=0.01,
                max_value=1.0,
                default_value=user_params["radius_decrease_factor"],
                callback=update_param,
                user_data="radius_decrease_factor"
            )
            dpg.add_text("Output Paths:")
            dpg.add_input_text(
                label="Video Path",
                tag="bubble_video_path_input",
                default_value=user_params["bubble_video_path"],
                callback=update_param,
                user_data="bubble_video_path"
            )
            dpg.add_input_text(
                label="CSV Path",
                tag="bubble_csv_path_input",
                default_value=user_params["bubble_csv_path"],
                callback=update_param,
                user_data="bubble_csv_path"
            )
        dpg.add_button(
            label="Generate Video",
            callback=lambda: generate_video()
        )
        dpg.add_text("Status:", tag="status")
        dpg.add_input_text(
            tag="log_window",
            multiline=True,
            readonly=True,
            width=-1,
            height=100
        )

dpg.create_context()
create_ui()
dpg.create_viewport(title="Video Generator", width=820, height=950)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
