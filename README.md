# NLP-Tool
https://devpost.com/software/lecture-summary-generator

YouTube Video Demo Link: https://youtu.be/LY9jxuDBuro

# 🎙️ Audio Transcriber & Summarizer

This Python desktop application allows you to upload a `.wav` file, transcribe the speech using **Google Cloud Speech-to-Text**, and summarize the contents using **NLP techniques**. It's built using `tkinter` for the GUI and integrates Google Cloud APIs for powerful speech recognition.

---

## 💡 Notes

* Billing must be enabled on your GCP project to use Speech-to-Text API beyond the free tier.
* This app only supports `.wav` files as input.
* For transcription longer than a minute, Google Cloud uses asynchronous (long-running) transcription.

---

## ✅ 1. Prerequisites

### 📦 Python Dependencies

Install all required Python packages using:

```bash
pip install -r requirements.txt
```

---

## ✅ 2. Steps Needed in Google Cloud to Run This Project

To use this application, you'll need to enable and configure **Google Cloud services**.

---

## 🔧 Google Cloud Setup Guide

###  💳 1. **Enable Billing**

1. Go to [Google Cloud Console Billing: https://console.cloud.google.com/billing](https://console.cloud.google.com/billing)
2. Attach your billing account to your Google Cloud project (required to use any APIs)

### ☁️ 1. **Create a Google Cloud Project**

1. Visit [Google Cloud Console Projects: https://console.cloud.google.com/projectcreate](https://console.cloud.google.com/projectcreate)
2. Click on the top-left dropdown → **New Project**
3. Give it a name like `audio-transcriber-project` and click **Create**

---

### 🔑 2. **Enable Required APIs**

In the sidebar:

1. Go to `APIs & Services` → `Library`
2. Enable these two APIs:

   * ✅ **[Cloud Speech-to-Text API: https://console.cloud.google.com/marketplace/product/google/speech.googleapis.com](https://console.cloud.google.com/marketplace/product/google/speech.googleapis.com)**
   * ✅ **Cloud Storage API**

---

### 🧪 3. **Create a Service Account**

1. Navigate to `IAM & Admin` → `Service Accounts` [https://console.cloud.google.com/iam-admin/serviceaccounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Click **"Create Service Account"**
3. Name it something like `audio-summarizer`
4. Grant role: Project > Owner
5. Continue & click "Done"
6. Once created, go to its **"Keys"** tab ; Click on your new service account > Keys > Add Key > Create new key
7. Click **"Add Key"** → `JSON` → Download the file
8. 💾 Move the key.JSON file to the project folder
9. 📌 Project will be calling this key.JSON credentials file, so the filepath will need to be updated in the source code.

---

### 🎯 4. **Grant Permissions to Service Account**

Give the service account these roles:

* ✅ **Storage Admin**
* ✅ **Speech-to-Text Admin**

You can assign these during service account creation or later via `IAM`.

---

### 🪣 5. **Create a Cloud Storage Bucket**

1. Go to [GCS Buckets: https://console.cloud.google.com/storage/browser](https://console.cloud.google.com/storage/browser) `Cloud Storage` → `Buckets` → **"Create Bucket"**
2. Choose a globally unique name like: `my-audio-transcriber-bucket`
3. Pick a **region** (preferably the same as your Speech API) (e.g., multi-region: us)
4. Leave default permissions

📌 In `request.py`, set this bucket name:

```python
BUCKET_NAME = "my-audio-transcriber-bucket"
```

---

### 🔐 6. **Configure Authentication Locally**

In your code (`request.py`), make sure this line points to the JSON key:

```python
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../uci-hackathon-project-65679fcbb285.json"
```

Alternatively, set it as an environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="../path/to/your-key.json"
```

---

### 🧪 7. **Run the App**

Run the main file:

```bash
python button.py
```

Use the GUI to upload a `.wav` file. It will:

* Transcribe the audio via Google Cloud Speech-to-Text
* Summarize the transcription using an NLP algorithm
* Display both in the interface

---

## 🧠 How It Works

### 💬 Speech Transcription

* Converts stereo to mono if needed
* Uploads audio to Google Cloud Storage
* Uses Google Speech-to-Text to transcribe audio

### 📝 Text Summarization

* Tokenizes and ranks sentences using `networkx` and cosine similarity
* Displays the most important 3 sentences as a summary

---

## 🧩 Project Structure

```bash
├── button.py            # GUI logic
├── request.py           # GCP transcription and NLP summary logic
├── requirements.txt     # Python dependencies
└── ../key.json          # Service account key (Not shared)
```

---




