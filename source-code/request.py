import os
import wave
from pydub import AudioSegment
import speech_recognition as sr
from google.cloud import storage, speech

import nltk
import numpy as np
import networkx as nx
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
from nltk.tokenize import sent_tokenize

# Download required nltk data
nltk.download('stopwords')
nltk.download('punkt')

# Set your Google Cloud service account key file path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../uci-hackathon-project-65679fcbb285.json"
BUCKET_NAME = "my-audio-transcriber-bucket"

def upload_to_gcs(file_path):
    """Uploads the audio file to Google Cloud Storage."""
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(os.path.basename(file_path))
    blob.upload_from_filename(file_path)
    return f"gs://{BUCKET_NAME}/{os.path.basename(file_path)}"

def stereo_to_mono(audio_file_name):
    """Converts stereo audio to mono (required for transcription)."""
    sound = AudioSegment.from_wav(audio_file_name)
    sound = sound.set_channels(1)
    sound.export(audio_file_name, format="wav")

def get_frame_rate_and_channels(file_path):
    """Extracts frame rate and number of channels."""
    with wave.open(file_path, "rb") as wf:
        return wf.getframerate(), wf.getnchannels()

def google_transcribe(file_path, output_file="output.txt"):
    """Transcribes audio using Google Cloud Speech-to-Text."""
    frame_rate, channels = get_frame_rate_and_channels(file_path)
    if channels > 1:
        stereo_to_mono(file_path)

    gcs_uri = upload_to_gcs(file_path)
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=frame_rate,
        language_code="en-US",
        enable_automatic_punctuation=True,
    )

    operation = client.long_running_recognize(config=config, audio=audio)
    print("Waiting for operation to complete...")
    response = operation.result(timeout=300)

    # Combine all transcribed chunks
    transcript = " ".join([result.alternatives[0].transcript for result in response.results])
    sentences = sent_tokenize(transcript)

    # Save transcription
    with open(output_file, "w") as f:
        f.write("=== Transcription ===\n")
        for sentence in sentences:
            f.write(sentence.strip() + "\n")

    # Generate summary
    full_text, summary = generate_summary_from_text(transcript)

    # Append summary to file
    with open(output_file, "a") as f:
        f.write("\n=== Summary ===\n")
        f.write(summary.strip() + "\n")
        f.write("\n=== Top 3 Important Sentences ===\n")
        for i, line in enumerate(rank_sentences(transcript), start=1):
            f.write(f"{i}. {line.strip()}\n")

    return transcript

def generate_summary_from_text(text):
    """Extracts 3 most central sentences from text using graph-based ranking."""
    sentences = sent_tokenize(text)
    if len(sentences) < 3:
        return text, text  # Not enough for summary

    stop_words = stopwords.words("english")
    sentence_vectors = [sent.split() for sent in sentences]
    sim_matrix = build_similarity_matrix(sentence_vectors, stop_words)

    graph = nx.from_numpy_array(sim_matrix)
    scores = nx.pagerank(graph)

    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    summary = "\n".join([ranked_sentences[i][1] for i in range(min(3, len(ranked_sentences)))])
    return text, summary

def build_similarity_matrix(sentences, stop_words):
    """Builds a matrix of cosine similarities between sentences."""
    size = len(sentences)
    sim_matrix = np.zeros((size, size))

    for i in range(size):
        for j in range(size):
            if i != j:
                sim_matrix[i][j] = sentence_similarity(sentences[i], sentences[j], stop_words)
    return sim_matrix

def sentence_similarity(sent1, sent2, stop_words=None):
    """Computes cosine similarity between two tokenized sentences."""
    if stop_words is None:
        stop_words = []

    all_words = list(set(sent1 + sent2))

    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)

    for w in sent1:
        if w not in stop_words:
            vector1[all_words.index(w)] += 1

    for w in sent2:
        if w not in stop_words:
            vector2[all_words.index(w)] += 1

    return 1 - cosine_distance(vector1, vector2)

def rank_sentences(text):
    """Returns top 3 most important sentences."""
    _, summary = generate_summary_from_text(text)
    return summary.split('\n')
