#!/usr/bin/env python3
import subprocess, threading, os, re, queue
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

ROOT_PAD = 12
log_lines = []

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def build_command(url, mode, quality, out_format, audio_format, audio_quality, folder):
    venv_python = os.path.join("myenv", "bin", "python")
    if not os.path.exists(venv_python):
        venv_python = "python3"
    out_t = os.path.join(folder, "%(title).60s [%(id)s].%(ext)s")
    if mode == "audio":
        return [
            venv_python, "-m", "yt_dlp",
            "-f", "bestaudio",
            "--extract-audio",
            "--audio-format", audio_format,
            "--audio-quality", audio_quality,
            "-o", out_t,
            url
        ]
    else:
        return [
            venv_python, "-m", "yt_dlp",
            "-f", f"bestvideo[height<={quality}]+bestaudio/best",
            "--merge-output-format", out_format,
            "-o", out_t,
            url
        ]

def run_command_thread(cmd, q):
    try:
        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        percent_re = re.compile(r"(\d{1,3}(?:\.\d+)?)%")

        for line in p.stdout:
            line = line.rstrip()
            m = percent_re.search(line)
            pct = float(m.group(1)) if m else None
            q.put(("line", line, pct))

        p.wait()
        q.put(("done", p.returncode))

    except Exception as e:
        q.put(("error", str(e)))

root = tk.Tk()
root.title("YT Downloader")
root.geometry("760x420")
# safe font set: use tuple form and fallback if not available
try:
    root.option_add("*Font", ("Segoe UI", 10))
except Exception:
    try:
        root.option_add("*Font", ("Helvetica", 10))
    except Exception:
        pass

style = ttk.Style(root)
try:
    style.theme_use("clam")
except Exception:
    pass

# Try configure styles; fall back harmlessly if it fails
use_header_style = False
try:
    style.configure("TFrame", background="#f6f7f9")
    style.configure("TLabel", background="#f6f7f9")
    style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))
    use_header_style = True
except Exception:
    use_header_style = False

main = ttk.Frame(root, padding=ROOT_PAD)
main.pack(fill="both", expand=True)

# Header (safe)
if use_header_style:
    ttk.Label(main, text="YouTube Downloader", style="Header.TLabel").grid(row=0, column=0, sticky="w")
else:
    ttk.Label(main, text="YouTube Downloader", font=("Helvetica", 14, "bold")).grid(row=0, column=0, sticky="w")

ttk.Label(main, text="URL:").grid(row=1, column=0, sticky="w", pady=(10,0))
url_entry = ttk.Entry(main, width=70)
url_entry.grid(row=2, column=0, columnspan=3, sticky="we", pady=6)

mode_var = tk.StringVar(value="")
def on_mode_change():
    m = mode_var.get()
    if m == "video":
        video_frame.grid()
        audio_frame.grid_remove()
    elif m == "audio":
        audio_frame.grid()
        video_frame.grid_remove()
    else:
        video_frame.grid_remove()
        audio_frame.grid_remove()

mframe = ttk.Frame(main)
mframe.grid(row=3, column=0, sticky="w", pady=8)
ttk.Radiobutton(mframe, text="Video", variable=mode_var, value="video", command=on_mode_change).pack(side="left", padx=6)
ttk.Radiobutton(mframe, text="Audio only", variable=mode_var, value="audio", command=on_mode_change).pack(side="left", padx=6)

folder_var = tk.StringVar(value=os.path.expanduser("~/Downloads"))
def choose_folder():
    d = filedialog.askdirectory(initialdir=folder_var.get())
    if d: folder_var.set(d)
ttk.Label(main, text="Download folder:").grid(row=4, column=0, sticky="w")
fentry = ttk.Entry(main, textvariable=folder_var, width=55)
fentry.grid(row=5, column=0, sticky="w", pady=6)
ttk.Button(main, text="Browse", command=choose_folder).grid(row=5, column=1, sticky="w", padx=6)

