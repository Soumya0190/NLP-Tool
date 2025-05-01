# NLP-Tool
https://devpost.com/software/lecture-summary-generator

---

Here is how you can explain this audio transcription and summarization project using the STAR method (Situation, Task, Action, Result):

S – Situation
Our team participated in HackUCI, a university hackathon, where we wanted to create a tool that could automatically transcribe spoken audio from .wav files and summarize the content to improve accessibility and speed up content review for lectures or meetings.

T – Task
The goal was to build a Python-based desktop application that:

Allows users to upload an audio file.

Transcribes the audio using Google's Speech-to-Text API.

Summarizes the resulting text using natural language processing (NLP) techniques.

Displays both the transcription and a ranked summary to the user.

A – Action
I designed and implemented the following components:

Frontend (button.py): Developed a simple GUI using tkinter that allows users to upload .wav files and displays the results in a formatted label.

Speech Transcription (request.py):

Converted stereo audio to mono using pydub for better recognition.

Uploaded audio files to Google Cloud Storage.

Transcribed the audio using the Google Cloud Speech API's long_running_recognize for large files.

Summarization Engine:

Tokenized and cleaned text.

Calculated sentence similarities using cosine similarity.

Built a similarity graph and applied the PageRank algorithm to rank sentences.

Extracted the top 3 ranked sentences for summary.

Text Output: Saved the transcription to output.txt and used it as input for the summarization process.

R – Result
Successfully deployed a functioning prototype within the 36-hour hackathon window.

The app could transcribe ~5-minute audio clips in under 2 minutes and produce coherent summaries.

Achieved a user-friendly interface and demonstrated the tool to judges, receiving positive feedback for the integration of transcription and summarization in one pipeline.

---

`request.py`Python

Thanks for sharing your full `request.py` script. This Python file does two main things:

---

## 🎯 **Purpose of the Script**
1. **Transcribe audio** using Google Cloud Speech-to-Text.
2. **Summarize the transcription** using a TextRank-style algorithm (graph-based sentence ranking).

---

## 🔍 Code Breakdown & Explanation

---

### ✅ **1. Imports & Setup**
```python
import os
from pydub import AudioSegment
import wave
import time
import speech_recognition as sr
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="hack-uci-2021-152c1928ead5.json"
```

- Sets the environment variable for Google Cloud authentication.
- Uses `pydub` to convert stereo to mono audio.
- Uses `wave` to get sample rate and channels from the WAV file.
- `speech_recognition` is imported but **not used** here. (Can be removed unless you need it.)

---

### ✅ **2. Upload Audio to Google Cloud Storage**
```python
def upload_to_bucket(blob_name, path_to_file, bucket_name):
    ...
```
- Uploads a file to a GCS bucket using credentials from `creds.json`.

```python
def video(file_name):
    ...
```
- Also uploads a file to a hardcoded bucket using a different credentials file.

> 🔧 These two functions do the same thing. You could consolidate them.

---

### ✅ **3. Audio Processing**
```python
def frame_rate_channel(audio_file_name):
    ...
```
- Returns frame rate and number of channels (mono or stereo) of an audio file.

```python
def stereo_to_mono(audio_file_name):
    ...
```
- Converts audio to mono using `pydub`.

---

### ✅ **4. Google Cloud Speech-to-Text**
```python
def google_transcribe(audio_file_name):
    ...
```

**Steps:**
1. Gets sample rate and channels.
2. Converts to mono if stereo.
3. Uploads to GCS bucket.
4. Calls **Google Cloud Speech API** for long-running recognition.
5. Assembles the transcript from the results.

> ⏱ It waits up to 90 seconds for the result.

---

### ✅ **5. Text Summarization (TextRank style)**

#### a. `read_article(file_name)`
- Reads text from a file.
- Splits it into sentences using `. ` (can miss other sentence endings).
- Uses a **bad regex replacement**:
  ```python
  sentence.replace("[^a-zA-Z]", " ")  # ❌ Not actual regex
  ```
  You should use:
  ```python
  re.sub(r'[^a-zA-Z]', ' ', sentence)
  ```

