def transcribe_gcs(gcs_uri):
    """Asynchronously transcribes the audio file specified by the gcs_uri."""
    from google.cloud import speech
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        language_code="en-US",
    )
    operation = client.long_running_recognize(config=config, audio=audio)
    
    print("Waiting for operation to complete...")
    response = operation.result(timeout=90)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        print(u"Transcript: {}".format(result.alternatives[0].transcript))
        print("Confidence: {}".format(result.alternatives[0].confidence))

if __name__ == "__main__":
    print("In Main")
    #video()
    #transcribe_gcs("gs://hack-uci-2021-bucket/history.wav")

def speech_to_text(config, audio):
    client = speech.SpeechClient()
    response = client.recognize(config=config, audio=audio)
    print_sentences(response)


def print_sentences(response):
    for result in response.results:
        best_alternative = result.alternatives[0]
        transcript = best_alternative.transcript
        confidence = best_alternative.confidence
        print("-" * 80)
        print(f"Transcript: {transcript}")
        print(f"Confidence: {confidence:.0%}")
        print_word_offsets(best_alternative)

def print_word_offsets(alternative):
    for word in alternative.words:
        start_s = word.start_time.total_seconds()
        end_s = word.end_time.total_seconds()
        word = word.word
        print(f"{start_s:>7.3f} | {end_s:>7.3f} | {word}")

client = speech.SpeechClient()
audio = speech.RecognitionAudio(uri='./history40b.wav')
config = speech.RecognitionConfig(encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
    language_code="en-US",
    enable_automatic_punctuation=True,
    enable_word_time_offsets=True
)
operation = client.long_running_recognize(config=config, audio=audio)
response = operation.result(timeout=90)

print_sentences(response)
