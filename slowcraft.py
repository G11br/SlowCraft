import os
import cv2
import shutil
import tempfile
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

APP_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG_EXEC = os.path.join(APP_DIR, "ffmpeg.exe")
RIFE_EXEC = os.path.join(APP_DIR, "rife-ncnn-vulkan.exe")
RIFE_MODEL = os.path.join(APP_DIR, "models", "rife-v4.6")

if sys.platform == "win32":
    CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW
else:
    CREATE_NO_WINDOW = 0

class SlowMoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SlowCraft")
        self.root.geometry("900x1000")

        self.video_path = None
        self.cap = None
        self.playing = False
        self.duration = 0
        self.temp_dir = tempfile.mkdtemp()

        self.create_widgets()

    def create_widgets(self):
        self.video_label = tk.Label(self.root, text="Upload a video")
        self.video_label.pack(pady=5, expand=True, fill="both")

        self.thumbnail = tk.Label(self.root)
        self.thumbnail.pack()

        self.duration_label = tk.Label(self.root, text="Duration: N/A")
        self.duration_label.pack()

        self.full_video_mode = tk.BooleanVar()
        self.full_video_check = tk.Checkbutton(
            self.root, text="Convert entire video", variable=self.full_video_mode,
            command=self.toggle_time_controls
        )
        self.full_video_check.pack()

        self.start_slider = tk.Scale(self.root, from_=0, to=100, orient="horizontal", length=600,
                                     label="Start Time", showvalue=True, command=self.update_start_time)
        self.start_slider.pack()
        self.start_slider.configure(state="disabled")

        self.end_slider = tk.Scale(self.root, from_=0, to=100, orient="horizontal", length=600,
                                   label="End Time", showvalue=True, command=self.update_end_time)
        self.end_slider.pack()
        self.end_slider.configure(state="disabled")

        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=5)

        tk.Label(control_frame, text="Start Time (s):").grid(row=0, column=0)
        self.start_entry = tk.Entry(control_frame, width=6)
        self.start_entry.grid(row=0, column=1, padx=5)

        tk.Label(control_frame, text="End Time (s):").grid(row=0, column=2)
        self.end_entry = tk.Entry(control_frame, width=6)
        self.end_entry.grid(row=0, column=3, padx=5)

        tk.Label(control_frame, text="SlowMo Factor (2/4/8):").grid(row=0, column=4)
        self.factor_entry = tk.Entry(control_frame, width=4)
        self.factor_entry.grid(row=0, column=5, padx=5)
        self.factor_entry.bind("<KeyRelease>", self.update_estimated_duration)

        self.output_estimate_label = tk.Label(self.root, text="Estimated output duration: N/A")
        self.output_estimate_label.pack()

        enhance_frame = tk.Frame(self.root)
        enhance_frame.pack(pady=5)
        self.enhance_video = tk.BooleanVar()
        self.enhance_checkbox = tk.Checkbutton(enhance_frame, text="Enhance Video Quality", variable=self.enhance_video)
        self.enhance_checkbox.pack(side="left")

        self.brightness_var = tk.DoubleVar(value=0.0)
        self.brightness_var.trace("w", self.update_brightness_preview)
        tk.Label(enhance_frame, text="Brightness:").pack(side="left")
        self.brightness_slider = tk.Scale(enhance_frame, from_=-1.0, to=1.0, resolution=0.1,
                                          orient="horizontal", variable=self.brightness_var, length=200)
        self.brightness_slider.pack(side="left")

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Upload Video", command=self.load_video).pack(side="left", padx=10)
        tk.Button(button_frame, text="Play/Pause", command=self.toggle_playback).pack(side="left", padx=10)
        tk.Button(button_frame, text="Generate SlowMo", command=self.process_video).pack(side="left", padx=10)

        self.status = tk.StringVar()
        self.status.set("Ready.")
        self.status_label = tk.Label(self.root, textvariable=self.status, anchor="w", relief="sunken")
        self.status_label.pack(side="bottom", fill="x")

    def set_status(self, msg):
        self.status.set(msg)
        self.root.update_idletasks()

    def toggle_time_controls(self):
        state = "disabled" if self.full_video_mode.get() else "normal"
        for widget in [self.start_slider, self.end_slider, self.start_entry, self.end_entry]:
            widget.configure(state=state)
        self.update_estimated_duration()

    def update_start_time(self, value):
        self.start_entry.delete(0, tk.END)
        self.start_entry.insert(0, str(int(value)))
        self.update_estimated_duration()

    def update_end_time(self, value):
        self.end_entry.delete(0, tk.END)
        self.end_entry.insert(0, str(int(value)))
        self.update_estimated_duration()

    def update_estimated_duration(self, event=None):
        try:
            factor = int(self.factor_entry.get().replace('x', ''))
            if self.full_video_mode.get():
                seg = self.duration
            else:
                seg = float(self.end_entry.get()) - float(self.start_entry.get())
            new_time = round(seg * factor, 2)
            self.output_estimate_label.config(text=f"Estimated output duration: {new_time} seconds")
        except:
            self.output_estimate_label.config(text="Estimated output duration: N/A")

    def load_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.mov *.avi")])
        if file_path:
            self.video_path = file_path
            self.cap = cv2.VideoCapture(self.video_path)
            self.set_status("Video loaded.")
            self.playing = False

            frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.duration = round(frames / fps, 2) if fps else 0
            self.duration_label.config(text=f"Duration: {self.duration} seconds")

            self.start_slider.configure(state="normal", to=int(self.duration), resolution=1)
            self.end_slider.configure(state="normal", to=int(self.duration), resolution=1)
            self.start_slider.set(0)
            self.end_slider.set(min(5, int(self.duration)))
            self.update_start_time(0)
            self.update_end_time(min(5, int(self.duration)))

            self.toggle_time_controls()

            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (320, 180))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.thumbnail.config(image=imgtk)
                self.thumbnail.image = imgtk

    def toggle_playback(self):
        if not self.cap:
            return
        self.playing = not self.playing
        if self.playing:
            self._stream()

    def _stream(self):
        if not self.playing or not self.cap:
            return
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (800, 450))
            brightness = self.brightness_var.get()
            frame = cv2.convertScaleAbs(frame, alpha=1, beta=int(brightness * 50))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk)

            current_time = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            self.end_slider.set(int(current_time))
            self.end_entry.delete(0, tk.END)
            self.end_entry.insert(0, str(int(current_time)))

            self.root.after(33, self._stream)
        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.playing = False

    def update_brightness_preview(self, *args):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (800, 450))
                brightness = self.brightness_var.get()
                frame = cv2.convertScaleAbs(frame, alpha=1, beta=int(brightness * 50))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.config(image=imgtk)

    def process_video(self):
        if not self.video_path:
            messagebox.showerror("No video", "Please upload a video first.")
            return
        if not os.path.exists(RIFE_MODEL):
            messagebox.showerror("Missing Model", f"Model not found: {RIFE_MODEL}")
            return
        try:
            if self.full_video_mode.get():
                start = 0
                end = self.duration
            else:
                start = float(self.start_entry.get())
                end = float(self.end_entry.get())

            factor = int(self.factor_entry.get().replace('x', ''))
        except ValueError:
            messagebox.showerror("Input Error", "Invalid time or factor.")
            return

        threading.Thread(target=self._run_pipeline, args=(start, end, factor, None)).start()

    def _detect_ffmpeg_pattern(self, folder):
        files = sorted(f for f in os.listdir(folder) if f.endswith(".png"))
        if not files:
            return None
        first_file = files[0]
        num_digits = len(os.path.splitext(first_file)[0])
        return f"%0{num_digits}d.png"

    def _run_pipeline(self, start, end, factor, _):
        self.set_status("Extracting segment...")
        input_clip = os.path.join(self.temp_dir, "clip.mp4")
        extracted_dir = os.path.join(self.temp_dir, "frames")
        os.makedirs(extracted_dir, exist_ok=True)

        subprocess.run([
            FFMPEG_EXEC, "-y", "-i", self.video_path,
            "-ss", str(start), "-to", str(end),
            "-c:v", "libx264", "-an", input_clip
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)

        self.set_status("Extracting frames...")
        subprocess.run([
            FFMPEG_EXEC, "-y", "-i", input_clip,
            os.path.join(extracted_dir, "%05d.png")
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)

        input_dir = extracted_dir
        passes = factor.bit_length() - 1

        for i in range(passes):
            self.set_status(f"RIFE Pass {i+1} of {passes}...")
            output_dir = os.path.join(self.temp_dir, f"interp_{i+1}")
            os.makedirs(output_dir, exist_ok=True)

            result = subprocess.run([
                RIFE_EXEC, "-i", input_dir, "-o", output_dir, "-m", RIFE_MODEL
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=CREATE_NO_WINDOW)

            if not any(fname.endswith(".png") for fname in os.listdir(output_dir)):
                self.set_status("❌ RIFE produced no frames.")
                messagebox.showerror("RIFE Error", f"No frames generated.\n\nError:\n{result.stderr.decode()}")
                return

            input_dir = output_dir

        self.set_status("Reassembling video...")
        pattern = self._detect_ffmpeg_pattern(input_dir)
        if not pattern:
            self.set_status("❌ No output frames found.")
            messagebox.showerror("Error", "No interpolated frames found.")
            return

        final_frames = os.path.join(input_dir, pattern)
        slowmo_video = os.path.join(self.temp_dir, "slowmo.mp4")

        filters = []
        brightness = self.brightness_var.get()
        if brightness != 0.0:
            filters.append(f"eq=brightness={brightness}")
        if self.enhance_video.get():
            filters.append("unsharp=7:7:1.0:7:7:0.0")
        # Add denoise filter
        filters.append("hqdn3d=4.0:3.0:6.0:4.5")
        vf_chain = ",".join(filters)

        # Fix: Use lower output FPS for slowmo effect
        output_fps = max(self.cap.get(cv2.CAP_PROP_FPS) / factor, 1)
        cmd = [FFMPEG_EXEC, "-y", "-framerate", str(output_fps), "-i", final_frames]
        if vf_chain:
            cmd += ["-vf", vf_chain]
        cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow", "-r", str(output_fps), slowmo_video]

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)

        if not os.path.exists(slowmo_video):
            self.set_status("❌ Failed to create slowmo.mp4.")
            messagebox.showerror("Error", "slowmo.mp4 was not created.")
            return

        self.set_status("Merging audio and saving output...")
        output_file = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 Video", "*.mp4")],
            title="Save your slowmo video as"
        )

        if output_file:
            result = subprocess.run([
                FFMPEG_EXEC, "-y", "-i", slowmo_video, "-i", input_clip,
                "-c:v", "copy", "-map", "0:v:0", "-map", "1:a:0?", "-shortest", output_file
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=CREATE_NO_WINDOW)

            if os.path.exists(output_file):
                self.set_status("✅ Done! SlowMo saved.")
                messagebox.showinfo("Success", f"Video saved to:\n{output_file}")
            else:
                self.set_status("❌ Failed to save video.")
                messagebox.showerror("Error", f"FFmpeg failed to save video.\n\n{result.stderr.decode()}")
        else:
            self.set_status("Save canceled.")

    def cleanup(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        if self.cap:
            self.cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = SlowMoApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.cleanup(), root.destroy()))
    root.mainloop()