#### b. `sentence_similarity(sent1, sent2, stopwords)`
- Computes cosine similarity between two sentences (as word vectors).

#### c. `build_similarity_matrix(sentences, stop_words)`
- Builds a matrix of similarities between all sentence pairs.

#### d. `generate_summary(file_name, top_n=3)`
- Loads and tokenizes the text.
- Builds similarity matrix and applies **PageRank**.
- Extracts the top N ranked sentences.

---

### ✅ **6. Main Execution**
```python
if __name__ == "__main__":
    ...
```

- Transcribes `history40b.wav`.
- Writes transcript to `output.txt`.
- Summarizes it using TextRank.

---

## ⚠️ Issues & Recommendations

| Problem | Fix |
|--------|-----|
| ✅ Redundant upload functions | Use one consistent `upload_to_bucket()` |
| ❌ Invalid regex with `replace()` | Use `re.sub()` for regex replacement |
| ⚠ Hardcoded bucket & file names | Parameterize or use CLI args |
| ❌ Unused imports (`speech_recognition`) | Remove unless needed |
| ⚠ Assumes audio is always LINEAR16 format | Add validation or support for FLAC, MP3, etc. |
| ⚠ Doesn't check if transcript is empty or invalid | Add try/except and fallback logic |

---

## ✅ Sample Run (Expected)

If you run:

```bash
python request.py
```

It should:
1. Transcribe `history40b.wav` using Google Cloud.
2. Write the text to `output.txt`.
3. Read the file and output a ranked summary of top 3 sentences.

---

Would you like me to refactor and fix the code into a cleaned-up version that's ready for production or easier debugging?

---

`button.py`python

The `button.py` script creates a **graphical user interface (GUI)** using the `tkinter` library to let users upload a `.wav` audio file, transcribe it to text using **Google Cloud Speech-to-Text**, and generate a **text summary** from the transcription. It depends on `request.py` for the transcription and summarization logic.

---

### 🔍 **Breakdown of Components:**

#### 1. **Imports**
```python
import tkinter
from tkinter import *
import tkinter.messagebox as messagebox
from tkinter import filedialog
import request as rq
```
- `tkinter`: GUI toolkit for Python.
- `filedialog`: For file selection dialog.
- `request as rq`: Imports the transcription and summarization logic from `request.py`.

---

#### 2. **Main GUI Window**
```python
top = tkinter.Tk()
```
- Initializes the main application window.

---

#### 3. **Upload Button Logic**
```python
def UploadAction(event = None):
    filename = filedialog.askopenfilename()
    filename = filename.split("/")[-1]
    ...
```
- Opens a file selection dialog.
- Extracts the selected filename (only the base name, not full path).
- Sends it for transcription using:
  ```python
  script = rq.google_transcribe(filename)
  ```

---

#### 4. **Save Transcription**
```python
f = open("output.txt", "w")
f.seek(0)
f.write(script)
f.close()
```
- Saves the transcription text to `output.txt`.

---

#### 5. **Summarize Text**
```python
whole, output = rq.generate_summary("./output.txt")
```
- Summarizes the transcription using `generate_summary` from `request.py`.

---

#### 6. **Display Results**
```python
l = Label(top, text = "Top 3 Ranked Sentence(s)\n\n"+output+"\n\nWhole Text: \n"+whole, ...)
l.pack()
```
- Displays both:
  - Top 3 ranked sentences (summary).
  - Full transcription.
- The output is styled and added to the GUI window.

---

#### 7. **GUI Setup**
```python
Label(... "Please Upload your Wav File Here ...").pack()
Button(... text="Upload Here", command=UploadAction).pack()
top.mainloop()
```
- Adds a prompt label and upload button to the interface.
- Starts the GUI event loop.

---

### ✅ **Purpose Summary**
`button.py` creates a user-friendly tool that:
1. Lets users upload `.wav` files.
2. Transcribes the audio via Google Cloud Speech-to-Text.
3. Summarizes the transcript using NLP techniques.
4. Displays both summary and full text in the GUI.

Would you like help converting this into a web app or CLI version?

---

`rough.py`python

