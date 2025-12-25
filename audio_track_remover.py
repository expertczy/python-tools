#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio Track Remover Tool
用于删除MKV、MP4等视频文件中的不需要的音轨

支持两种模式：
- 命令行模式：python audio_track_remover.py <video_file>
- GUI模式：python audio_track_remover.py --gui
"""

import os
import sys
import subprocess
import json
import locale
from pathlib import Path

# 设置控制台编码
if sys.platform == 'win32':
    try:
        # 设置控制台输出编码为UTF-8
        os.system('chcp 65001 > nul')
    except:
        pass


def run_ffmpeg_command(cmd):
    """Run ffmpeg command and return result"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def get_video_info(file_path):
    """Get video file information"""
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        str(file_path)
    ]

    success, stdout, stderr = run_ffmpeg_command(cmd)
    if not success:
        print(f"Failed to get video info: {stderr}")
        return None

    try:
        data = json.loads(stdout)
        return data
    except json.JSONDecodeError:
        print("Failed to parse video info")
        return None


def list_audio_tracks(video_info):
    """List all audio tracks in video file"""
    streams = video_info.get('streams', [])
    audio_tracks = []

    for i, stream in enumerate(streams):
        if stream.get('codec_type') == 'audio':
            track_info = {
                'index': i,
                'stream_index': stream.get('index'),
                'codec': stream.get('codec_name', 'unknown'),
                'language': stream.get('tags', {}).get('language', 'und'),
                'title': stream.get('tags', {}).get('title', ''),
                'channels': stream.get('channels', 'unknown'),
                'sample_rate': stream.get('sample_rate', 'unknown'),
                'bitrate': stream.get('bit_rate', 'unknown')
            }
            audio_tracks.append(track_info)

    return audio_tracks


def display_audio_tracks(audio_tracks):
    """Display audio track information"""
    if not audio_tracks:
        print("No audio tracks found")
        return

    print("\nFound audio tracks:")
    print("-" * 80)
    print("No. | Lang | Title | Channels | Sample Rate | Bitrate | Codec")
    print("-" * 80)

    for i, track in enumerate(audio_tracks, 1):
        language = track['language']
        title = track['title'][:20] if track['title'] else ''
        channels = track['channels']
        sample_rate = track['sample_rate']
        bitrate = track['bitrate']
        codec = track['codec']

        # 格式化比特率
        if bitrate != 'unknown':
            bitrate = f"{int(bitrate)//1000}kbps"

        print("3d")


def select_tracks_to_keep(audio_tracks):
    """Let user select tracks to keep"""
    if len(audio_tracks) <= 1:
        print("Only one audio track found, no selection needed")
        return [0] if audio_tracks else []

    print("\nSelect tracks to keep (enter numbers separated by commas, or 'all' to keep all):")
    print("Example: 1,2 or 1 or all")

    while True:
        choice = input("Select: ").strip().lower()

        if choice == 'all':
            return list(range(len(audio_tracks)))

        try:
            indices = [int(x.strip()) - 1 for x in choice.split(',')]
            if all(0 <= i < len(audio_tracks) for i in indices):
                return indices
            else:
                print("Invalid track numbers, please try again")
        except ValueError:
            print("Invalid input format, please try again")


def remove_audio_tracks(input_file, output_file, tracks_to_keep, audio_tracks):
    """Remove unwanted audio tracks"""
    # Build ffmpeg command
    cmd = ['ffmpeg', '-i', str(input_file), '-map', '0:v']  # Keep all video tracks

    # Add audio tracks to keep
    for i in tracks_to_keep:
        if i < 0 or i >= len(audio_tracks):
            error_msg = f"Error: Invalid track index {i} (valid range: 0-{len(audio_tracks)-1})"
            print(error_msg)
            return False

        track = audio_tracks[i]
        stream_index = track['stream_index']
        cmd.extend(['-map', f'0:{stream_index}'])

    # Copy all subtitle tracks (if any)
    cmd.extend(['-map', '0:s?', '-c', 'copy', str(output_file)])

    print("Running command:", ' '.join(cmd))

    success, stdout, stderr = run_ffmpeg_command(cmd)
    if success:
        print(f"Processing completed! Output file: {output_file}")
        return True
    else:
        print(f"Processing failed: {stderr}")
        return False


