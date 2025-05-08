# Import the Tkinter GUI toolkit
import tkinter as tk

# Import the file dialog module from tkinter to allow file selection
from tkinter import filedialog

# Import a custom module (likely named `request.py`) where audio transcription and summarization functions live
# NOTE: This should probably be named `requests` if it's referring to the HTTP library, but here it's custom.
import request as rq

def upload_action():
    """
    Callback function that is triggered when the user clicks the "Upload WAV File" button.
    - Opens a file dialog to select a WAV file.
    - Calls the transcription function.
    - Generates a summary.
    - Displays both in the GUI.
    """
    # Open a file picker dialog to select a .wav file
    file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    
    # If the user cancels the file selection dialog, exit the function
    if not file_path:
        return

    # Print the selected file path to the console for debugging
    print("Selected:", file_path)

    # Transcribe the audio file using a Google Cloud Speech-to-Text function defined in the `request` module
    transcript = rq.google_transcribe(file_path)

    # Generate a summary from the full transcript
    _, summary = rq.generate_summary_from_text(transcript)

    # Compose the result string to display in the GUI
    result_text = (
        "=== Summary ===\n\n"
        f"{summary.strip()}\n\n"
        "=== Full Transcription ===\n\n"
        f"{transcript.strip()}"
    )

    # Update the label widget in the GUI with the resulting text
    result_label.config(text=result_text)

# ---------------- GUI SETUP ---------------- #

# Create the main application window
root = tk.Tk()

# Set the title of the window
root.title("Audio Transcriber & Summarizer")

# Set the window dimensions (800x600 pixels)
root.geometry("800x600")

# Set the background color of the window
root.configure(bg="lightblue")

# Add a heading label to the window
tk.Label(
    root,
    text="Upload WAV File for Transcription & Summary",  # Display text
    font=("Courier", 14),                                # Font style and size
    bg="lightblue"                                       # Match window background
).pack(pady=20)                                          # Add vertical padding

# Add a button to upload a WAV file
tk.Button(
    root,
    text="Upload WAV File",         # Button label
    command=upload_action,          # Function to call when clicked
    bg="white",                     # Button background color
    font=("Courier", 12)            # Font styling
).pack()

# Add a label widget to display the transcription and summary results
result_label = tk.Label(
    root, 
    text="",                        # Start with empty text
    wraplength=750,                 # Wrap text to fit nicely in the window
    justify="left",                 # Align text to the left
    bg="lightblue",                 # Match window background
    font=("Courier", 10)           # Font styling
)
result_label.pack(pady=20)         # Add vertical padding

# Start the GUI event loop — keeps the window open and responsive
root.mainloop()