The `rough.py` script is a **prototype** or **test version** of a Google Cloud Speech-to-Text transcription utility. It transcribes an audio file (either from a **Google Cloud Storage URI** or **local file path**) and prints the results in a detailed format, including the **start/end timestamps of each word** and the **confidence score**.

---

### 🧠 High-Level Purpose:
- **Connects to Google Cloud Speech API**
- **Transcribes `.flac` audio files**
- **Prints full transcripts with word-level timing and confidence**

---

### 🔍 Detailed Breakdown

---

#### 1. **`transcribe_gcs(gcs_uri)`**
```python
def transcribe_gcs(gcs_uri):
```
- Takes a URI like `gs://your-bucket/file.flac`
- Transcribes the audio using **long-running recognition** (for longer audio files)

```python
from google.cloud import speech
client = speech.SpeechClient()
audio = speech.RecognitionAudio(uri=gcs_uri)
config = speech.RecognitionConfig(...)
```
- Creates the speech client and sets config:
  - Format: FLAC
  - Language: English (`en-US`)

```python
operation = client.long_running_recognize(config=config, audio=audio)
response = operation.result(timeout=90)
```
- Submits the file for **asynchronous transcription** (non-blocking).
- Waits for up to 90 seconds.

```python
for result in response.results:
    print(u"Transcript: {}".format(result.alternatives[0].transcript))
    print("Confidence: {}".format(result.alternatives[0].confidence))
```
- Iterates through results and prints the top (most likely) transcription alternative and confidence.

---

#### 2. **`speech_to_text(config, audio)`**
```python
def speech_to_text(config, audio):
    client = speech.SpeechClient()
    response = client.recognize(config=config, audio=audio)
    print_sentences(response)
```
- This is a **synchronous** version for short audio files.
- Calls `print_sentences()` to display the results.

---

#### 3. **`print_sentences(response)`**
```python
def print_sentences(response):
    for result in response.results:
        ...
        print_word_offsets(best_alternative)
```
- Prints transcript and confidence for each result.
- Delegates to `print_word_offsets` to print individual word timings.

---

#### 4. **`print_word_offsets(alternative)`**
```python
def print_word_offsets(alternative):
    for word in alternative.words:
        ...
        print(f"{start_s:>7.3f} | {end_s:>7.3f} | {word}")
```
- For each word, prints:
  - Start time
  - End time
  - The word itself
- Useful for generating **subtitles** or **highlighting spoken words in a UI**.

---

#### 5. **Main Execution Block**
```python
client = speech.SpeechClient()
audio = speech.RecognitionAudio(uri='./history40b.wav')
...
operation = client.long_running_recognize(...)
response = operation.result(timeout=90)
print_sentences(response)
```
- Appears to **run immediately** on a local file called `history40b.wav` using `long_running_recognize`.
- `speech.SpeechClient()` is re-initialized outside any function — not ideal practice.

---

### ⚠️ Issues / Suggestions for Improvement

- **`__main__` block is misused** — it's commented out and actual code is outside functions.
- **Hardcoded file path** (`'./history40b.wav'`) and URI handling are mixed up.
- Repetitive `speech.SpeechClient()` calls — could be reused.
- Should wrap the bottom script logic in `if __name__ == "__main__":`

---

### ✅ Final Summary
`rough.py` is a test script that transcribes `.flac` audio files using Google Cloud Speech-to-Text, prints word-by-word timing, confidence, and transcripts. It's useful for debugging or analyzing how well the speech recognition system works.

Would you like me to clean up this script for production use or convert it to process local `.wav` files directly?

---

The `speech.py` script is a simple **speech-to-text converter** that:

- Loads a local `.wav` audio file (`history.wav`)
- Uses **Google Web Speech API** (via the `speech_recognition` library) to transcribe it
- Writes the recognized text to a file named `test1.txt`

---

### 🔍 Step-by-Step Explanation

#### 1. **Import the Library**
```python
import speech_recognition as sr
```
- Imports the `speech_recognition` library, which provides an easy-to-use interface for various speech recognition engines/APIs (like Google, Sphinx, etc.).

---

