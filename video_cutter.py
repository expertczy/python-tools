import tkinter as tk
from tkinter import filedialog, messagebox
from moviepy.editor import VideoFileClip
import os
import subprocess

class VideoCutterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Cutter")
        self.root.geometry("600x400")
        
        # Variables
        self.video_path = tk.StringVar()
        self.start_time = tk.StringVar()
        self.end_time = tk.StringVar()
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # File selection
        tk.Label(self.root, text="Video File:").pack(pady=10)
        tk.Entry(self.root, textvariable=self.video_path, width=50).pack()
        tk.Button(self.root, text="Browse", command=self.browse_file).pack(pady=5)
        
        # Time inputs
        time_frame = tk.Frame(self.root)
        time_frame.pack(pady=20)
        
        tk.Label(time_frame, text="Start Time (HH:MM:SS):").grid(row=0, column=0, padx=5)
        tk.Entry(time_frame, textvariable=self.start_time).grid(row=0, column=1, padx=5)
        
        tk.Label(time_frame, text="End Time (HH:MM:SS):").grid(row=1, column=0, padx=5)
        tk.Entry(time_frame, textvariable=self.end_time).grid(row=1, column=1, padx=5)
        
        # Cut button
        tk.Button(self.root, text="Cut Video", command=self.cut_video).pack(pady=20)
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mkv *.mov"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.video_path.set(filename)
            
    def time_to_seconds(self, time_str):
        try:
            h, m, s = map(int, time_str.split(':'))
            return h * 3600 + m * 60 + s
        except:
            raise ValueError("Invalid time format. Please use HH:MM:SS")
            
    def cut_with_ffmpeg(self, input_path, output_path, start_seconds, end_seconds):
        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output file without asking
            "-ss", str(start_seconds),
            "-to", str(end_seconds),
            "-i", input_path,
            "-c", "copy",
            output_path
        ]
        subprocess.run(cmd, check=True)
            
    def cut_video(self):
        try:
            video_path = self.video_path.get()
            if not video_path:
                messagebox.showerror("Error", "Please select a video file")
                return
            start_seconds = self.time_to_seconds(self.start_time.get())
            end_seconds = self.time_to_seconds(self.end_time.get())
            if start_seconds >= end_seconds:
                messagebox.showerror("Error", "End time must be greater than start time")
                return
            output_path = filedialog.asksaveasfilename(
                defaultextension=".mp4",
                filetypes=[("MP4 files", "*.mp4")],
                initialfile="cut_video.mp4"
            )
            if not output_path:
                return
            try:
                self.cut_with_ffmpeg(video_path, output_path, start_seconds, end_seconds)
                messagebox.showinfo("Success", "Video cut successfully (fast mode)!")
            except Exception as ffmpeg_error:
                try:
                    video = VideoFileClip(video_path)
                    if end_seconds > video.duration:
                        messagebox.showerror("Error", "End time exceeds video duration")
                        return
                    cut_video = video.subclip(start_seconds, end_seconds)
                    cut_video.write_videofile(
                        output_path,
                        codec="libx264",
                        preset="ultrafast",
                        threads=4
                    )
                    video.close()
                    cut_video.close()
                    messagebox.showinfo("Success", "Video cut successfully (MoviePy fallback)!")
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {str(e)}")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCutterApp(root)
    root.mainloop()