def process_video_file(file_path):
    """Process single video file"""
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return

    print(f"\nProcessing file: {file_path}")

    # Get video information
    video_info = get_video_info(file_path)
    if not video_info:
        return

    # List audio tracks
    audio_tracks = list_audio_tracks(video_info)
    if not audio_tracks:
        print("No audio tracks found in this file")
        return

    # Display audio tracks
    display_audio_tracks(audio_tracks)

    # Select tracks to keep
    tracks_to_keep = select_tracks_to_keep(audio_tracks)

    if not tracks_to_keep:
        print("No tracks selected to keep, skipping processing")
        return

    # Generate output filename
    stem = file_path.stem
    suffix = file_path.suffix
    output_file = file_path.parent / f"{stem}_cleaned{suffix}"

    # If output file exists, ask for confirmation
    if output_file.exists():
        choice = input(f"Output file already exists: {output_file}\nOverwrite? (y/n): ").strip().lower()
        if choice != 'y':
            print("Processing cancelled")
            return

    # Remove unwanted audio tracks
    print(f"\nKeeping tracks: {[i+1 for i in tracks_to_keep]}")
    success = remove_audio_tracks(file_path, output_file, tracks_to_keep, audio_tracks)

    if success:
        # 显示文件大小对比
        input_size = file_path.stat().st_size
        output_size = output_file.stat().st_size
        print(".1f")
        print(".1f")


def check_dependencies():
    """Check dependencies"""
    # Check ffmpeg
    success, _, _ = run_ffmpeg_command(['ffmpeg', '-version'])
    if not success:
        print("Error: ffmpeg not found, please install ffmpeg")
        print("Download from: https://ffmpeg.org/download.html")
        return False

    # Check ffprobe
    success, _, _ = run_ffmpeg_command(['ffprobe', '-version'])
    if not success:
        print("Error: ffprobe not found, please ensure ffmpeg is properly installed")
        return False

    return True


# GUI相关导入 - 只有在使用GUI时才需要
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk, scrolledtext
    import threading
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False


class AudioTrackRemoverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Track Remover v1.0")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # 变量
        self.input_file = None
        self.audio_tracks = []
        self.selected_tracks = []
        self.processing = False

        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="5")
        file_frame.pack(fill=tk.X, pady=(0, 10))

        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(file_frame, text="Browse...", command=self.select_file).pack(side=tk.RIGHT)

        # 音轨信息区域
        tracks_frame = ttk.LabelFrame(main_frame, text="Audio Tracks - Click any row to toggle Keep/Delete", padding="5")
        tracks_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 创建Treeview来显示音轨
        columns = ("No.", "Language", "Title", "Channels", "Sample Rate", "Bitrate", "Codec", "Keep?")
        self.tracks_tree = ttk.Treeview(tracks_frame, columns=columns, show="headings", height=8)

        # 设置列标题和宽度
        column_widths = {
            "No.": 50,
            "Language": 70,
            "Title": 120,
            "Channels": 70,
            "Sample Rate": 90,
            "Bitrate": 80,
            "Codec": 80,
            "Keep?": 60
        }
        
        for col in columns:
            self.tracks_tree.heading(col, text=col)
            width = column_widths.get(col, 80)
            anchor = "center" if col == "Keep?" else "w"  # "w" = west (left), "center" = center
            self.tracks_tree.column(col, width=width, anchor=anchor)

        # 添加滚动条
        v_scrollbar = ttk.Scrollbar(tracks_frame, orient=tk.VERTICAL, command=self.tracks_tree.yview)
        self.tracks_tree.configure(yscrollcommand=v_scrollbar.set)

        self.tracks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定选择事件 - 整行都可以点击
        self.tracks_tree.bind('<Button-1>', self.on_track_click)
        self.tracks_tree.bind('<Double-Button-1>', self.on_track_click)
        
        # 添加提示标签
        hint_label = ttk.Label(tracks_frame, text="💡 Tip: Click on any row or the 'Keep?' column to toggle track selection", 
                               font=('TkDefaultFont', 8), foreground='gray')
        hint_label.pack(side=tk.BOTTOM, pady=(5, 0))

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        self.select_all_btn = ttk.Button(button_frame, text="Keep All", command=self.select_all_tracks, state=tk.DISABLED)
        self.select_all_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.select_none_btn = ttk.Button(button_frame, text="Delete All", command=self.select_none_tracks, state=tk.DISABLED)
        self.select_none_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.process_btn = ttk.Button(button_frame, text="Process & Remove Unselected Tracks", command=self.process_file, state=tk.DISABLED)
        self.process_btn.pack(side=tk.RIGHT)

        # 进度和状态区域
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="5")
        status_frame.pack(fill=tk.BOTH, expand=True)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))

        # 状态文本
        self.status_text = scrolledtext.ScrolledText(status_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        self.status_text.pack(fill=tk.BOTH, expand=True)

        # 检查依赖
        self.check_dependencies()

    def check_dependencies(self):
        """检查依赖"""
        success, _, _ = self.run_ffmpeg_command(['ffmpeg', '-version'])
        if not success:
            self.log_message("ERROR: FFmpeg not found. Please install FFmpeg first.")
            self.log_message("Download from: https://ffmpeg.org/download.html")
        else:
            self.log_message("FFmpeg found - ready to process files!")

    def select_file(self):
        """选择文件"""
        filetypes = [
            ('Video files', '*.mkv *.mp4 *.avi *.mov *.flv *.wmv *.m4v'),
            ('MKV files', '*.mkv'),
            ('MP4 files', '*.mp4'),
            ('All files', '*.*')
        ]

        filename = filedialog.askopenfilename(
            title="Select video file",
            filetypes=filetypes
        )

        if filename:
            self.input_file = Path(filename)
            self.file_path_var.set(str(self.input_file))
            self.log_message(f"Selected file: {self.input_file}")

            # 清空之前的音轨信息
            self.clear_tracks()
            
            # 自动开始分析
            self.analyze_file()

    def clear_tracks(self):
        """清空音轨显示"""
        for item in self.tracks_tree.get_children():
            self.tracks_tree.delete(item)
        self.audio_tracks = []
        self.selected_tracks = []
        self.select_all_btn.config(state=tk.DISABLED)
        self.select_none_btn.config(state=tk.DISABLED)
        self.process_btn.config(state=tk.DISABLED)

    def analyze_file(self):
        """分析文件"""
        if not self.input_file or not self.input_file.exists():
            messagebox.showerror("Error", "Please select a valid file first")
            return

        self.log_message("Analyzing file...")
        self.progress_var.set(10)

        # 在后台线程中运行分析
        threading.Thread(target=self._analyze_file_thread, daemon=True).start()

    def _analyze_file_thread(self):
        """分析文件的后台线程"""
        try:
            # 获取视频信息
            video_info = self.get_video_info(self.input_file)
            if not video_info:
                self.root.after(0, lambda: self.log_message("Failed to analyze file"))
                return

            # 列出音轨
            audio_tracks = self.list_audio_tracks(video_info)
            if not audio_tracks:
                self.root.after(0, lambda: self.log_message("No audio tracks found in this file"))
                return

            self.audio_tracks = audio_tracks

            # 更新UI（确保在主线程中更新）
            def update_ui():
                self.display_tracks(audio_tracks)
                self.progress_var.set(50)
                self.log_message(f"Found {len(audio_tracks)} audio track(s)")
            
            self.root.after(0, update_ui)

        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"Error analyzing file: {str(e)}"))

        finally:
            self.root.after(0, lambda: self.progress_var.set(0))

    def display_tracks(self, audio_tracks):
        """显示音轨信息"""
        # 先清空UI显示
        for item in self.tracks_tree.get_children():
            self.tracks_tree.delete(item)
        self.selected_tracks = []
        
        # 保存音轨数据（不清空self.audio_tracks，而是更新它）
        self.audio_tracks = audio_tracks

        for i, track in enumerate(audio_tracks, 1):
            # 格式化比特率
            bitrate = track['bitrate']
            if bitrate != 'unknown':
                bitrate = f"{int(bitrate)//1000}kbps"

            values = (
                str(i),
                track['language'],
                track['title'][:15] if track['title'] else '',
                track['channels'],
                track['sample_rate'],
                bitrate,
                track['codec'],
                "✓ Keep"  # 默认选择，显示为"✓ Keep"
            )

            item = self.tracks_tree.insert("", tk.END, values=values, tags=('selected',))
            # 确保索引是有效的
            track_index = i - 1
            if 0 <= track_index < len(audio_tracks):
                self.selected_tracks.append(track_index)

        self.select_all_btn.config(state=tk.NORMAL)
        self.select_none_btn.config(state=tk.NORMAL)
        self.process_btn.config(state=tk.NORMAL)

    def on_track_click(self, event):
        """处理音轨点击事件 - 整行都可以点击"""
        item = self.tracks_tree.identify_row(event.y)
        if item:
            # 点击整行都可以切换选择状态
            self.toggle_track_selection(item)

    def toggle_track_selection(self, item):
        """切换音轨选择状态"""
        current_values = self.tracks_tree.item(item, 'values')
        track_no = int(current_values[0]) - 1

        # 验证索引范围
        if track_no < 0 or track_no >= len(self.audio_tracks):
            return

        new_values = list(current_values)
        
        if track_no in self.selected_tracks:
            # 取消选择（将删除此音轨）
            self.selected_tracks.remove(track_no)
            new_values[7] = "✗ Delete"
            self.tracks_tree.item(item, values=new_values, tags=())
        else:
            # 选择（将保留此音轨）
            self.selected_tracks.append(track_no)
            new_values[7] = "✓ Keep"
            self.tracks_tree.item(item, values=new_values, tags=('selected',))

        self.update_process_button()

    def select_all_tracks(self):
        """选择所有音轨（保留所有）"""
        if not self.audio_tracks:
            return

        self.selected_tracks = list(range(len(self.audio_tracks)))
        for item in self.tracks_tree.get_children():
            values = list(self.tracks_tree.item(item, 'values'))
            values[7] = "✓ Keep"
            self.tracks_tree.item(item, values=values, tags=('selected',))

        self.update_process_button()

    def select_none_tracks(self):
        """取消选择所有音轨（删除所有）"""
        self.selected_tracks = []
        for item in self.tracks_tree.get_children():
            values = list(self.tracks_tree.item(item, 'values'))
            values[7] = "✗ Delete"
            self.tracks_tree.item(item, values=values, tags=())

        self.update_process_button()

    def update_process_button(self):
        """更新处理按钮状态"""
        if self.selected_tracks:
            self.process_btn.config(state=tk.NORMAL)
        else:
            self.process_btn.config(state=tk.DISABLED)

    def process_file(self):
        """处理文件"""
        if not self.selected_tracks:
            messagebox.showwarning("Warning", "Please select at least one audio track to keep")
            return

        # 验证选择的数据
        if not self.audio_tracks:
            messagebox.showerror("Error", "No audio tracks available. Please analyze the file first.")
            return

        # 检查索引有效性
        invalid_indices = [i for i in self.selected_tracks if i < 0 or i >= len(self.audio_tracks)]
        if invalid_indices:
            messagebox.showerror("Error", f"Invalid track indices found: {invalid_indices}")
            return

        # 生成输出文件名
        stem = self.input_file.stem
        suffix = self.input_file.suffix
        output_file = self.input_file.parent / f"{stem}_cleaned{suffix}"

        # 检查输出文件是否存在
        if output_file.exists():
            result = messagebox.askyesno("File exists",
                                       f"Output file already exists:\n{output_file}\n\nOverwrite?")
            if not result:
                return

        total_tracks = len(self.audio_tracks)
        tracks_to_keep = len(self.selected_tracks)
        tracks_to_delete = total_tracks - tracks_to_keep
        
        self.log_message(f"Processing file...")
        self.log_message(f"  - Total tracks: {total_tracks}")
        self.log_message(f"  - Keeping: {tracks_to_keep} track(s)")
        self.log_message(f"  - Deleting: {tracks_to_delete} track(s)")
        
        self.process_btn.config(state=tk.DISABLED)
        self.progress_var.set(20)

        # 在后台线程中运行处理
        threading.Thread(target=self._process_file_thread,
                        args=(output_file,),
                        daemon=True).start()

    def _process_file_thread(self, output_file):
        """处理文件的后台线程"""
        try:
            self.root.after(0, lambda: self.progress_var.set(50))

            success = self.remove_audio_tracks(self.input_file, output_file, self.selected_tracks, self.audio_tracks)

            if success:
                self.root.after(0, lambda: self.progress_var.set(100))
                self.root.after(0, lambda: self.log_message(f"Processing completed! Output file: {output_file}"))

                # 显示文件大小对比
                input_size = self.input_file.stat().st_size
                output_size = output_file.stat().st_size
                size_msg = ".1f"
                self.root.after(0, lambda: self.log_message(size_msg))

                messagebox.showinfo("Success", f"File processed successfully!\nSaved as: {output_file}")
            else:
                self.root.after(0, lambda: self.log_message("Processing failed"))
                messagebox.showerror("Error", "Failed to process file")

        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"Error: {str(e)}"))
            messagebox.showerror("Error", f"Processing failed: {str(e)}")

        finally:
            self.root.after(0, lambda: self.process_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.progress_var.set(0))

    def run_ffmpeg_command(self, cmd):
        """Run ffmpeg command and return result"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)

    def get_video_info(self, file_path):
        """Get video file information"""
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(file_path)
        ]

        success, stdout, stderr = self.run_ffmpeg_command(cmd)
        if not success:
            return None

        try:
            data = json.loads(stdout)
            return data
        except json.JSONDecodeError:
            return None

    def list_audio_tracks(self, video_info):
        """List all audio tracks in video file"""
        streams = video_info.get('streams', [])
        audio_tracks = []

        for i, stream in enumerate(streams):
            if stream.get('codec_type') == 'audio':
                track_info = {
                    'index': i,
                    'stream_index': stream.get('index'),
                    'codec': stream.get('codec_name', 'unknown'),
                    'language': stream.get('tags', {}).get('language', 'und'),
                    'title': stream.get('tags', {}).get('title', ''),
                    'channels': stream.get('channels', 'unknown'),
                    'sample_rate': stream.get('sample_rate', 'unknown'),
                    'bitrate': stream.get('bit_rate', 'unknown')
                }
                audio_tracks.append(track_info)

        return audio_tracks

    def remove_audio_tracks(self, input_file, output_file, tracks_to_keep, audio_tracks):
        """Remove unwanted audio tracks"""
        # Build ffmpeg command
        cmd = ['ffmpeg', '-i', str(input_file), '-map', '0:v']  # Keep all video tracks

        # Add audio tracks to keep
        for i in tracks_to_keep:
            if i < 0 or i >= len(audio_tracks):
                error_msg = f"Error: Invalid track index {i} (valid range: 0-{len(audio_tracks)-1})"
                print(error_msg)
                if hasattr(self, 'log_message'):
                    self.log_message(error_msg)
                return False

            track = audio_tracks[i]
            stream_index = track['stream_index']
            cmd.extend(['-map', f'0:{stream_index}'])

        # Copy all subtitle tracks (if any)
        cmd.extend(['-map', '0:s?', '-c', 'copy', str(output_file)])

        success, stdout, stderr = self.run_ffmpeg_command(cmd)
        return success

    def log_message(self, message):
        """记录消息到状态文本框"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)


