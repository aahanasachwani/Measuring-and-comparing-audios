import threading
import sys

try:
    import pyaudio
    import numpy as np
    import matplotlib.pyplot as plt
    import speech_recognition as sr
    from speech_recognition import AudioData
except ImportError as e:
    print(f"Missing library : {e.name}")
    sys.exit()

stop_event = threading.Event()

def wait_for_enter():
    input()
    stop_event.set()

def record_audio(label):
    stop_event.clear()
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=1024
    )

    frames = []
    print(f"\n{label}")
    print("Press Enter to stop.....")
    threading.Thread(target=wait_for_enter, daemon=True).start()

    print("Recording", end="", flush=True)
    while not stop_event.is_set():
        frames.append(stream.read(1024, exception_on_overflow=False))
        print(".", end="", flush=True)

    print("\nDONE")

    stream.stop_stream()
    stream.close()
    width = p.get_sample_size(pyaudio.paInt16)
    p.terminate()

    return b"".join(frames), 16000, width

def analyse_audio(data, rate):
    samples = np.frombuffer(data, dtype=np.int16)
    return {
        "duration": len(samples) / rate,
        "avg_volume": np.mean(np.abs(samples)),
        "max_volume": np.max(np.abs(samples)),
        "samples": samples
    }

def transcribe(data, rate, width):
    recognizer = sr.Recognizer()
    try:
        return recognizer.recognize_google(AudioData(data, rate, width))
    except:
        return "[Could not transcribe]"

def display_stats(stats, text, label):
    print("\n" + "-" * 35)
    print(label)
    print("-" * 35)
    print(f"Duration   : {stats['duration']:.2f} sec")
    print(f"Avg volume : {stats['avg_volume']:.0f}")
    print(f"Max volume : {stats['max_volume']:.0f}")
    print(f"Text       : {text}")

def compare(s1, s2):
    print("\n" + "=" * 40)
    print("COMPARISON RESULTS")
    print("=" * 40)

    longer = "1" if s1["duration"] > s2["duration"] else "2"
    print(f"Recording {longer} is longer ({s1['duration']:.1f}s vs {s2['duration']:.1f}s)")

    louder = "1" if s1["avg_volume"] > s2["avg_volume"] else "2"
    print(f"Recording {louder} is louder ({s1['avg_volume']:.1f} vs {s2['avg_volume']:.1f})")

def plot_both(s1, s2, rate):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5))

    t1 = np.linspace(0, len(s1["samples"]) / rate, len(s1["samples"]))
    ax1.plot(t1, s1["samples"])
    ax1.set_title("Recording 1 (Normal)")
    ax1.set_ylabel("Amplitude")
    ax1.grid(True, alpha=0.3)

    t2 = np.linspace(0, len(s2["samples"]) / rate, len(s2["samples"]))
    ax2.plot(t2, s2["samples"])
    ax2.set_title("Recording 2 (Modified)")
    ax2.set_xlabel("Time (seconds)")
    ax2.set_ylabel("Amplitude")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

def main():
    print("=" * 40)
    print("Voice Analysis Lab")
    print("=" * 40)
    print("Record twice and compare your voice!")

    audio1, rate, width = record_audio("Recording 1: Speak NORMALLY")
    stats1 = analyse_audio(audio1, rate)
    text1 = transcribe(audio1, rate, width)
    display_stats(stats1, text1, "Recording 1")

    input("\nPress Enter, then speak LOUDER or FASTER...")
    audio2, rate, width = record_audio("Recording 2: CHANGE YOUR VOICE")
    stats2 = analyse_audio(audio2, rate)
    text2 = transcribe(audio2, rate, width)
    display_stats(stats2, text2, "Recording 2")

    compare(stats1, stats2)
    plot_both(stats1, stats2, rate)

if __name__ == "__main__":
    main()
