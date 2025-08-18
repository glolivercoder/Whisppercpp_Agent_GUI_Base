import os
import json
import time
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import subprocess
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuração da aplicação Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'whisper-secret-key')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['TRANSCRIPTION_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'transcriptions')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['ALLOWED_EXTENSIONS'] = {'wav', 'mp3', 'ogg', 'flac', 'm4a'}

# Verificar se estamos em modo de demonstração
try:
    from run import demo_mode
    app.config['DEMO_MODE'] = demo_mode
except ImportError:
    app.config['DEMO_MODE'] = False

# Caminho para o executável whisper.cpp e modelos
WHISPER_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WHISPER_EXECUTABLE = os.path.join(WHISPER_BASE_DIR, 'main')
MODELS_DIR = os.path.join(WHISPER_BASE_DIR, 'models')

# Criar diretórios necessários se não existirem
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TRANSCRIPTION_FOLDER'], exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# Função para verificar extensões permitidas
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Função para listar modelos disponíveis
def get_available_models():
    models = []
    if os.path.exists(MODELS_DIR):
        for file in os.listdir(MODELS_DIR):
            if file.endswith('.bin'):
                models.append(file)
    return models

# Função para transcrever áudio usando whisper.cpp
def transcribe_audio(audio_path, model_name='base', language=None):
    # Verificar se o arquivo de áudio existe
    if not os.path.exists(audio_path):
        logger.error(f"Arquivo de áudio não encontrado: {audio_path}")
        return {"error": "Arquivo de áudio não encontrado"}
    
    # Gerar ID de transcrição
    transcription_id = str(uuid.uuid4())
    
    # Verificar se estamos em modo de demonstração
    if app.config.get('DEMO_MODE', False) or not os.path.exists(WHISPER_EXECUTABLE):
        logger.info("Executando em modo de demonstração - simulando transcrição")
        
        # Criar uma transcrição simulada
        demo_text = f"[Modo de demonstração] Transcrição simulada para {os.path.basename(audio_path)}\n"
        demo_text += "Este é um texto de exemplo gerado porque o executável whisper.cpp não foi encontrado.\n"
        demo_text += "Para usar a funcionalidade completa, compile o whisper.cpp e configure o caminho correto em config.py.\n"
        
        if language:
            demo_text += f"Idioma selecionado: {language}\n"
        
        # Salvar transcrição simulada
        transcription_path = os.path.join(app.config['TRANSCRIPTION_FOLDER'], f"{transcription_id}.txt")
        with open(transcription_path, 'w', encoding='utf-8') as f:
            f.write(demo_text)
        
        return {
            "id": transcription_id,
            "text": demo_text,
            "file": os.path.basename(audio_path),
            "model": model_name,
            "language": language or "auto",
            "timestamp": time.time(),
            "demo": True
        }
    
    # Modo normal - usar whisper.cpp
    model_path = os.path.join(MODELS_DIR, model_name)
    
    # Verificar se o modelo existe
    if not os.path.exists(model_path):
        logger.error(f"Modelo não encontrado: {model_path}")
        return {"error": "Modelo não encontrado"}
    
    # Preparar comando para whisper.cpp
    cmd = [WHISPER_EXECUTABLE, '-m', model_path, '-f', audio_path]
    
    # Adicionar opção de idioma se especificado
    if language:
        cmd.extend(['-l', language])
    
    logger.info(f"Executando comando: {' '.join(cmd)}")
    
    try:
        # Executar whisper.cpp
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Salvar transcrição
        transcription_path = os.path.join(app.config['TRANSCRIPTION_FOLDER'], f"{transcription_id}.txt")
        
        with open(transcription_path, 'w', encoding='utf-8') as f:
            f.write(result.stdout)
        
        return {
            "id": transcription_id,
            "text": result.stdout,
            "file": os.path.basename(audio_path),
            "model": model_name,
            "language": language or "auto",
            "timestamp": time.time(),
            "demo": False
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao executar whisper.cpp: {e}")
        logger.error(f"Saída de erro: {e.stderr}")
        return {"error": "Erro ao processar áudio", "details": e.stderr}
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        return {"error": "Erro inesperado", "details": str(e)}

# Rotas da aplicação
@app.route('/')
def index():
    models = get_available_models()
    demo_mode = app.config.get('DEMO_MODE', False) or not os.path.exists(WHISPER_EXECUTABLE)
    return render_template('index.html', models=models, demo_mode=demo_mode)

@app.route('/about')
def about():
    # Carregar informações do MEMO.json
    memo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'MEMO.json')
    memo_data = {}
    
    if os.path.exists(memo_path):
        try:
            with open(memo_path, 'r', encoding='utf-8') as f:
                memo_data = json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar MEMO.json: {e}")
    
    return render_template('about.html', memo=memo_data)

@app.route('/status')
def status():
    # Verificar status do sistema
    whisper_executable_exists = os.path.exists(WHISPER_EXECUTABLE)
    models = get_available_models()
    
    return jsonify({
        "status": "online",
        "whisper_executable": whisper_executable_exists,
        "models_available": models,
        "upload_folder": os.path.exists(app.config['UPLOAD_FOLDER']),
        "transcription_folder": os.path.exists(app.config['TRANSCRIPTION_FOLDER'])
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    # Verificar se há arquivo na requisição
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    
    file = request.files['file']
    
    # Verificar se o arquivo tem nome
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400
    
    # Verificar se o arquivo tem extensão permitida
    if not allowed_file(file.filename):
        return jsonify({"error": "Formato de arquivo não suportado"}), 400
    
    # Salvar arquivo
    filename = secure_filename(file.filename)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
    
    file.save(file_path)
    
    return jsonify({
        "message": "Arquivo enviado com sucesso",
        "file_id": file_id,
        "filename": filename,
        "path": file_path
    })

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.json
    
    # Verificar dados necessários
    if not data or 'file_path' not in data:
        return jsonify({"error": "Caminho do arquivo não fornecido"}), 400
    
    file_path = data['file_path']
    model = data.get('model', 'base')
    language = data.get('language', None)
    
    # Transcrever áudio
    result = transcribe_audio(file_path, model, language)
    
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify(result)

@app.route('/transcriptions/<transcription_id>')
def get_transcription(transcription_id):
    transcription_path = os.path.join(app.config['TRANSCRIPTION_FOLDER'], f"{transcription_id}.txt")
    
    if not os.path.exists(transcription_path):
        return jsonify({"error": "Transcrição não encontrada"}), 404
    
    return send_from_directory(app.config['TRANSCRIPTION_FOLDER'], f"{transcription_id}.txt")

@app.route('/models')
def list_models():
    models = get_available_models()
    return jsonify({"models": models})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)