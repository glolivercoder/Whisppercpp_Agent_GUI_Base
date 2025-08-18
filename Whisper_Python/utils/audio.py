import os
import sys
import subprocess
import tempfile
import logging
import numpy as np
import soundfile as sf
from typing import Optional, Tuple, List, Dict, Union

# Adicionar o diretório pai ao path para importar config.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AudioProcessor:
    """Classe para processamento de arquivos de áudio"""
    
    def __init__(self):
        """Inicializa o processador de áudio"""
        pass
    
    @staticmethod
    def convert_audio(input_file: str, output_format: str = 'wav', 
                     sample_rate: int = 16000, channels: int = 1) -> str:
        """Converte um arquivo de áudio para o formato desejado
        
        Args:
            input_file: Caminho para o arquivo de áudio de entrada
            output_format: Formato de saída (wav, mp3, etc.)
            sample_rate: Taxa de amostragem em Hz
            channels: Número de canais (1 para mono, 2 para estéreo)
            
        Returns:
            str: Caminho para o arquivo convertido
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Arquivo de áudio não encontrado: {input_file}")
        
        # Criar arquivo temporário para saída
        output_file = tempfile.NamedTemporaryFile(
            suffix=f".{output_format}", 
            delete=False
        ).name
        
        # Comando ffmpeg para conversão
        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-ar', str(sample_rate),
            '-ac', str(channels),
            '-y',  # Sobrescrever arquivo se existir
            output_file
        ]
        
        try:
            # Executar ffmpeg
            subprocess.run(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                check=True
            )
            
            logger.info(f"Arquivo convertido com sucesso: {output_file}")
            return output_file
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao converter áudio: {e.stderr}")
            raise RuntimeError(f"Erro ao converter áudio: {e.stderr}")
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            raise
    
    @staticmethod
    def normalize_audio(audio_data: np.ndarray, target_level: float = -23.0) -> np.ndarray:
        """Normaliza o áudio para um nível alvo (LUFS)
        
        Args:
            audio_data: Array NumPy com dados de áudio
            target_level: Nível alvo em LUFS
            
        Returns:
            np.ndarray: Áudio normalizado
        """
        # Calcular RMS
        rms = np.sqrt(np.mean(audio_data**2))
        
        # Converter para dB
        current_level = 20 * np.log10(rms) if rms > 0 else -100.0
        
        # Calcular ganho necessário
        gain = 10**((target_level - current_level) / 20)
        
        # Aplicar ganho
        normalized_audio = audio_data * gain
        
        # Limitar para evitar clipping
        if np.max(np.abs(normalized_audio)) > 1.0:
            normalized_audio = normalized_audio / np.max(np.abs(normalized_audio))
        
        return normalized_audio
    
    @staticmethod
    def split_audio(audio_file: str, segment_duration: float = 30.0) -> List[str]:
        """Divide um arquivo de áudio em segmentos menores
        
        Args:
            audio_file: Caminho para o arquivo de áudio
            segment_duration: Duração de cada segmento em segundos
            
        Returns:
            List[str]: Lista de caminhos para os segmentos
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Arquivo de áudio não encontrado: {audio_file}")
        
        # Carregar áudio
        audio_data, sample_rate = sf.read(audio_file)
        
        # Calcular número de amostras por segmento
        samples_per_segment = int(segment_duration * sample_rate)
        
        # Calcular número de segmentos
        num_segments = int(np.ceil(len(audio_data) / samples_per_segment))
        
        segment_files = []
        
        for i in range(num_segments):
            # Extrair segmento
            start_idx = i * samples_per_segment
            end_idx = min(start_idx + samples_per_segment, len(audio_data))
            segment = audio_data[start_idx:end_idx]
            
            # Criar arquivo temporário para o segmento
            segment_file = tempfile.NamedTemporaryFile(
                suffix=".wav", 
                delete=False
            ).name
            
            # Salvar segmento
            sf.write(segment_file, segment, sample_rate)
            
            segment_files.append(segment_file)
        
        logger.info(f"Áudio dividido em {len(segment_files)} segmentos")
        return segment_files
    
    @staticmethod
    def get_audio_info(audio_file: str) -> Dict[str, Union[int, float, str]]:
        """Obtém informações sobre um arquivo de áudio
        
        Args:
            audio_file: Caminho para o arquivo de áudio
            
        Returns:
            Dict: Informações sobre o arquivo de áudio
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Arquivo de áudio não encontrado: {audio_file}")
        
        try:
            # Carregar áudio
            audio_data, sample_rate = sf.read(audio_file)
            
            # Calcular duração
            duration = len(audio_data) / sample_rate
            
            # Obter número de canais
            channels = 1 if len(audio_data.shape) == 1 else audio_data.shape[1]
            
            # Calcular nível RMS
            rms = np.sqrt(np.mean(audio_data**2))
            level_db = 20 * np.log10(rms) if rms > 0 else -100.0
            
            return {
                'sample_rate': sample_rate,
                'channels': channels,
                'duration': duration,
                'samples': len(audio_data),
                'level_db': level_db,
                'format': os.path.splitext(audio_file)[1][1:],
                'file_size': os.path.getsize(audio_file)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do áudio: {e}")
            raise
    
    @staticmethod
    def record_audio(output_file: str, duration: float = 5.0, 
                    sample_rate: int = 16000, channels: int = 1) -> str:
        """Grava áudio do microfone
        
        Args:
            output_file: Caminho para o arquivo de saída
            duration: Duração da gravação em segundos
            sample_rate: Taxa de amostragem em Hz
            channels: Número de canais
            
        Returns:
            str: Caminho para o arquivo gravado
        """
        # Comando ffmpeg para gravação
        cmd = [
            'ffmpeg',
            '-f', 'avfoundation' if sys.platform == 'darwin' else 'dshow',
            '-i', ':0' if sys.platform == 'darwin' else 'audio=Microphone',
            '-t', str(duration),
            '-ar', str(sample_rate),
            '-ac', str(channels),
            '-y',  # Sobrescrever arquivo se existir
            output_file
        ]
        
        try:
            # Executar ffmpeg
            subprocess.run(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                check=True
            )
            
            logger.info(f"Áudio gravado com sucesso: {output_file}")
            return output_file
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao gravar áudio: {e.stderr}")
            raise RuntimeError(f"Erro ao gravar áudio: {e.stderr}")
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            raise

# Função para criar uma instância do processador de áudio
def get_audio_processor() -> AudioProcessor:
    """Cria e retorna uma instância do AudioProcessor
    
    Returns:
        AudioProcessor: Instância do processador de áudio
    """
    return AudioProcessor()

# Exemplo de uso
if __name__ == '__main__':
    # Criar processador de áudio
    processor = get_audio_processor()
    
    # Exemplo de arquivo de áudio
    audio_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    if audio_file and os.path.exists(audio_file):
        # Obter informações do áudio
        info = processor.get_audio_info(audio_file)
        print("Informações do áudio:")
        for key, value in info.items():
            print(f"  - {key}: {value}")
        
        # Converter para WAV
        wav_file = processor.convert_audio(audio_file)
        print(f"Arquivo convertido: {wav_file}")
        
        # Dividir em segmentos
        segments = processor.split_audio(wav_file, segment_duration=10.0)
        print(f"Segmentos: {len(segments)}")
        for i, segment in enumerate(segments):
            print(f"  - Segmento {i+1}: {segment}")
    else:
        print("Uso: python audio.py <arquivo_de_audio>")