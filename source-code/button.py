import tkinter as tk
from tkinter import filedialog
import request as rq

def upload_action():
    """Triggered when the user uploads a file via GUI."""
    file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if not file_path:
        return

    print("Selected:", file_path)

    # Transcribe audio and generate output
    transcript = rq.google_transcribe(file_path)
    _, summary = rq.generate_summary_from_text(transcript)

    # Display results in GUI
    result_text = (
        "=== Summary ===\n\n"
        f"{summary.strip()}\n\n"
        "=== Full Transcription ===\n\n"
        f"{transcript.strip()}"
    )

    result_label.config(text=result_text)

# GUI setup
root = tk.Tk()
root.title("Audio Transcriber & Summarizer")
root.geometry("800x600")
root.configure(bg="lightblue")

tk.Label(
    root,
    text="Upload WAV File for Transcription & Summary",
    font=("Courier", 14),
    bg="lightblue"
).pack(pady=20)

tk.Button(
    root,
    text="Upload WAV File",
    command=upload_action,
    bg="white",
    font=("Courier", 12)
).pack()

result_label = tk.Label(
    root, 
    text="", 
    wraplength=750, 
    justify="left", 
    bg="lightblue", 
    font=("Courier", 10)
)
result_label.pack(pady=20)

root.mainloop()
