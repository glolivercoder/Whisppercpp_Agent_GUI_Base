// Whisper.cpp Web App - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const recordButton = document.getElementById('recordButton');
    const stopButton = document.getElementById('stopButton');
    const timerElement = document.getElementById('timer');
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    const transcribeButton = document.getElementById('transcribeButton');
    const modelSelect = document.getElementById('modelSelect');
    const languageSelect = document.getElementById('languageSelect');
    const translateCheckbox = document.getElementById('translateCheckbox');
    const wordTimestampsCheckbox = document.getElementById('wordTimestampsCheckbox');
    const resultContainer = document.getElementById('transcriptionResult');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const alertContainer = document.getElementById('alertContainer');
    
    // Audio Recording Variables
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let recordingTimer;
    let recordingSeconds = 0;
    let audioBlob;
    let audioUrl;
    let waveform;
    
    // Initialize WaveSurfer for waveform visualization if available
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
    
    // Event Listeners
    if (recordButton) {
        recordButton.addEventListener('click', toggleRecording);
    }
    
    if (stopButton) {
        stopButton.addEventListener('click', stopRecording);
    }
    
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleUpload);
    }
    
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
    
    if (uploadArea) {
        // Drag and drop functionality
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });
        
        uploadArea.addEventListener('drop', handleDrop, false);
        uploadArea.addEventListener('click', () => fileInput.click());
    }
    
    if (transcribeButton) {
        transcribeButton.addEventListener('click', transcribeAudio);
    }
    
    // Functions
    
    // Toggle recording state
    function toggleRecording() {
        if (!isRecording) {
            startRecording();
        } else {
            stopRecording();
        }
    }
    
    // Start audio recording
    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            mediaRecorder.addEventListener('dataavailable', event => {
                audioChunks.push(event.data);
            });
            
            mediaRecorder.addEventListener('stop', () => {
                audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                audioUrl = URL.createObjectURL(audioBlob);
                
                // Display waveform if WaveSurfer is available
                if (waveform) {
                    waveform.load(audioUrl);
                }
                
                // Enable transcribe button
                if (transcribeButton) {
                    transcribeButton.disabled = false;
                }
            });
            
            mediaRecorder.start();
            isRecording = true;
            recordingSeconds = 0;
            startTimer();
            
            // Update UI
            if (recordButton) {
                recordButton.classList.add('recording');
                recordButton.innerHTML = '<i class="fas fa-stop"></i>';
            }
            
            if (stopButton) {
                stopButton.disabled = false;
            }
            
        } catch (error) {
            console.error('Error accessing microphone:', error);
            showAlert('Erro ao acessar o microfone. Verifique as permissões do navegador.', 'danger');
        }
    }
    
    // Stop audio recording
    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            isRecording = false;
            stopTimer();
            
            // Update UI
            if (recordButton) {
                recordButton.classList.remove('recording');
                recordButton.innerHTML = '<i class="fas fa-microphone"></i>';
            }
            
            if (stopButton) {
                stopButton.disabled = true;
            }
            
            // Stop all tracks on the stream
            if (mediaRecorder.stream) {
                mediaRecorder.stream.getTracks().forEach(track => track.stop());
            }
        }
    }
    
    // Start recording timer
    function startTimer() {
        stopTimer(); // Clear any existing timer
        recordingTimer = setInterval(() => {
            recordingSeconds++;
            updateTimerDisplay();
        }, 1000);
        updateTimerDisplay();
    }
    
    // Stop recording timer
    function stopTimer() {
        if (recordingTimer) {
            clearInterval(recordingTimer);
            recordingTimer = null;
        }
    }
    
    // Update timer display
    function updateTimerDisplay() {
        if (timerElement) {
            const minutes = Math.floor(recordingSeconds / 60);
            const seconds = recordingSeconds % 60;
            timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
    }
    
    // Handle file upload form submission
    function handleUpload(event) {
        event.preventDefault();
        const formData = new FormData(uploadForm);
        
        // Show loading spinner
        if (loadingSpinner) {
            loadingSpinner.style.display = 'block';
        }
        
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Load the audio file for visualization
                if (waveform) {
                    waveform.load(`/uploads/${data.filename}`);
                }
                
                // Enable transcribe button
                if (transcribeButton) {
                    transcribeButton.disabled = false;
                    transcribeButton.setAttribute('data-filename', data.filename);
                }
                
                showAlert('Arquivo carregado com sucesso!', 'success');
            } else {
                showAlert(`Erro ao carregar arquivo: ${data.error}`, 'danger');
            }
        })
        .catch(error => {
            console.error('Error uploading file:', error);
            showAlert('Erro ao enviar o arquivo. Tente novamente.', 'danger');
        })
        .finally(() => {
            // Hide loading spinner
            if (loadingSpinner) {
                loadingSpinner.style.display = 'none';
            }
        });
    }
    
    // Handle file selection
    function handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('file', file);
            
            // Show loading spinner
            if (loadingSpinner) {
                loadingSpinner.style.display = 'block';
            }
            
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Load the audio file for visualization
                    if (waveform) {
                        waveform.load(`/uploads/${data.filename}`);
                    }
                    
                    // Enable transcribe button
                    if (transcribeButton) {
                        transcribeButton.disabled = false;
                        transcribeButton.setAttribute('data-filename', data.filename);
                    }
                    
                    showAlert('Arquivo carregado com sucesso!', 'success');
                } else {
                    showAlert(`Erro ao carregar arquivo: ${data.error}`, 'danger');
                }
            })
            .catch(error => {
                console.error('Error uploading file:', error);
                showAlert('Erro ao enviar o arquivo. Tente novamente.', 'danger');
            })
            .finally(() => {
                // Hide loading spinner
                if (loadingSpinner) {
                    loadingSpinner.style.display = 'none';
                }
            });
        }
    }
    
    // Handle drag and drop
    function handleDrop(event) {
        const dt = event.dataTransfer;
        const file = dt.files[0];
        
        if (file) {
            fileInput.files = dt.files;
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
        uploadArea.classList.add('dragover');
    }
    
    // Remove highlight from drop area
    function unhighlight() {
        uploadArea.classList.remove('dragover');
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
        } else if (transcribeButton.hasAttribute('data-filename')) {
            // Use uploaded audio filename
            audioSource = transcribeButton.getAttribute('data-filename');
        } else {
            showAlert('Nenhum áudio disponível para transcrição.', 'warning');
            return;
        }
        
        // Show loading spinner
        if (loadingSpinner) {
            loadingSpinner.style.display = 'block';
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
        
        // Prepare form data
        const formData = new FormData();
        
        if (isRecordedAudio) {
            formData.append('audio', audioBlob, 'recorded_audio.wav');
        } else {
            formData.append('filename', audioSource);
        }
        
        formData.append('model', model);
        formData.append('language', language);
        formData.append('translate', translate);
        formData.append('word_timestamps', wordTimestamps);
        
        // Send transcription request
        fetch('/transcribe', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayTranscription(data.transcription, data.transcription_id, wordTimestamps);
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
            // Hide loading spinner
            if (loadingSpinner) {
                loadingSpinner.style.display = 'none';
            }
            
            // Re-enable transcribe button
            if (transcribeButton) {
                transcribeButton.disabled = false;
            }
        });
    }
    
    // Display transcription results
    function displayTranscription(transcription, transcriptionId, withWordTimestamps) {
        if (resultContainer) {
            resultContainer.style.display = 'block';
            
            if (withWordTimestamps && typeof transcription === 'object' && transcription.words) {
                // Display with word-level timestamps
                resultContainer.classList.add('with-timestamps');
                
                // Clear previous content
                resultContainer.innerHTML = '';
                
                // Add each word with its timestamp
                transcription.words.forEach(word => {
                    const wordSpan = document.createElement('span');
                    wordSpan.className = 'word';
                    wordSpan.textContent = word.word + ' ';
                    
                    const timestampSpan = document.createElement('span');
                    timestampSpan.className = 'timestamp';
                    timestampSpan.textContent = formatTimestamp(word.start) + ' - ' + formatTimestamp(word.end);
                    
                    wordSpan.appendChild(timestampSpan);
                    resultContainer.appendChild(wordSpan);
                });
                
            } else if (typeof transcription === 'object' && transcription.segments) {
                // Display with segment-level timestamps
                resultContainer.classList.remove('with-timestamps');
                
                // Clear previous content
                resultContainer.innerHTML = '';
                
                // Add each segment with its timestamp
                transcription.segments.forEach(segment => {
                    const segmentDiv = document.createElement('div');
                    segmentDiv.className = 'segment';
                    
                    const timestampSpan = document.createElement('span');
                    timestampSpan.className = 'segment-timestamp';
                    timestampSpan.textContent = `[${formatTimestamp(segment.start)} - ${formatTimestamp(segment.end)}] `;
                    
                    const textSpan = document.createElement('span');
                    textSpan.className = 'segment-text';
                    textSpan.textContent = segment.text;
                    
                    segmentDiv.appendChild(timestampSpan);
                    segmentDiv.appendChild(textSpan);
                    resultContainer.appendChild(segmentDiv);
                });
                
            } else {
                // Display plain text transcription
                resultContainer.classList.remove('with-timestamps');
                resultContainer.textContent = transcription;
            }
            
            // Store transcription ID for later reference
            if (transcriptionId) {
                resultContainer.setAttribute('data-transcription-id', transcriptionId);
            }
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
});