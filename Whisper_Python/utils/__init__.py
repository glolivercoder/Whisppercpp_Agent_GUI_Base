# Pacote utils para a aplicação Whisper_Python

from .whisper_wrapper import WhisperWrapper, get_whisper_wrapper
from .audio import AudioProcessor, get_audio_processor

__all__ = [
    'WhisperWrapper',
    'get_whisper_wrapper',
    'AudioProcessor',
    'get_audio_processor'
]