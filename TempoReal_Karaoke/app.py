import logging
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
import os
import subprocess
import threading
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed_videos'
socketio = SocketIO(app, async_mode='gevent')

# Configure logging
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(log_dir, 'TEMPOREAL_KARAOKE.log')
# Setup file handler with error handling
try:
    file_handler = logging.FileHandler(log_file_path, mode='a')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_handler)
    logging.getLogger().setLevel(logging.INFO)
except PermissionError:
    print(f"Permission denied to write to {log_file_path}. Logging to console only.")
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app.logger.addHandler(logging.StreamHandler())

# Dictionary to hold the processes for each client
client_processes = {}

# --- Helper Functions --- #

def stream_stdout(sid, stdout):
    """Read stdout from the whisper process and emit it to the client."""
    for line in iter(stdout.readline, b''):
        socketio.emit('stt_result', {'text': line.decode('utf-8', errors='ignore')}, room=sid)
    stdout.close()

def get_base_dir():
    return os.path.dirname(os.path.abspath(__file__))

# --- SocketIO Handlers --- #

@app.route('/')
def index():
    # Scan the models directory for available .bin files
    models_dir = os.path.join(get_base_dir(), '..', '..', 'models')
    available_models = []
    app.logger.info(f"Checking models directory: {models_dir}")
    if os.path.exists(models_dir):
        app.logger.info(f"Models directory exists.")
        try:
            dir_contents = os.listdir(models_dir)
            app.logger.info(f"Models directory contents: {dir_contents}")
            available_models = [f for f in dir_contents if f.endswith('.bin')]
        except Exception as e:
            app.logger.error(f"Error reading models directory: {e}")
    else:
        app.logger.warning(f"Models directory not found at: {models_dir}")
    app.logger.info(f"Available models: {available_models}")
    return render_template('index.html', models=available_models)

@app.route('/favicon.ico')
def favicon():
    return '', 204

@socketio.on('connect')
def handle_connect():
    app.logger.info(f'Client connected: {request.sid}')

@socketio.on('start_stream')
def handle_start_stream(data):
    model_name = data.get('model', 'ggml-base.en.bin')
    app.logger.info(f'Starting stream for {request.sid} with model {model_name}')

    base_dir = get_base_dir()
    model_path = os.path.join(base_dir, "..", "..", "models", model_name)

    app.logger.info(f"Attempting to load model from: {model_path}")
    if not os.path.exists(model_path):
        app.logger.error(f"Model file not found: {model_name} at {model_path}")
        emit('stt_error', {'error': f'Model file not found: {model_name}'})
        return

    whisper_executable_path = os.path.join(base_dir, "..", "..", "build", "bin", "Release", "stream.exe")
    ffmpeg_executable_path = os.path.join(base_dir, "ffmpeg", "bin", "ffmpeg.exe")

    ffmpeg_command = [ffmpeg_executable_path, '-i', 'pipe:0', '-f', 's16le', '-ar', '16000', '-ac', '1', 'pipe:1']
    whisper_command = [whisper_executable_path, "-m", model_path, "-t", "8", "--step", "500", "--length", "5000", "--mic-id", "-1"]

    try:
        ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        whisper_process = subprocess.Popen(whisper_command, stdin=ffmpeg_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        client_processes[request.sid] = {'ffmpeg': ffmpeg_process, 'whisper': whisper_process}
        
        stdout_thread = threading.Thread(target=stream_stdout, args=(request.sid, whisper_process.stdout))
        stdout_thread.daemon = True
        stdout_thread.start()
        app.logger.info(f"Started ffmpeg and whisper processes for {request.sid}")

    except FileNotFoundError as e:
        app.logger.error(f"Error starting subprocess: {e}")
        emit('stt_error', {'error': f'A required executable was not found: {e.filename}'})
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        emit('stt_error', {'error': str(e)})


@socketio.on('disconnect')
def handle_disconnect():
    app.logger.info(f'Client disconnected: {request.sid}')
    if request.sid in client_processes:
        processes = client_processes.pop(request.sid)
        if processes.get('ffmpeg'): processes['ffmpeg'].terminate(); processes['ffmpeg'].wait()
        if processes.get('whisper'): processes['whisper'].terminate(); processes['whisper'].wait()
        app.logger.info(f"Terminated processes for {request.sid}")

@socketio.on('audio_stream')
def handle_audio_stream(stream):
    if request.sid in client_processes:
        try:
            client_processes[request.sid]['ffmpeg'].stdin.write(stream)
            client_processes[request.sid]['ffmpeg'].stdin.flush()
        except (BrokenPipeError, IOError):
            app.logger.warning(f"Broken pipe for client {request.sid}.")

# --- HTTP Routes for Tabs 2 & 3 --- #

@app.route('/processed/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename, as_attachment=True)

@app.route('/preprocess_audio', methods=['POST'])
def preprocess_audio():
    if 'audioFile' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400
    file = request.files['audioFile']
    model_name = request.form.get('model', 'ggml-base.en.bin')
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        temp_filename = f"{uuid.uuid4()}_{filename}"
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        file.save(input_path)

        # Convert to WAV and transcribe
        output_wav_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}.wav")
        transcription, error = transcribe_file(input_path, output_wav_path, model_name)

        # Clean up temporary files
        os.remove(input_path)
        if os.path.exists(output_wav_path):
            os.remove(output_wav_path)

        if error:
            return jsonify({"status": "error", "message": error})
        else:
            return jsonify({"status": "success", "transcription": transcription})

def transcribe_file(input_path, output_wav_path, model_name):
    base_dir = get_base_dir()
    model_path = os.path.join(base_dir, "..", "..", "models", model_name)
    app.logger.info(f"Attempting to transcribe with model from: {model_path}")
    if not os.path.exists(model_path):
        app.logger.error(f"Model file not found for transcription: {model_name} at {model_path}")
        return None, f"Model file not found: {model_name}"

    main_executable_path = os.path.join(base_dir, "..", "..", "build", "bin", "Release", "main.exe")
    ffmpeg_executable_path = os.path.join(base_dir, "ffmpeg", "bin", "ffmpeg.exe")

    try:
        # Convert to 16kHz mono WAV
        ffmpeg_command = [ffmpeg_executable_path, '-i', input_path, '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', output_wav_path]
        subprocess.run(ffmpeg_command, check=True, capture_output=True)

        # Transcribe with whisper.cpp
        whisper_command = [main_executable_path, "-m", model_path, "-f", output_wav_path]
        result = subprocess.run(whisper_command, check=True, capture_output=True, text=True)
        
        return result.stdout, None

    except subprocess.CalledProcessError as e:
        app.logger.error(f"Subprocess error during transcription: {e.stderr.decode('utf-8', errors='ignore')}")
        return None, e.stderr.decode('utf-8', errors='ignore')
    except FileNotFoundError as e:
        app.logger.error(f"Executable not found during transcription: {e.filename}")
        return None, f"Executable not found: {e.filename}"
    except Exception as e:
        app.logger.error(f"An unexpected error occurred during transcription: {e}")
        return None, str(e)

@app.route('/generate_video', methods=['POST'])
def generate_video():
    if 'videoFile' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400
    file = request.files['videoFile']
    model_name = request.form.get('model', 'ggml-base.en.bin')
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1]
        unique_id = uuid.uuid4()
        
        # Define paths for all our files
        input_video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}{ext}")
        extracted_audio_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}.wav")
        srt_path_base = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}.wav") # main.exe creates srt with same name
        
        file.save(input_video_path)

        # Run the generation process
        error = process_video_for_srt(input_video_path, extracted_audio_path, srt_path_base, model_name)

        # Construct the final path for the subtitled video
        output_video_path = os.path.join(app.config['PROCESSED_FOLDER'], f"subtitled_{unique_id}{ext}")

        if error:
            # Clean up even if there's an error
            if os.path.exists(input_video_path): os.remove(input_video_path)
            if os.path.exists(extracted_audio_path): os.remove(extracted_audio_path)
            if os.path.exists(f"{srt_path_base}.srt"): os.remove(f"{srt_path_base}.srt")
            return jsonify({"status": "error", "message": error})
        else:
            # Clean up temporary files, keep the final video
            if os.path.exists(input_video_path): os.remove(input_video_path)
            if os.path.exists(extracted_audio_path): os.remove(extracted_audio_path)
            if os.path.exists(f"{srt_path_base}.srt"): os.remove(f"{srt_path_base}.srt")
            return jsonify({"status": "success", "download_url": f"/processed/subtitled_{unique_id}{ext}"})

