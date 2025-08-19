import os
import subprocess

# Paths
WHISPER_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WHISPER_EXECUTABLE = os.path.join(WHISPER_BASE_DIR, 'build', 'bin', 'Release', 'whisper-cli.exe')
MODELS_DIR = os.path.join(WHISPER_BASE_DIR, 'models')
SAMPLES_DIR = os.path.join(WHISPER_BASE_DIR, 'samples')

MODEL_NAME = 'ggml-base.bin'
SAMPLE_FILE = 'jfk.wav'

MODEL_PATH = os.path.join(MODELS_DIR, MODEL_NAME)
SAMPLE_PATH = os.path.join(SAMPLES_DIR, SAMPLE_FILE)

print(f"Whisper executable: {WHISPER_EXECUTABLE}")
print(f"Model path: {MODEL_PATH}")
print(f"Sample path: {SAMPLE_PATH}")

# Check if files exist
if not os.path.exists(WHISPER_EXECUTABLE):
    print(f"ERROR: Whisper executable not found at {WHISPER_EXECUTABLE}")
    exit()

if not os.path.exists(MODEL_PATH):
    print(f"ERROR: Model not found at {MODEL_PATH}")
    exit()

if not os.path.exists(SAMPLE_PATH):
    print(f"ERROR: Sample audio file not found at {SAMPLE_PATH}")
    exit()

# Construct command
cmd = [WHISPER_EXECUTABLE, '-m', MODEL_PATH, '-f', SAMPLE_PATH]

print(f"\nRunning command: {' '.join(cmd)}\n")

# Execute command
try:
    result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
    print("---" + " Transcription" + " ---")
    print(result.stdout)
    print("---------------------")
    print("Test completed successfully!")
except subprocess.CalledProcessError as e:
    print("---" + " ERROR" + " ---")
    print(f"Whisper.cpp execution failed with exit code {e.returncode}")
    print("Stderr:")
    print(e.stderr)
    print("-------------")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