video_frame = ttk.Frame(main, padding=(6,6,6,6), relief="ridge")
video_frame.grid(row=6, column=0, columnspan=3, sticky="we", pady=8)
video_frame.grid_remove()
ttk.Label(video_frame, text="Video Quality:").grid(row=0, column=0, sticky="w")
quality_var = tk.StringVar(value="720")
ttk.OptionMenu(video_frame, quality_var, quality_var.get(), "360","480","720","1080").grid(row=0, column=1, sticky="w", padx=6)
ttk.Label(video_frame, text="Format:").grid(row=0, column=2, sticky="w", padx=(12,0))
format_var = tk.StringVar(value="mkv")
ttk.OptionMenu(video_frame, format_var, format_var.get(), "mkv","mp4","webm").grid(row=0, column=3, sticky="w", padx=6)

audio_frame = ttk.Frame(main, padding=(6,6,6,6), relief="ridge")
audio_frame.grid(row=7, column=0, columnspan=3, sticky="we")
audio_frame.grid_remove()
ttk.Label(audio_frame, text="Audio Format:").grid(row=0, column=0, sticky="w")
audio_format_var = tk.StringVar(value="mp3")
ttk.OptionMenu(audio_frame, audio_format_var, audio_format_var.get(), "mp3","m4a","opus","wav").grid(row=0, column=1, sticky="w", padx=6)
ttk.Label(audio_frame, text="Audio Quality (0=best):").grid(row=0, column=2, sticky="w", padx=(12,0))
audio_quality_var = tk.StringVar(value="0")
ttk.Entry(audio_frame, textvariable=audio_quality_var, width=5).grid(row=0, column=3, sticky="w", padx=6)

progress_text = tk.StringVar(value="")
progress_label = ttk.Label(main, textvariable=progress_text, wraplength=720, anchor="w", justify="left")
progress_label.grid(row=8, column=0, columnspan=3, sticky="we", pady=(8,2))

progress_bar = ttk.Progressbar(main, orient="horizontal", length=700, mode="determinate")
progress_bar.grid(row=9, column=0, columnspan=3, sticky="we", pady=(2,8))

def start_download():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Input error", "Please enter a URL.")
        return
    mode = mode_var.get()
    if not mode:
        messagebox.showerror("Select mode", "Choose Video or Audio.")
        return
    folder = folder_var.get().strip()
    if not folder:
        messagebox.showerror("Folder", "Select a download folder.")
        return
    ensure_dir(folder)
    cmd = build_command(url, mode, quality_var.get(), format_var.get(), audio_format_var.get(), audio_quality_var.get(), folder)
    progress_text.set("Starting download...")
    progress_bar["value"] = 0
    global q
    q = queue.Queue()
    t = threading.Thread(target=run_command_thread, args=(cmd, q), daemon=True)
    t.start()
    root.after(150, poll_queue)

ttk.Button(main, text="Download", command=start_download).grid(row=10, column=0, sticky="w", pady=6)
main.columnconfigure(0, weight=1)

def poll_queue():
    try:
        while True:
            item = q.get_nowait()

            if item[0] == "line":
                _, line, pct = item

                log_lines.append(line)

                # show last line in GUI
                progress_text.set(line)

                if pct is not None:
                    progress_bar["value"] = max(0, min(100, pct))

            elif item[0] == "done":
                code = item[1]

                if code == 0:
                    progress_bar["value"] = 100
                    messagebox.showinfo("Done", "Download completed.")
                else:
                    error_line = None

                    for line in reversed(log_lines):
                        if "ERROR:" in line:
                            error_line = line
                            break

                    if not error_line:
                        error_line = log_lines[-1] if log_lines else "Unknown error"

                    messagebox.showerror("Download Error", error_line)

            elif item[0] == "error":
                messagebox.showerror("Error", item[1])

    except queue.Empty:
        root.after(150, poll_queue)

on_mode_change()
root.mainloop()
