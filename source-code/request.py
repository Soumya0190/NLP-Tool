# === Import necessary libraries ===
import os  # For environment variables and file paths
import wave  # For reading audio metadata
from pydub import AudioSegment  # For audio processing (e.g., stereo to mono conversion)
import speech_recognition as sr  # Local speech recognition library (not used here, but imported)
from google.cloud import storage, speech  # Google Cloud libraries for Storage and Speech-to-Text

# NLP and summarization libraries
import nltk
import numpy as np  # For numerical operations (e.g., similarity matrix)
import networkx as nx  # For graph-based ranking (TextRank)
from nltk.corpus import stopwords  # Stopwords removal
from nltk.cluster.util import cosine_distance  # Sentence similarity calculation
from nltk.tokenize import sent_tokenize  # Sentence tokenization

# === Download required NLTK data ===
nltk.download('stopwords')  # Common words to ignore (e.g., "the", "is", "and")
nltk.download('punkt')  # Pre-trained tokenizer model

# === Configure Google Cloud credentials and target bucket ===
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../uci-hackathon-project-65679fcbb285.json"
BUCKET_NAME = "my-audio-transcriber-bucket"

# === Function: Upload audio file to Google Cloud Storage ===
def upload_to_gcs(file_path):
    """
    Uploads a local audio file to a specified Google Cloud Storage bucket.
    Returns the GCS URI needed for transcription.
    """
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(os.path.basename(file_path))
    blob.upload_from_filename(file_path)
    return f"gs://{BUCKET_NAME}/{os.path.basename(file_path)}"

# === Function: Convert stereo to mono ===
def stereo_to_mono(audio_file_name):
    """
    Converts a stereo audio file to mono (Google Speech API requires mono audio).
    Overwrites the original file.
    """
    sound = AudioSegment.from_wav(audio_file_name)
    sound = sound.set_channels(1)
    sound.export(audio_file_name, format="wav")

# === Function: Get audio frame rate and channels ===
def get_frame_rate_and_channels(file_path):
    """
    Extracts the frame rate (sample rate) and number of channels (mono/stereo) from an audio file.
    """
    with wave.open(file_path, "rb") as wf:
        return wf.getframerate(), wf.getnchannels()

# === Main transcription and summarization pipeline ===
def google_transcribe(file_path, output_file="output.txt"):
    """
    Transcribes a .wav audio file using Google Speech-to-Text,
    writes the full transcription and summary to an output file,
    and returns the full transcription as a string.
    """
    # Check if audio needs to be converted to mono
    frame_rate, channels = get_frame_rate_and_channels(file_path)
    if channels > 1:
        stereo_to_mono(file_path)

    # Upload to Google Cloud Storage
    gcs_uri = upload_to_gcs(file_path)

    # Set up Google Speech-to-Text client and config
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=frame_rate,
        language_code="en-US",
        enable_automatic_punctuation=True,
    )

    # Start long-running asynchronous recognition
    operation = client.long_running_recognize(config=config, audio=audio)
    print("Waiting for operation to complete...")
    response = operation.result(timeout=300)

    # Merge all returned transcription chunks into a single string
    transcript = " ".join([result.alternatives[0].transcript for result in response.results])
    sentences = sent_tokenize(transcript)

    # Save raw transcription to file
    with open(output_file, "w") as f:
        f.write("=== Transcription ===\n")
        for sentence in sentences:
            f.write(sentence.strip() + "\n")

    # Generate summary and top-ranked sentences
    full_text, summary = generate_summary_from_text(transcript)

    # Save summary to the same file
    with open(output_file, "a") as f:
        f.write("\n=== Summary ===\n")
        f.write(summary.strip() + "\n")
        f.write("\n=== Top 3 Important Sentences ===\n")
        for i, line in enumerate(rank_sentences(transcript), start=1):
            f.write(f"{i}. {line.strip()}\n")

    return transcript

# === Function: Create summary using TextRank ===
def generate_summary_from_text(text):
    """
    Generates a short summary from the input text by selecting the 3 most important sentences.
    Uses a graph-based ranking algorithm (TextRank).
    """
    sentences = sent_tokenize(text)
    if len(sentences) < 3:
        return text, text  # Not enough data to summarize

    stop_words = stopwords.words("english")
    sentence_vectors = [sent.split() for sent in sentences]  # Tokenize each sentence
    sim_matrix = build_similarity_matrix(sentence_vectors, stop_words)  # Calculate sentence similarities

    # Build graph and compute sentence ranks using PageRank
    graph = nx.from_numpy_array(sim_matrix)
    scores = nx.pagerank(graph)

    # Sort sentences by their score
    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)

    # Select top 3 sentences
    summary = "\n".join([ranked_sentences[i][1] for i in range(min(3, len(ranked_sentences)))])
    return text, summary

# === Function: Build similarity matrix ===
def build_similarity_matrix(sentences, stop_words):
    """
    Creates a similarity matrix between all pairs of sentences using cosine similarity.
    """
    size = len(sentences)
    sim_matrix = np.zeros((size, size))  # Initialize square matrix

    for i in range(size):
        for j in range(size):
            if i != j:
                sim_matrix[i][j] = sentence_similarity(sentences[i], sentences[j], stop_words)
    return sim_matrix

# === Function: Cosine similarity between two tokenized sentences ===
def sentence_similarity(sent1, sent2, stop_words=None):
    """
    Computes cosine similarity between two tokenized sentences using a bag-of-words approach.
    Ignores stopwords.
    """
    if stop_words is None:
        stop_words = []

    all_words = list(set(sent1 + sent2))  # Unique words from both sentences

    # Convert sentences to vector representation
    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)

    for w in sent1:
        if w not in stop_words:
            vector1[all_words.index(w)] += 1

    for w in sent2:
        if w not in stop_words:
            vector2[all_words.index(w)] += 1

    # Return cosine similarity (1 - distance)
    return 1 - cosine_distance(vector1, vector2)

# === Function: Return top 3 ranked sentences ===
def rank_sentences(text):
    """
    Wrapper to extract and return the top 3 most central sentences from the text.
    """
    _, summary = generate_summary_from_text(text)
    return summary.split('\n')
