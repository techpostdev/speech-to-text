import os
import sys

# ================= FIX FOR WHISPER ASSETS =================
def fix_whisper_assets():
    """
    Fix missing mel_filters.npz error in PyInstaller / frozen build
    """
    try:
        import whisper
        whisper_dir = os.path.dirname(whisper.__file__)
        assets_path = os.path.join(whisper_dir, "assets")

        # Force Whisper to use correct asset path
        os.environ["WHISPER_ASSETS"] = assets_path

        # Extra safety: ensure folder exists
        if not os.path.exists(assets_path):
            print("⚠ Whisper assets folder missing:", assets_path)

    except Exception as e:
        print("⚠ Whisper asset fix error:", e)

fix_whisper_assets()

# ================= YOUR ORIGINAL IMPORTS =================
import tkinter as tk
from tkinter import filedialog, ttk
import threading
import whisper
import time
import json

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    TkinterDnD = tk

# ============================================
# THEME COLORS
# ============================================
BG = "#0d0d0d"
CARD = "#161616"
BORDER = "#2a2a2a"
ACCENT = "#ff4d00"
ACCENT2 = "#ff8c00"
TEXT = "#f0f0f0"
MUTED = "#666666"
SUCCESS = "#00e676"
FONT_TITLE = ("Georgia", 22, "bold")
FONT_SUB = ("Georgia", 10, "italic")
FONT_MONO = ("Courier New", 9)
FONT_UI = ("Courier New", 10)
FONT_BTN = ("Courier New", 11, "bold")


class WhisperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WHISPER — Speech to Text")
        self.root.geometry("880x750")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.video_file = None
        self.batch_files = []
        self.model_var = tk.StringVar(value="base")
        self.language_var = tk.StringVar(value="en")
        self.output_dir = None
        self.is_running = False
        self.start_time = 0

        self._build_ui()
        self._setup_shortcuts()
        self._check_device()

    def _build_ui(self):
        # ---- TOP HEADER ----
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=30, pady=(28, 0))

        tk.Label(header, text="WHISPER", font=FONT_TITLE,
                 fg=ACCENT, bg=BG).pack(side="left")
        tk.Label(header, text="  /  speech to text engine",
                 font=FONT_SUB, fg=MUTED, bg=BG).pack(side="left", pady=(8, 0))

        # Divider
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=30, pady=(14, 0))

        # ---- FILE DROP ZONE ----
        drop_frame = tk.Frame(self.root, bg=CARD, bd=0, highlightthickness=1,
                              highlightbackground=BORDER)
        drop_frame.pack(fill="x", padx=30, pady=(20, 0))

        if DND_AVAILABLE:
            drop_frame.drop_target_register(DND_FILES)
            drop_frame.dnd_bind("<<Drop>>", self._drop_file)

        inner = tk.Frame(drop_frame, bg=CARD)
        inner.pack(pady=22, padx=20)

        tk.Label(inner, text="▶  SELECT OR DRAG & DROP VIDEO/AUDIO FILE", font=FONT_BTN,
                 fg=ACCENT, bg=CARD).pack()
        tk.Label(inner, text="mp4 · mov · mkv · avi · mp3 · wav · m4a · flac",
                 font=("Courier New", 8), fg=MUTED, bg=CARD).pack(pady=(4, 12))

        self.file_label = tk.Label(inner, text="No file selected",
                                   font=FONT_MONO, fg=MUTED, bg=CARD,
                                   wraplength=680, justify="center")
        self.file_label.pack()

        btn_row = tk.Frame(drop_frame, bg=CARD)
        btn_row.pack(pady=(0, 18))

        self._make_btn(btn_row, "BROWSE FILE", self._browse_file, ACCENT).pack(side="left", padx=6)
        self._make_btn(btn_row, "SCAN FOLDER", self._scan_folder, "#333333").pack(side="left", padx=6)
        self._make_btn(btn_row, "OUTPUT FOLDER", self._select_output_dir, "#333333").pack(side="left", padx=6)

        # ---- MODEL SELECTOR ----
        model_frame = tk.Frame(self.root, bg=BG)
        model_frame.pack(fill="x", padx=30, pady=(18, 0))

        tk.Label(model_frame, text="MODEL", font=FONT_BTN,
                 fg=MUTED, bg=BG).pack(side="left", padx=(0, 16))

        models = [("tiny", "Fastest"), ("base", "Balanced ✓"), ("small", "Better"), ("medium", "Best Quality")]
        for val, label in models:
            f = tk.Frame(model_frame, bg=BG)
            f.pack(side="left", padx=6)
            rb = tk.Radiobutton(f, text=label, variable=self.model_var, value=val,
                                font=("Courier New", 9), fg=TEXT, bg=BG,
                                selectcolor=BG, activebackground=BG,
                                activeforeground=ACCENT,
                                indicatoron=1,
                                padx=8, pady=4,
                                cursor="hand2")
            rb.pack()

        # ---- LANGUAGE SELECTOR ----
        lang_frame = tk.Frame(self.root, bg=BG)
        lang_frame.pack(fill="x", padx=30, pady=(18, 0))

        tk.Label(lang_frame, text="LANGUAGE", font=FONT_BTN,
                 fg=MUTED, bg=BG).pack(side="left", padx=(0, 16))

        languages = [("English", "en"), ("Spanish", "es"), ("French", "fr"), 
                     ("German", "de"), ("Italian", "it"), ("Japanese", "ja"),
                     ("Chinese", "zh"), ("Russian", "ru")]
        for name, code in languages:
            rb = tk.Radiobutton(lang_frame, text=name, variable=self.language_var, 
                               value=code, font=("Courier New", 9), fg=TEXT, bg=BG,
                               selectcolor=BG, activebackground=BG,
                               indicatoron=1, padx=6, pady=2,
                               cursor="hand2")
            rb.pack(side="left", padx=4)

        # ---- OUTPUT FORMATS ----
        fmt_frame = tk.Frame(self.root, bg=BG)
        fmt_frame.pack(fill="x", padx=30, pady=(16, 0))

        tk.Label(fmt_frame, text="OUTPUT", font=FONT_BTN,
                 fg=MUTED, bg=BG).pack(side="left", padx=(0, 16))

        self.fmt_vars = {}
        formats = [("TXT", True), ("SRT", False), ("VTT", False), ("JSON", False), ("TSV", False)]
        for fmt, default in formats:
            var = tk.BooleanVar(value=default)
            self.fmt_vars[fmt] = var
            cb = tk.Checkbutton(fmt_frame, text=fmt, variable=var,
                                font=("Courier New", 9, "bold"), fg=ACCENT2, bg=BG,
                                selectcolor="#1a1a1a", activebackground=BG,
                                activeforeground=ACCENT, cursor="hand2",
                                highlightthickness=0)
            cb.pack(side="left", padx=8)

        # ---- BATCH PROCESSING ----
        batch_frame = tk.Frame(self.root, bg=BG)
        batch_frame.pack(fill="x", padx=30, pady=(10, 0))
        
        self.batch_var = tk.BooleanVar(value=False)
        batch_cb = tk.Checkbutton(batch_frame, text="BATCH PROCESS ALL FILES IN FOLDER", 
                                  variable=self.batch_var,
                                  font=("Courier New", 9, "bold"), fg=ACCENT2, bg=BG,
                                  selectcolor="#1a1a1a", activebackground=BG,
                                  cursor="hand2")
        batch_cb.pack(side="left")

        # ---- RUN BUTTON ----
        run_row = tk.Frame(self.root, bg=BG)
        run_row.pack(pady=(22, 0))

        self.run_btn = tk.Button(run_row, text="▶  START TRANSCRIPTION",
                                 font=FONT_BTN, fg=BG, bg=ACCENT,
                                 activebackground=ACCENT2, activeforeground=BG,
                                 relief="flat", bd=0, padx=28, pady=12,
                                 cursor="hand2", command=self._start)
        self.run_btn.pack()

        # ---- PROGRESS ----
        prog_frame = tk.Frame(self.root, bg=BG)
        prog_frame.pack(fill="x", padx=30, pady=(18, 0))

        self.status_label = tk.Label(prog_frame, text="Ready.",
                                     font=FONT_MONO, fg=MUTED, bg=BG)
        self.status_label.pack(anchor="w")

        self.progress = ttk.Progressbar(prog_frame, mode="indeterminate", length=820)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TProgressbar", troughcolor=CARD,
                        background=ACCENT, thickness=4)
        self.progress.pack(fill="x", pady=(6, 0))

        # ---- LOG / TRANSCRIPT BOX ----
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=30, pady=(16, 0))

        log_frame = tk.Frame(self.root, bg=BG)
        log_frame.pack(fill="both", expand=True, padx=30, pady=(10, 20))

        tk.Label(log_frame, text="TRANSCRIPT OUTPUT",
                 font=("Courier New", 8), fg=MUTED, bg=BG).pack(anchor="w")

        text_frame = tk.Frame(log_frame, bg=BORDER, bd=1)
        text_frame.pack(fill="both", expand=True, pady=(4, 0))

        self.log_box = tk.Text(text_frame, bg="#111111", fg=TEXT,
                               font=FONT_MONO, relief="flat",
                               wrap="word", padx=12, pady=10,
                               insertbackground=ACCENT,
                               selectbackground=ACCENT,
                               state="disabled", bd=0)
        scrollbar = tk.Scrollbar(text_frame, command=self.log_box.yview,
                                 bg=CARD, troughcolor=BG)
        self.log_box.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.log_box.pack(side="left", fill="both", expand=True)

    def _setup_shortcuts(self):
        self.root.bind('<Control-o>', lambda e: self._browse_file())
        self.root.bind('<Control-Return>', lambda e: self._start())
        self.root.bind('<Control-b>', lambda e: self._scan_folder())

    def _check_device(self):
        try:
            import torch
            if torch.cuda.is_available():
                self._log("✓ CUDA available - using GPU acceleration")
                return "cuda"
            else:
                self._log("⚠ CUDA not available - using CPU (slower)")
                return "cpu"
        except:
            self._log("⚠ PyTorch not found - using CPU")
            return "cpu"

    def _make_btn(self, parent, text, cmd, color):
        return tk.Button(parent, text=text, font=FONT_BTN,
                         fg=TEXT if color != ACCENT else BG,
                         bg=color, activebackground=ACCENT2,
                         activeforeground=BG, relief="flat",
                         bd=0, padx=18, pady=8,
                         cursor="hand2", command=cmd)

    def _drop_file(self, event):
        file_path = event.data.strip()

        if file_path.startswith("{") and file_path.endswith("}"):
            file_path = file_path[1:-1]

        if os.path.isfile(file_path):
            self.video_file = file_path
            self.batch_files = []
            self.batch_var.set(False)

            name = os.path.basename(file_path)
            size_mb = os.path.getsize(file_path) / (1024 * 1024)

            if size_mb > 500:
                self.file_label.config(
                    text=f"⚠  {name}  ({size_mb:.1f} MB) - Large file may take a while",
                    fg=ACCENT
                )
                self._set_status(
                    f"⚠ Large file ({size_mb:.1f} MB) may take a while",
                    ACCENT
                )
            else:
                self.file_label.config(
                    text=f"✔  {name}  ({size_mb:.1f} MB)",
                    fg=SUCCESS
                )

            self._log(f"Drag & Drop loaded: {file_path}")

    def _browse_file(self):
        f = filedialog.askopenfilename(
            title="Select Video/Audio File",
            filetypes=[("Media Files", "*.mp4 *.mp3 *.wav *.m4a *.flac *.mov *.avi *.mkv"),
                       ("All Files", "*.*")]
        )
        if f:
            self.video_file = f
            self.batch_files = []
            self.batch_var.set(False)
            name = os.path.basename(f)
            size_mb = os.path.getsize(f) / (1024 * 1024)
            if size_mb > 500:
                self.file_label.config(text=f"⚠  {name}  ({size_mb:.1f} MB) - Large file may take a while", fg=ACCENT)
                self._set_status(f"⚠ Large file ({size_mb:.1f} MB) may take a while", ACCENT)
            else:
                self.file_label.config(text=f"✔  {name}  ({size_mb:.1f} MB)", fg=SUCCESS)

    def _scan_folder(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if not folder:
            return
        exts = ['.mp4', '.mp3', '.wav', '.m4a', '.flac', '.mov', '.avi', '.mkv']
        self.batch_files = [os.path.join(folder, f) for f in os.listdir(folder)
                           if os.path.splitext(f)[1].lower() in exts]
        if not self.batch_files:
            self.file_label.config(text="❌  No media files found in folder.", fg=ACCENT)
            return
        self.video_file = self.batch_files[0]
        name = os.path.basename(self.video_file)
        size_mb = os.path.getsize(self.video_file) / (1024 * 1024)
        self.file_label.config(
            text=f"✔  {name}  ({size_mb:.1f} MB)  [{len(self.batch_files)} file(s) in folder]",
            fg=SUCCESS)
        self._log(f"Found {len(self.batch_files)} media file(s) in folder")

    def _select_output_dir(self):
        folder = filedialog.askdirectory(title="Select Output Directory")
        if folder:
            self.output_dir = folder
            self._set_status(f"✓ Output folder: {folder}", SUCCESS)
            self._log(f"Output directory set to: {folder}")

    def _log(self, msg, color=TEXT):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.configure(state="disabled")
        self.log_box.see("end")

    def _set_status(self, msg, color=MUTED):
        self.status_label.config(text=msg, fg=color)

    def _update_transcribe_status(self, elapsed):
        if self.is_running:
            self._set_status(f"Transcribing... {elapsed:.0f} seconds elapsed", ACCENT2)
            self.root.after(1000, lambda: self._update_transcribe_status(time.time() - self.start_time))

    def _start(self):
        if self.is_running:
            return
        if not self.video_file or not os.path.exists(self.video_file):
            self._set_status("⚠  Please select a valid file first.", ACCENT)
            return
        
        if self.batch_var.get() and len(self.batch_files) > 1:
            self._start_batch()
        else:
            self.is_running = True
            self.run_btn.config(state="disabled", text="⏳  PROCESSING...", bg="#333333")
            self.progress.start(12)
            thread = threading.Thread(target=self._run_whisper, args=(self.video_file,), daemon=True)
            thread.start()

    def _start_batch(self):
        if not self.batch_files:
            self._set_status("⚠ No batch files found. Please scan a folder first.", ACCENT)
            return
        
        self.is_running = True
        self.run_btn.config(state="disabled", text="⏳  BATCH PROCESSING...", bg="#333333")
        self.progress.start(12)
        thread = threading.Thread(target=self._run_batch, daemon=True)
        thread.start()

    def _run_batch(self):
        total = len(self.batch_files)
        self._log(f"\n{'=' * 52}")
        self._log(f"BATCH PROCESSING - {total} file(s)")
        self._log(f"{'=' * 52}\n")
        
        for idx, file_path in enumerate(self.batch_files, 1):
            if not self.is_running:
                break
            self._log(f"\n[{idx}/{total}] Processing: {os.path.basename(file_path)}")
            self._set_status(f"Batch {idx}/{total}: {os.path.basename(file_path)}", ACCENT2)
            self._run_whisper(file_path, batch_mode=True)
        
        self._log(f"\n{'=' * 52}")
        self._log(f"✓ BATCH COMPLETE - Processed {total} file(s)")
        self._log(f"{'=' * 52}")
        self._set_status(f"✓ Batch complete - Processed {total} file(s)", SUCCESS)
        self.progress.stop()
        self.run_btn.config(state="normal", text="▶  START TRANSCRIPTION", bg=ACCENT)
        self.is_running = False

    def _run_whisper(self, file_path, batch_mode=False):
        try:
            model_size = self.model_var.get()
            if not batch_mode:
                self._set_status(f"Loading Whisper model: {model_size}...", ACCENT2)
            
            self._log(f"{'=' * 52}")
            self._log(f"  FILE   : {os.path.basename(file_path)}")
            self._log(f"  MODEL  : {model_size}")
            self._log(f"  LANGUAGE: {self.language_var.get()}")
            self._log(f"  DATE   : {time.ctime()}")
            self._log(f"{'=' * 52}\n")

            # Use user home dir for model cache (safe for PyInstaller)
            cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "whisper")
            os.makedirs(cache_dir, exist_ok=True)

            model = whisper.load_model(model_size, download_root=cache_dir)
            
            if not batch_mode:
                self._set_status("Transcribing... please wait ⏳", ACCENT2)
            
            self.start_time = time.time()
            self.root.after(1000, lambda: self._update_transcribe_status(0))
            
            result = model.transcribe(file_path, language=self.language_var.get(),
                                      task="transcribe", word_timestamps=True)
            elapsed = round(time.time() - self.start_time, 2)

            transcript = result["text"]
            segments = result["segments"]
            
            # Determine output directory
            if self.output_dir:
                out_dir = self.output_dir
            else:
                out_dir = os.path.dirname(file_path)
            
            base_name = os.path.splitext(os.path.basename(file_path))[0]

            saved = []

            # TXT
            if self.fmt_vars["TXT"].get():
                path = os.path.join(out_dir, f"{base_name}.txt")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(f"FILE: {os.path.basename(file_path)}\n")
                    f.write(f"DATE: {time.ctime()}\n")
                    f.write(f"MODEL: Whisper {model_size}\n")
                    f.write(f"LANGUAGE: {self.language_var.get()}\n")
                    f.write(f"TIME: {elapsed} seconds\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(transcript)
                saved.append("TXT")

            # SRT
            if self.fmt_vars["SRT"].get():
                path = os.path.join(out_dir, f"{base_name}.srt")
                with open(path, "w", encoding="utf-8") as f:
                    for i, seg in enumerate(segments, 1):
                        f.write(f"{i}\n{self._fmt_srt(seg['start'])} --> {self._fmt_srt(seg['end'])}\n{seg['text'].strip()}\n\n")
                saved.append("SRT")

            # VTT
            if self.fmt_vars["VTT"].get():
                path = os.path.join(out_dir, f"{base_name}.vtt")
                with open(path, "w", encoding="utf-8") as f:
                    f.write("WEBVTT\n\n")
                    for i, seg in enumerate(segments, 1):
                        f.write(f"{i}\n{self._fmt_vtt(seg['start'])} --> {self._fmt_vtt(seg['end'])}\n{seg['text'].strip()}\n\n")
                saved.append("VTT")

            # JSON
            if self.fmt_vars["JSON"].get():
                path = os.path.join(out_dir, f"{base_name}.json")
                data = {"file": os.path.basename(file_path), "date": time.ctime(),
                        "model": model_size, "language": self.language_var.get(),
                        "time_taken": elapsed,
                        "full_text": transcript,
                        "segments": [{"id": s["id"], "start": s["start"],
                                      "end": s["end"], "text": s["text"].strip()}
                                     for s in segments]}
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                saved.append("JSON")

            # TSV
            if self.fmt_vars["TSV"].get():
                path = os.path.join(out_dir, f"{base_name}.tsv")
                with open(path, "w", encoding="utf-8") as f:
                    f.write("ID\tStart\tEnd\tText\n")
                    for s in segments:
                        f.write(f"{s['id']}\t{s['start']:.3f}\t{s['end']:.3f}\t{s['text'].strip()}\n")
                saved.append("TSV")

            self._log(transcript)
            self._log(f"\n{'=' * 52}")
            self._log(f"  ✔  Done in {elapsed}s — Saved: {' · '.join(saved)}")
            self._log(f"  📁 Folder: {out_dir}")
            self._log(f"{'=' * 52}")
            
            if not batch_mode:
                self._set_status(f"✔  Completed in {elapsed}s — {' · '.join(saved)} saved.", SUCCESS)

        except Exception as e:
            self._log(f"\n❌ ERROR: {str(e)}")
            if not batch_mode:
                self._set_status(f"❌ Error: {str(e)}", ACCENT)

        finally:
            if not batch_mode:
                self.progress.stop()
                self.run_btn.config(state="normal", text="▶  START TRANSCRIPTION", bg=ACCENT)
                self.is_running = False

    def _fmt_srt(self, s):
        h, m = int(s // 3600), int((s % 3600) // 60)
        sec, ms = int(s % 60), int((s - int(s)) * 1000)
        return f"{h:02}:{m:02}:{sec:02},{ms:03}"

    def _fmt_vtt(self, s):
        h, m = int(s // 3600), int((s % 3600) // 60)
        sec, ms = int(s % 60), int((s - int(s)) * 1000)
        return f"{h:02}:{m:02}:{sec:02}.{ms:03}"


if __name__ == "__main__":
    # Use TkinterDnD.Tk if available, otherwise fall back to tk.Tk
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    app = WhisperGUI(root)
    root.mainloop()