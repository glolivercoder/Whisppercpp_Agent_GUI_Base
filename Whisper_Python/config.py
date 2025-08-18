import os

# Diretório base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Diretório base do whisper.cpp
WHISPER_BASE_DIR = os.path.dirname(BASE_DIR)

# Configurações de caminhos
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
TRANSCRIPTION_FOLDER = os.path.join(BASE_DIR, 'transcriptions')
MODELS_DIR = os.path.join(WHISPER_BASE_DIR, 'models')

# Caminho para o executável whisper.cpp
WHISPER_EXECUTABLE = os.path.join(WHISPER_BASE_DIR, 'build', 'bin', 'Release', 'whisper-cli.exe')

# Configurações de upload
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'flac', 'm4a'}

# Configurações de modelos
DEFAULT_MODEL = 'base'
AVAILABLE_MODELS = {
    'tiny': {
        'file': 'ggml-tiny.bin',
        'size': '75 MB',
        'memory': '~390 MB',
        'description': 'Mais rápido, menos preciso'
    },
    'base': {
        'file': 'ggml-base.bin',
        'size': '142 MB',
        'memory': '~500 MB',
        'description': 'Bom equilíbrio entre velocidade e precisão'
    },
    'small': {
        'file': 'ggml-small.bin',
        'size': '466 MB',
        'memory': '~1.0 GB',
        'description': 'Mais preciso, velocidade moderada'
    },
    'medium': {
        'file': 'ggml-medium.bin',
        'size': '1.5 GB',
        'memory': '~2.6 GB',
        'description': 'Alta precisão, mais lento'
    },
    'large': {
        'file': 'ggml-large.bin',
        'size': '3.0 GB',
        'memory': '~4.7 GB',
        'description': 'Máxima precisão, mais lento'
    }
}

# Configurações de idiomas suportados
SUPPORTED_LANGUAGES = {
    'auto': 'Detecção automática',
    'en': 'Inglês',
    'pt': 'Português',
    'es': 'Espanhol',
    'fr': 'Francês',
    'de': 'Alemão',
    'it': 'Italiano',
    'ja': 'Japonês',
    'zh': 'Chinês',
    'ru': 'Russo',
    'nl': 'Holandês',
    'uk': 'Ucraniano',
    'ar': 'Árabe',
    'hi': 'Hindi',
    'ko': 'Coreano'
}

# Configurações de transcrição
TRANSCRIPTION_OPTIONS = {
    'translate': False,  # Traduzir para inglês
    'no_timestamps': False,  # Remover timestamps
    'max_len': 0,  # Comprimento máximo do segmento (0 = sem limite)
    'word_timestamps': False,  # Timestamps por palavra
    'highlight_words': False,  # Destacar palavras durante a reprodução
    'max_context': -1,  # Contexto máximo (-1 = padrão)
    'single_segment': False,  # Processar como um único segmento
    'print_special': False,  # Imprimir tokens especiais
    'print_progress': True,  # Mostrar progresso
    'print_realtime': False,  # Imprimir em tempo real
    'print_timestamps': True,  # Imprimir timestamps
    'token_timestamps': False,  # Timestamps por token
    'diarize': False,  # Diarização (identificação de falantes)
    'speed_up': False,  # Acelerar áudio (2x)
    'audio_ctx': 0  # Contexto de áudio (0 = padrão)
}

# Configurações da aplicação Flask
FLASK_CONFIG = {
    'SECRET_KEY': os.environ.get('SECRET_KEY', 'whisper-secret-key'),
    'DEBUG': True,
    'HOST': '0.0.0.0',
    'PORT': 5000
}