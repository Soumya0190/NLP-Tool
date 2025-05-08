import request as rq
import nltk
nltk.download('stopwords')

def main():
    input_wav = "../audio-files/history.wav"  # Your audio file path

    # Step 1: Transcribe the audio
    print("Transcribing audio...")
    transcript = rq.google_transcribe(input_wav)

    print("\n=== FULL TRANSCRIPT ===\n")
    print(transcript)

    # Step 2: Summarize and rank important sentences
    print("\n=== SUMMARY AND RANKED SENTENCES ===")
    _, summary = rq.generate_summary_from_text(transcript)
    print(summary)

if __name__ == "__main__":
    main()