def process_video_for_srt(input_video, output_audio, srt_base, model_name):
    base_dir = get_base_dir()
    model_path = os.path.join(base_dir, "..", "..", "models", model_name)
    app.logger.info(f"Attempting to generate video with model from: {model_path}")
    if not os.path.exists(model_path):
        app.logger.error(f"Model file not found for video generation: {model_name} at {model_path}")
        return f"Model file not found: {model_name}"

    main_executable_path = os.path.join(base_dir, "..", "..", "build", "bin", "Release", "main.exe")
    ffmpeg_executable_path = os.path.join(base_dir, "ffmpeg", "bin", "ffmpeg.exe")

    try:
        # 1. Extract audio
        extract_cmd = [ffmpeg_executable_path, '-i', input_video, '-vn', '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', output_audio]
        subprocess.run(extract_cmd, check=True, capture_output=True)

        # 2. Generate SRT
        srt_cmd = [main_executable_path, "-m", model_path, "-f", output_audio, "-osrt"]
        subprocess.run(srt_cmd, check=True, capture_output=True)

        # 3. Burn subtitles
        output_video = os.path.join(app.config['PROCESSED_FOLDER'], f"subtitled_{os.path.basename(input_video)}")
        burn_cmd = [ffmpeg_executable_path, '-i', input_video, '-vf', f"subtitles='{srt_base}.srt'", output_video]
        subprocess.run(burn_cmd, check=True, capture_output=True)

        return None # No error

    except subprocess.CalledProcessError as e:
        app.logger.error(f"Subprocess error during video generation: {e.stderr.decode('utf-8', errors='ignore')}")
        return e.stderr.decode('utf-8', errors='ignore')
    except FileNotFoundError as e:
        app.logger.error(f"Executable not found during video generation: {e.filename}")
        return f"Executable not found: {e.filename}"
    except Exception as e:
        app.logger.error(f"An unexpected error occurred during video generation: {e}")
        return str(e)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(app.config['PROCESSED_FOLDER']):
        os.makedirs(app.config['PROCESSED_FOLDER'])
    socketio.run(app, debug=True)