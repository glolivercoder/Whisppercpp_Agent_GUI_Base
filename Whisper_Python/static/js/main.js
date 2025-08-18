// Whisper.cpp Web App - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const transcribeButton = document.getElementById('transcribeButton');
    const modelSelect = document.getElementById('modelSelect');
    const languageSelect = document.getElementById('languageSelect');
    const translateCheckbox = document.getElementById('translateCheck');
    const wordTimestampsCheckbox = document.getElementById('wordTimestampsCheck');
    const resultContainer = document.getElementById('transcriptionResult');
    const alertContainer = document.getElementById('alertContainer');
    const copyButton = document.getElementById('copyButton');
    const downloadButton = document.getElementById('downloadButton');
    const progressBar = document.querySelector('#transcriptionProgress .progress-bar');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileNameSpan = document.getElementById('fileName');
    const fileSizeSpan = document.getElementById('fileSize');
    const fileTypeSpan = document.getElementById('fileType');
    const uploadPreview = document.getElementById('uploadPreview');
    const uploadPreviewContainer = document.getElementById('uploadPreviewContainer');
    const dropArea = document.getElementById('dropArea');
    const browseButton = document.getElementById('browseButton');
    
    // Audio Recording Variables (from recorder.js)
    let audioBlob;
    let audioUrl;
    let recordedFilename;
    let uploadedFileId; // To store the ID of uploaded files
    
    // Event Listeners
    if (transcribeButton) {
        transcribeButton.addEventListener('click', transcribeAudio);
    }
    
    if (copyButton) {
        copyButton.addEventListener('click', copyTranscription);
    }
    
    if (downloadButton) {
        downloadButton.addEventListener('click', downloadTranscription);
    }
    
    // File upload event listeners
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
    
    if (browseButton) {
        browseButton.addEventListener('click', () => fileInput.click());
    }
    
    if (dropArea) {
        // Drag and drop functionality
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });
        
        dropArea.addEventListener('drop', handleDrop, false);
        dropArea.addEventListener('click', () => fileInput.click());
    }
    
    // Initialize WaveSurfer for waveform visualization if available
    let waveform;
    if (window.WaveSurfer && document.getElementById('waveform')) {
        waveform = WaveSurfer.create({
            container: '#waveform',
            waveColor: '#4a6fa5',
            progressColor: '#17a2b8',
            cursorColor: 'transparent',
            barWidth: 2,
            barRadius: 3,
            responsive: true,
            height: 100,
            normalize: true
        });
        
        waveform.on('ready', function() {
            document.getElementById('waveformContainer').style.display = 'block';
            transcribeButton.disabled = false;
        });
    }
    
    // Fetch available models
    fetchModels();
    
    // Functions
    
    // Handle file selection
    function handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            displayFileInfo(file);
            uploadFile(file);
        }
    }
    
    // Handle drag and drop
    function handleDrop(event) {
        const dt = event.dataTransfer;
        const file = dt.files[0];
        
        if (file) {
            fileInput.files = dt.files;
            displayFileInfo(file);
            uploadFile(file);
        }
    }
    
    // Prevent default drag and drop behavior
    function preventDefaults(event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    // Highlight drop area
    function highlight() {
        dropArea.classList.add('dragover');
    }
    
    // Remove highlight from drop area
    function unhighlight() {
        dropArea.classList.remove('dragover');
    }
    
    // Display file information
    function displayFileInfo(file) {
        if (fileInfo && fileNameSpan && fileSizeSpan && fileTypeSpan) {
            fileNameSpan.textContent = file.name;
            fileSizeSpan.textContent = formatFileSize(file.size);
            fileTypeSpan.textContent = file.type || 'N/A';
            fileInfo.classList.remove('d-none');
        }
        
        // Display audio preview if it's an audio file
        if (uploadPreview && uploadPreviewContainer) {
            if (file.type.startsWith('audio/')) {
                const url = URL.createObjectURL(file);
                uploadPreview.src = url;
                uploadPreviewContainer.classList.remove('d-none');
            } else {
                uploadPreviewContainer.classList.add('d-none');
            }
        }
    }
    
    // Format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Upload file to server
    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Show loading spinner or progress
        if (document.getElementById('transcriptionProgress')) {
            document.getElementById('transcriptionProgress').classList.remove('d-none');
        }
        
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.file_id && data.filename) {
                // Store the uploaded file ID
                uploadedFileId = data.file_id + '_' + data.filename;
                
                // Pass filename to main app
                if (window.mainApp) {
                    window.mainApp.setRecordedFilename(uploadedFileId);
                    window.mainApp.enableTranscribeButton();
                }
                
                showAlert('Arquivo carregado com sucesso!', 'success');
            } else {
                showAlert(`Erro ao carregar arquivo: ${data.error || 'Erro desconhecido'}`, 'danger');
            }
        })
        .catch(error => {
            console.error('Error uploading file:', error);
            showAlert('Erro ao enviar o arquivo. Tente novamente.', 'danger');
        })
        .finally(() => {
            // Hide progress bar
            if (document.getElementById('transcriptionProgress')) {
                document.getElementById('transcriptionProgress').classList.add('d-none');
            }
        });
    }
    
    // Handle file selection
    function handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            // Display file info
            if (fileInfo) {
                fileNameSpan.textContent = file.name;
                fileSizeSpan.textContent = formatFileSize(file.size);
                fileTypeSpan.textContent = file.type || 'N/A';
                fileInfo.classList.remove('d-none');
            }
            
            // Display audio preview
            if (uploadPreview) {
                const fileURL = URL.createObjectURL(file);
                uploadPreview.src = fileURL;
            }
            
            if (uploadPreviewContainer) {
                uploadPreviewContainer.classList.remove('d-none');
            }
            
            // Upload file to server
            uploadFile(file);
        }
    }
    
    // Handle drag and drop
    function handleDrop(event) {
        const dt = event.dataTransfer;
        const file = dt.files[0];
        
        if (file) {
            // Set file input value
            if (fileInput) {
                fileInput.files = dt.files;
            }
            
            // Handle file selection
            handleFileSelect({ target: { files: dt.files } });
        }
    }
    
    // Prevent default drag and drop behavior
    function preventDefaults(event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    // Highlight drop area
    function highlight() {
        if (dropArea) {
            dropArea.classList.add('dragover');
        }
    }
    
    // Remove highlight from drop area
    function unhighlight() {
        if (dropArea) {
            dropArea.classList.remove('dragover');
        }
    }
    
    // Upload file to server
    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Show loading state
        if (transcribeButton) {
            transcribeButton.disabled = true;
            transcribeButton.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Enviando...';
        }
        
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.file_id && data.filename) {
                // Store file info for transcription
                uploadedFileId = data.file_id;
                recordedFilename = data.filename;
                
                // Pass filename to recorder.js functions
                if (window.mainApp) {
                    window.mainApp.setRecordedFilename(`${data.file_id}_${data.filename}`);
                    window.mainApp.enableTranscribeButton();
                }
                
                showAlert('Arquivo carregado com sucesso!', 'success');
            } else {
                showAlert(`Erro ao carregar arquivo: ${data.error || 'Erro desconhecido'}`, 'danger');
            }
        })
        .catch(error => {
            console.error('Error uploading file:', error);
            showAlert('Erro ao enviar o arquivo. Tente novamente.', 'danger');
        })
        .finally(() => {
            // Restore button state
            if (transcribeButton) {
                transcribeButton.innerHTML = '<i class="fas fa-play me-1"></i> Iniciar Transcrição';
                transcribeButton.disabled = false;
            }
        });
    }
    
    // Format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Transcribe audio
    function transcribeAudio() {
        // Get selected options
        const model = modelSelect ? modelSelect.value : 'base';
        const language = languageSelect ? languageSelect.value : 'auto';
        const translate = translateCheckbox ? translateCheckbox.checked : false;
        const wordTimestamps = wordTimestampsCheckbox ? wordTimestampsCheckbox.checked : false;
        
        // Get audio source (recorded or uploaded)
        let audioSource;
        let isRecordedAudio = false;
        
        if (audioBlob) {
            // Use recorded audio
            audioSource = audioBlob;
            isRecordedAudio = true;
        } else if (recordedFilename) {
            // Use uploaded audio filename
            audioSource = recordedFilename;
        } else {
            showAlert('Nenhum áudio disponível para transcrição.', 'warning');
            return;
        }
        
        // Show progress bar
        if (document.getElementById('transcriptionProgress')) {
            document.getElementById('transcriptionProgress').classList.remove('d-none');
        }
        
        // Disable transcribe button
        if (transcribeButton) {
            transcribeButton.disabled = true;
        }
        
        // Clear previous results
        if (resultContainer) {
            resultContainer.innerHTML = '';
            resultContainer.style.display = 'none';
        }
        
        // Reset copy and download buttons
        if (copyButton) {
            copyButton.disabled = true;
        }
        if (downloadButton) {
            downloadButton.disabled = true;
        }
        
        // Handle recorded audio (upload it first)
        if (isRecordedAudio) {
            const formData = new FormData();
            formData.append('file', audioBlob, 'recorded_audio.wav');
            
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(uploadData => {
                if (uploadData.file_id && uploadData.filename) {
                    // Now transcribe the uploaded file
                    transcribeFile(uploadData.file_id + '_' + uploadData.filename, model, language, translate, wordTimestamps);
                } else {
                    throw new Error(uploadData.error || 'Erro ao carregar arquivo gravado');
                }
            })
            .catch(error => {
                console.error('Error uploading recorded audio:', error);
                showAlert('Erro ao enviar o áudio gravado: ' + error.message, 'danger');
                resetTranscriptionUI();
            });
        } else {
            // Transcribe uploaded file directly
            transcribeFile(audioSource, model, language, translate, wordTimestamps);
        }
    }
    
    // Transcribe a file
    function transcribeFile(filename, model, language, translate, wordTimestamps) {
        // Update progress bar
        if (progressBar) {
            progressBar.style.width = '30%';
            progressBar.textContent = '30%';
        }
        
        // Prepare JSON data
        const data = {
            filename: filename,
            model: model,
            language: language,
            translate: translate,
            word_timestamps: wordTimestamps
        };
        
        // Send transcription request
        fetch('/transcribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            // Update progress bar
            if (progressBar) {
                progressBar.style.width = '60%';
                progressBar.textContent = '60%';
            }
            
            return response.json();
        })
        .then(data => {
            // Update progress bar
            if (progressBar) {
                progressBar.style.width = '100%';
                progressBar.textContent = '100%';
            }
            
            if (data.success) {
                displayTranscription(data.transcription, data.transcription_id, wordTimestamps);
                
                // Enable copy and download buttons
                if (copyButton) {
                    copyButton.disabled = false;
                }
                if (downloadButton) {
                    downloadButton.disabled = false;
                }
                
                showAlert('Transcrição concluída com sucesso!', 'success');
            } else {
                showAlert(`Erro na transcrição: ${data.error}`, 'danger');
            }
        })
        .catch(error => {
            console.error('Error transcribing audio:', error);
            showAlert('Erro ao transcrever o áudio. Tente novamente.', 'danger');
        })
        .finally(() => {
            resetTranscriptionUI();
        });
    }
    
    // Reset transcription UI after completion or error
    function resetTranscriptionUI() {
        // Hide progress bar after a delay
        setTimeout(() => {
            if (document.getElementById('transcriptionProgress')) {
                document.getElementById('transcriptionProgress').classList.add('d-none');
            }
            
            // Reset progress bar
            if (progressBar) {
                progressBar.style.width = '0%';
                progressBar.textContent = '0%';
            }
            
            // Re-enable transcribe button
            if (transcribeButton) {
                transcribeButton.disabled = false;
            }
        }, 2000);
    }
    
    // Display transcription results
    function displayTranscription(transcription, transcriptionId, withWordTimestamps) {
        if (resultContainer) {
            resultContainer.style.display = 'block';
            
            // For now, we'll display the transcription as plain text
            // In the future, we can implement word-level or segment-level timestamps
            resultContainer.classList.remove('with-timestamps');
            resultContainer.textContent = typeof transcription === 'object' ? JSON.stringify(transcription, null, 2) : transcription;
            
            // Store transcription ID for later reference
            if (transcriptionId) {
                resultContainer.setAttribute('data-transcription-id', transcriptionId);
            }
        }
    }
    
    // Copy transcription to clipboard
    function copyTranscription() {
        if (resultContainer) {
            const text = resultContainer.textContent || resultContainer.innerText;
            navigator.clipboard.writeText(text)
                .then(() => {
                    showAlert('Transcrição copiada para a área de transferência!', 'success');
                })
                .catch(err => {
                    console.error('Failed to copy transcription: ', err);
                    showAlert('Falha ao copiar a transcrição. Tente novamente.', 'danger');
                });
        }
    }
    
    // Download transcription as text file
    function downloadTranscription() {
        if (resultContainer) {
            const text = resultContainer.textContent || resultContainer.innerText;
            const blob = new Blob([text], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = 'transcription.txt';
            document.body.appendChild(a);
            a.click();
            
            // Clean up
            setTimeout(() => {
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }, 100);
        }
    }
    
    // Format timestamp (seconds to MM:SS.ms)
    function formatTimestamp(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        const milliseconds = Math.floor((seconds % 1) * 1000);
        
        return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(3, '0')}`;
    }
    
    // Fetch available models
    function fetchModels() {
        if (modelSelect) {
            fetch('/models')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.models) {
                    // Clear existing options
                    modelSelect.innerHTML = '';
                    
                    // Add each model as an option
                    data.models.forEach(model => {
                        const option = document.createElement('option');
                        option.value = model.name;
                        option.textContent = `${model.name} (${model.size})`;
                        modelSelect.appendChild(option);
                    });
                }
            })
            .catch(error => {
                console.error('Error fetching models:', error);
            });
        }
    }
    
    // Show alert message
    function showAlert(message, type = 'info') {
        if (alertContainer) {
            // Remove any existing alerts
            alertContainer.innerHTML = '';
            
            // Create alert element
            const alertElement = document.createElement('div');
            alertElement.className = `alert alert-${type} alert-dismissible fade show`;
            alertElement.role = 'alert';
            
            // Add message
            alertElement.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            
            // Add to container
            alertContainer.appendChild(alertElement);
            
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                if (alertElement.parentNode) {
                    const bsAlert = new bootstrap.Alert(alertElement);
                    bsAlert.close();
                }
            }, 5000);
        }
    }
    
    // Expose functions to global scope for recorder.js to use
    window.mainApp = {
        setAudioBlob: function(blob, url) {
            audioBlob = blob;
            audioUrl = url;
            recordedFilename = null;
            
            // Load waveform if available
            if (waveform) {
                waveform.load(audioUrl);
            }
        },
        
        setRecordedFilename: function(filename) {
            recordedFilename = filename;
            audioBlob = null;
            audioUrl = null;
            
            // Load waveform if available
            if (waveform) {
                waveform.load(`/uploads/${filename}`);
            }
        },
        
        enableTranscribeButton: function() {
            if (transcribeButton) {
                transcribeButton.disabled = false;
            }
        }
    };
});