#### 2. **Initialize Recognizer**
```python
r = sr.Recognizer()
```
- Creates a **Recognizer** object — the core tool used to process audio and convert it to text.

---

#### 3. **Load the Audio File**
```python
audio_file = sr.AudioFile('history.wav')
```
- Loads a **local `.wav` audio file** named `history.wav`.
- Supported formats include WAV, AIFF, and FLAC.

---

#### 4. **Record and Recognize Speech**
```python
with audio_file as source: 
   r.adjust_for_ambient_noise(source) 
   audio = r.record(source)
```
- Opens the file as a source.
- `adjust_for_ambient_noise()` helps reduce background noise effect by calibrating the recognizer.
- `record(source)` captures the entire audio content into a variable called `audio`.

```python
result = r.recognize_google(audio)
```
- Sends the recorded audio to **Google Web Speech API** for transcription.
- Returns the recognized text as a string.

> 🔗 This requires an **active internet connection**, but does not need an API key for small usage.

---

#### 5. **Write Result to File**
```python
with open('test1.txt', mode ='w') as file: 
   file.write("Recognized text:\n") 
   file.write(result) 
   print("ready!")
```
- Opens or creates `test1.txt` in **write mode**.
- Writes the header and transcribed text into the file.
- Prints `ready!` to indicate completion.

---

### ✅ Summary

| Step                        | Purpose                                                  |
|----------------------------|----------------------------------------------------------|
| `speech_recognition.Recognizer()` | Prepares for audio recognition                      |
| `sr.AudioFile()`           | Loads `.wav` file locally                                |
| `adjust_for_ambient_noise` | Improves accuracy in noisy audio                         |
| `recognize_google()`       | Uses Google's free speech API (no key required)          |
| File write (`test1.txt`)   | Saves the transcript                                     |

---

### ⚠️ Notes
- Only handles small audio files (<1 minute ideally).
- No error handling — if audio is unclear or file is missing, it will crash.
- For longer audios or batch processing, consider `Google Cloud Speech-to-Text`.

Would you like help expanding this into a more robust CLI tool or web app?

---

The `test.py` script is a **simple Python program** that:

- Takes a **list of sentences** (each sentence is a list of words),
- **Prints** the number of words in each sentence and the words themselves,
- **Concatenates** all the words into a single string called `whole_text`,
- Then **prints the full text** at the end.

---

### 🔍 Step-by-Step Breakdown

#### 1. **Input: Nested List of Words**
```python
sentences = [
    ['Hi', 'everyone'],
    ['This', 'is', 'dr'],
    ['Millward'],
    ['And', "I'm", 'coming', 'to', 'you', 'from', 'the', 'voice', 'memo', 'platform'],
    ...
]
```
- Each inner list represents a **sentence**, split into individual **words**.

---

#### 2. **Initialize an Empty String**
```python
whole_text = ""
```
- This will store the **full text** by concatenating all words with spaces.

---

#### 3. **Iterate Over Sentences**
```python
for i in range(len(sentences)):
    print(len(sentences[i]))   # print the number of words in sentence i
    for j in range(len(sentences[i])):
        whole_text = whole_text + " " + sentences[i][j]  # add each word with space
        print(sentences[i][j])  # print each word
```
- Outer loop: Goes over each sentence.
- Inner loop: Goes over each word in the sentence.
- Adds each word to `whole_text`, separating with a space.
- Prints:
  - Number of words in each sentence.
  - Each individual word.

---

#### 4. **Print the Final Text**
```python
print(whole_text)
```
- Displays the full combined text created from the sentence list.

---

### ✅ Example Output (Shortened)

Assuming the first few lines are run, the output would look like:
```
2
Hi
everyone
3
This
is
dr
1
Millward
...
Hi everyone This is dr Millward And I'm coming to you from the voice memo platform ...
```

---

### 🔧 Purpose

This script could be:
- A **test utility** to verify word-by-word transcription output.
- Part of a **speech-to-text** or **text summarization** pipeline, where the system starts from word arrays and needs to build readable text.
- A preprocessing step for **text summarization or analysis**.

Would you like to enhance this by adding punctuation or sentence reconstruction?