import os
import sys
import threading
import subprocess
import queue
import shutil
import re
import customtkinter as ctk
from tkinter import filedialog, messagebox

# --- Helper Functions ---
def get_base_path():
    return sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.abspath(".")

def get_executable(exec_name):
    base = get_base_path()
    bundled = os.path.join(base, "binaries", exec_name)
    if os.path.exists(bundled):
        return bundled
    return shutil.which(exec_name)

# --- Main Application ---
class VidarDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Vidar Downloader")
        self.geometry("650x650")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Queues for thread-safe UI updates
        self.download_queue = queue.Queue()
        self.log_queue = queue.Queue()
        self.progress_queue = queue.Queue()
        self.running = True

        # List to store loaded URLs from file as tuples: (url, password)
        self.loaded_urls = []

        # Quality mapping for yt-dlp formats
        self.quality_mapping = {
            "best": "bestvideo+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best",
            "720p": "bestvideo[height<=720]+bestaudio/best",
            "480p": "bestvideo[height<=480]+bestaudio/best",
            "360p": "bestvideo[height<=360]+bestaudio/best",
            "240p": "bestvideo[height<=240]+bestaudio/best",
            "144p": "bestvideo[height<=144]+bestaudio/best"
        }
        self.output_dir = os.path.join(os.getcwd(), "Video Downloads")
        self.no_check_certificate = False

        # Aria2c options
        self.use_aria2 = False
        self.aria2_args = ""

        # Cookie file path
        self.cookies_file = None

        # yt-dlp path and delayed initialization
        self.yt_dlp_path = None

        # Turbo mode flag: adds extra arguments for faster downloads
        self.turbo_mode = False

        self.create_widgets()
        threading.Thread(target=self.initialize_yt_dlp, daemon=True).start()
        self.start_queue_thread()
        self.after(100, self.process_queues)

    def initialize_yt_dlp(self):
        exec_name = "yt-dlp.exe" if sys.platform == "win32" else "yt-dlp"
        self.yt_dlp_path = get_executable(exec_name)
        if not self.yt_dlp_path:
            self.show_error("yt-dlp executable not found!")
            return
        try:
            result = subprocess.run([self.yt_dlp_path, "--version"],
                                      capture_output=True, text=True, check=True)
            self.append_log(f"Using yt-dlp version: {result.stdout.strip()}\n")
        except subprocess.CalledProcessError as e:
            self.show_error(f"Error getting yt-dlp version: {e.stderr}")

    def create_widgets(self):
        # Main container frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=8)
        self.main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Two-tab layout: Download and Settings
        self.tabview = ctk.CTkTabview(self.main_frame, width=600, height=500)
        self.tabview.pack(pady=5)
        self.tabview.add("Download")
        self.tabview.add("Settings")

        # ---- Download Tab ----
        download_tab = self.tabview.tab("Download")
        ctk.CTkLabel(download_tab, text="Video URL:").pack(pady=(10, 0), padx=10, anchor="w")
        self.url_entry = ctk.CTkEntry(download_tab, placeholder_text="Enter video URL", width=580)
        self.url_entry.pack(pady=(0, 10), padx=10)
        ctk.CTkLabel(download_tab, text="Video Password (if required):").pack(pady=(5, 0), padx=10, anchor="w")
        self.password_entry = ctk.CTkEntry(download_tab, placeholder_text="Enter password", width=580, show="*")
        self.password_entry.pack(pady=(0, 10), padx=10)
        self.load_file_btn = ctk.CTkButton(download_tab, text="Load URLs from File", command=self.load_urls_from_file)
        self.load_file_btn.pack(pady=5, padx=10)
        self.loaded_label = ctk.CTkLabel(download_tab, text="No URLs loaded from file.", fg_color="transparent")
        self.loaded_label.pack(pady=(5, 10), padx=10)

        # Options frame (Quality & Format)
        options_frame = ctk.CTkFrame(download_tab, corner_radius=6)
        options_frame.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(options_frame, text="Quality:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.quality_var = ctk.StringVar(value="best")
        self.quality_option = ctk.CTkComboBox(options_frame, variable=self.quality_var,
                                               values=list(self.quality_mapping.keys()), width=100)
        self.quality_option.grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkLabel(options_frame, text="Format:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.format_var = ctk.StringVar(value="mp4")
        self.format_option = ctk.CTkComboBox(options_frame, variable=self.format_var,
                                            values=["mp4", "mkv", "mov", "avi"], width=100)
        self.format_option.grid(row=0, column=3, padx=5, pady=5)

        # Download button
        self.download_btn = ctk.CTkButton(download_tab, text="Download", command=self.download_videos)
        self.download_btn.pack(pady=10, padx=10)

        # Progress bar and percentage label
        self.progress_bar = ctk.CTkProgressBar(download_tab, width=580)
        self.progress_bar.pack(pady=5, padx=10)
        self.progress_label = ctk.CTkLabel(download_tab, text="Progress: 0%")
        self.progress_label.pack(pady=(0, 10), padx=10)

        # Log textbox
        self.log_text = ctk.CTkTextbox(download_tab, state="disabled", width=580, height=120)
        self.log_text.pack(pady=5, padx=10)

        # ---- Settings Tab ----
        settings_tab = self.tabview.tab("Settings")
        self.aria2_check = ctk.CTkCheckBox(settings_tab, text="Use aria2c for downloads", command=self.toggle_aria2)
        self.aria2_check.pack(pady=(10, 5), padx=10, anchor="w")
        ctk.CTkLabel(settings_tab, text="aria2c Arguments:").pack(pady=(5, 0), padx=10, anchor="w")
        self.aria2_args_entry = ctk.CTkEntry(settings_tab, placeholder_text="e.g. --max-connection-per-server=4", width=580)
        self.aria2_args_entry.pack(pady=(0, 10), padx=10)
        self.ssl_check = ctk.CTkCheckBox(settings_tab, text="Disable SSL certificate verification", command=self.toggle_ssl)
        self.ssl_check.pack(pady=5, padx=10, anchor="w")
        self.cookie_btn = ctk.CTkButton(settings_tab, text="Select Cookies File", command=self.select_cookie_file)
        self.cookie_btn.pack(pady=10, padx=10, anchor="w")
        
        # Turbo Mode checkbox
        self.turbo_mode_check = ctk.CTkCheckBox(settings_tab, text="Enable Turbo Mode", command=self.toggle_turbo)
        self.turbo_mode_check.pack(pady=5, padx=10, anchor="w")
        
        out_dir_frame = ctk.CTkFrame(settings_tab, corner_radius=6)
        out_dir_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(out_dir_frame, text="Output Directory:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.output_dir_var = ctk.StringVar(value=self.output_dir)
        self.output_dir_entry = ctk.CTkEntry(out_dir_frame, textvariable=self.output_dir_var, width=400)
        self.output_dir_entry.grid(row=0, column=1, padx=5, pady=5)
        self.browse_btn = ctk.CTkButton(out_dir_frame, text="Browse", command=self.browse_output_directory, width=80)
        self.browse_btn.grid(row=0, column=2, padx=5, pady=5)

    def toggle_turbo(self):
        self.turbo_mode = not self.turbo_mode
        mode = "enabled" if self.turbo_mode else "disabled"
        self.append_log(f"Turbo Mode {mode}.\n")

    def select_cookie_file(self):
        file_path = filedialog.askopenfilename(title="Select Cookies File")
        if file_path:
            self.cookies_file = file_path
            self.append_log(f"Cookie file selected: {file_path}\n")

    def load_urls_from_file(self):
        file_path = filedialog.askopenfilename(title="Select URL Text File", filetypes=[("Text Files", "*.txt")])
        if file_path:
            try:
                self.loaded_urls.clear()
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        # Allow for multiple delimiters: | , ; or whitespace
                        parts = re.split(r'\s*[|,;]\s*', line)
                        url = parts[0].strip()
                        password = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
                        # Validate basic URL format
                        if url.lower().startswith("http"):
                            self.loaded_urls.append((url, password))
                        else:
                            self.append_log(f"Skipped invalid URL entry: {line}\n")
                count = len(self.loaded_urls)
                self.loaded_label.configure(text=f"Loaded {count} URL{'s' if count != 1 else ''} from file.")
                self.append_log(f"Loaded {count} URL{'s' if count != 1 else ''} from file.\n")
            except Exception as e:
                self.show_error(f"Failed to load URLs: {str(e)}")

    def toggle_aria2(self):
        self.use_aria2 = not self.use_aria2
        if self.use_aria2 and not get_executable("aria2c.exe" if sys.platform == "win32" else "aria2c"):
            self.show_error("aria2c executable not found!")
            self.use_aria2 = False

    def toggle_ssl(self):
        self.no_check_certificate = not self.no_check_certificate

    def browse_output_directory(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir = dir_path
            self.output_dir_var.set(dir_path)
            os.makedirs(dir_path, exist_ok=True)

    def append_log(self, message):
        self.log_queue.put(message)

    def show_error(self, message):
        self.log_queue.put(f"ERROR: {message}\n")
        self.after(0, lambda: messagebox.showerror("Error", message))

    def process_queues(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_text.configure(state="normal")
                self.log_text.insert("end", msg)
                self.log_text.see("end")
                self.log_text.configure(state="disabled")
        except queue.Empty:
            pass

        try:
            while True:
                prog = self.progress_queue.get_nowait()
                self.progress_bar.set(prog)
                self.progress_label.configure(text=f"Progress: {int(prog * 100)}%")
        except queue.Empty:
            pass

        self.after(100, self.process_queues)

    def download_videos(self):
        # If URLs have been loaded from a file, process them; otherwise, use manual entry.
        if self.loaded_urls:
            for url, password in self.loaded_urls:
                self.enqueue_download(url, password)
            self.loaded_urls.clear()
            self.loaded_label.configure(text="No URLs loaded from file.")
        else:
            url = self.url_entry.get().strip()
            password = self.password_entry.get().strip() or None
            if not url:
                self.show_error("URL is required!")
                return
            self.enqueue_download(url, password)

    def enqueue_download(self, url, password=None):
        self.download_queue.put((url, password))
        self.append_log(f"Enqueued: {url}\n")

    def start_queue_thread(self):
        threading.Thread(target=self.process_queue, daemon=True).start()

    def process_queue(self):
        while self.running:
            try:
                url, password = self.download_queue.get(timeout=1)
                self.process_download(url, password)
                self.download_queue.task_done()
            except queue.Empty:
                continue

    def process_download(self, url, password):
        if not self.yt_dlp_path:
            self.show_error("yt-dlp executable not configured!")
            return

        quality_format = self.quality_mapping.get(self.quality_var.get(), "bestvideo+bestaudio/best")
        output_format = self.format_var.get()

        command = [
            self.yt_dlp_path,
            "--newline",
        ]
        if self.no_check_certificate:
            command.append("--no-check-certificate")
        if self.cookies_file:
            command += ["--cookies", self.cookies_file]
        if password:
            command += ["--video-password", password]
        if self.use_aria2:
            command += ["--external-downloader", "aria2c"]
            self.aria2_args = self.aria2_args_entry.get().strip()
            if self.aria2_args:
                command += self.aria2_args.split()

        # Append Turbo Mode arguments if enabled
        if self.turbo_mode:
            command += ["--concurrent-fragments", "10", "--buffer-size", "16K"]

        command += [
            "-f", quality_format,
            "--merge-output-format", output_format,
            "--output", os.path.join(self.output_dir, "%(title)s.%(ext)s"),
            url
        ]
        self.append_log(f"Executing: {' '.join(command)}\n")

        try:
            proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in proc.stdout:
                self.append_log(line)
                match = re.search(r'(\d+(?:\.\d+)?)%', line)
                if match:
                    try:
                        prog = float(match.group(1)) / 100.0
                        self.progress_queue.put(prog)
                    except ValueError:
                        pass
            proc.wait()
            if proc.returncode == 0:
                self.append_log(f"✅ Download succeeded: {url}\n")
            else:
                self.append_log(f"❌ Download failed: {url} (Code: {proc.returncode})\n")
        except Exception as e:
            self.show_error(f"Download error: {str(e)}")

    def on_close(self):
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.running = False
            self.destroy()

if __name__ == "__main__":
    app = VidarDownloader()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