def run_gui_mode(file_path=None):
    """运行GUI模式"""
    if not GUI_AVAILABLE:
        print("Error: tkinter not available. Cannot run GUI mode.")
        print("Install tkinter: pip install tk (or your system package manager)")
        sys.exit(1)

    root = tk.Tk()
    app = AudioTrackRemoverGUI(root)
    
    # 如果提供了文件路径，自动加载并分析
    if file_path:
        file_path_obj = Path(file_path)
        if file_path_obj.exists():
            app.input_file = file_path_obj
            app.file_path_var.set(str(file_path_obj))
            app.log_message(f"Selected file: {file_path_obj}")
            app.clear_tracks()
            # 延迟一点再分析，确保GUI完全初始化
            root.after(100, app.analyze_file)
        else:
            app.log_message(f"File not found: {file_path}")
    
    root.mainloop()


def run_cli_mode(file_path):
    """运行命令行模式"""
    print("Audio Track Remover Tool v1.0")
    print("=" * 40)

    # 检查依赖
    if not check_dependencies():
        sys.exit(1)

    # 处理文件
    process_video_file(file_path)


def show_help():
    """显示帮助信息"""
    print("Audio Track Remover Tool v1.0")
    print("=" * 40)
    print()
    print("This tool removes unwanted audio tracks from video files.")
    print()
    print("Usage:")
    print("  python audio_track_remover.py                # Start GUI mode (default)")
    print("  python audio_track_remover.py <video_file>   # Open file in GUI mode")
    print("  python audio_track_remover.py --cli <file>    # Process file in CLI mode")
    print("  python audio_track_remover.py --help          # Show this help")
    print()
    print("Supported formats: MKV, MP4, AVI, MOV, FLV, WMV, etc.")
    print()
    print("Requirements:")
    print("  - FFmpeg (download from https://ffmpeg.org/download.html)")
    print("  - tkinter (for GUI mode, usually pre-installed with Python)")
    print()


def main():
    """主函数"""
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg in ['--help', '-h', '/?']:
            show_help()
            return
        
        if arg == '--cli' and len(sys.argv) > 2:
            # 命令行模式（需要--cli参数）
            file_path = Path(sys.argv[2])
            run_cli_mode(file_path)
            return
        
        # 如果参数是文件路径，在GUI中打开
        file_path = Path(arg)
        if file_path.exists():
            run_gui_mode(str(file_path))
            return
    
    # 默认启动GUI模式
    run_gui_mode()


if __name__ == "__main__":
    main()