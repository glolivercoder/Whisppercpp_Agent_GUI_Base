// Whisper.cpp Web App - Audio Recorder

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const recordButton = document.getElementById('recordButton');
    const pauseButton = document.getElementById('pauseButton');
    const stopButton = document.getElementById('stopButton');
    const recordingStatus = document.getElementById('recordingStatus');
    const recordingTime = document.getElementById('recordingTime');
    const audioPreviewContainer = document.getElementById('audioPreviewContainer');
    const audioPreview = document.getElementById('audioPreview');
    const alertContainer = document.getElementById('alertContainer');
    
    // Audio Recording Variables
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let isPaused = false;
    let recordingTimer;
    let recordingSeconds = 0;
    let audioBlob;
    let audioUrl;
    
    // Event Listeners
    if (recordButton) {
        recordButton.addEventListener('click', toggleRecording);
    }
    
    if (pauseButton) {
        pauseButton.addEventListener('click', togglePauseResume);
    }
    
    if (stopButton) {
        stopButton.addEventListener('click', stopRecording);
    }
    
    // Functions
    
    // Toggle recording state (start/pause/resume)
    function toggleRecording() {
        if (!isRecording) {
            startRecording();
        } else if (isPaused) {
            resumeRecording();
        } else {
            pauseRecording();
        }
    }
    
    // Toggle pause/resume state
    function togglePauseResume() {
        if (isPaused) {
            resumeRecording();
        } else {
            pauseRecording();
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
                
                // Pass audio blob to main app
                if (window.mainApp) {
                    window.mainApp.setAudioBlob(audioBlob, audioUrl);
                    window.mainApp.enableTranscribeButton();
                }
                
                // Display audio preview
                if (audioPreview) {
                    audioPreview.src = audioUrl;
                }
                
                if (audioPreviewContainer) {
                    audioPreviewContainer.classList.remove('d-none');
                }
                
                // Stop all tracks on the stream
                if (mediaRecorder.stream) {
                    mediaRecorder.stream.getTracks().forEach(track => track.stop());
                }
            });
            
            mediaRecorder.start();
            isRecording = true;
            isPaused = false;
            recordingSeconds = 0;
            startTimer();
            
            // Update UI
            updateRecordingUI();
            
        } catch (error) {
            console.error('Error accessing microphone:', error);
            showAlert('Erro ao acessar o microfone. Verifique as permissões do navegador.', 'danger');
        }
    }
    
    // Pause audio recording
    function pauseRecording() {
        if (mediaRecorder && isRecording && !isPaused) {
            mediaRecorder.pause();
            isPaused = true;
            stopTimer();
            
            // Update UI
            updateRecordingUI();
        }
    }
    
    // Resume audio recording
    function resumeRecording() {
        if (mediaRecorder && isRecording && isPaused) {
            mediaRecorder.resume();
            isPaused = false;
            startTimer();
            
            // Update UI
            updateRecordingUI();
        }
    }
    
    // Stop audio recording
    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            isRecording = false;
            isPaused = false;
            stopTimer();
            
            // Update UI
            updateRecordingUI();
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
        if (recordingTime) {
            const minutes = Math.floor(recordingSeconds / 60);
            const seconds = recordingSeconds % 60;
            recordingTime.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
    }
    
    // Update recording UI based on state
    function updateRecordingUI() {
        if (recordButton) {
            if (!isRecording) {
                // Not recording
                recordButton.innerHTML = '<i class="fas fa-microphone me-1"></i> Iniciar Gravação';
                recordButton.classList.remove('btn-secondary');
                recordButton.classList.add('btn-danger');
            } else if (isPaused) {
                // Paused
                recordButton.innerHTML = '<i class="fas fa-microphone me-1"></i> Retomar';
                recordButton.classList.remove('btn-secondary');
                recordButton.classList.add('btn-danger');
            } else {
                // Recording
                recordButton.innerHTML = '<i class="fas fa-pause me-1"></i> Pausar';
                recordButton.classList.remove('btn-danger');
                recordButton.classList.add('btn-secondary');
            }
        }
        
        if (pauseButton) {
            if (!isRecording) {
                // Not recording
                pauseButton.disabled = true;
            } else if (isPaused) {
                // Paused
                pauseButton.disabled = true;
            } else {
                // Recording
                pauseButton.disabled = false;
            }
        }
        
        if (stopButton) {
            if (!isRecording) {
                // Not recording
                stopButton.disabled = true;
            } else {
                // Recording or paused
                stopButton.disabled = false;
            }
        }
        
        if (recordingStatus) {
            if (isRecording && !isPaused) {
                // Recording
                recordingStatus.classList.remove('d-none');
            } else {
                // Not recording or paused
                recordingStatus.classList.add('d-none');
            }
        }
    }
    
    // Show alert message
    function showAlert(message, type = 'info') {
        // Create a temporary alert container if the main one doesn't exist
        let container = alertContainer;
        if (!container) {
            container = document.createElement('div');
            container.id = 'tempAlertContainer';
            document.body.appendChild(container);
        }
        
        // Remove any existing alerts
        container.innerHTML = '';
        
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
        container.appendChild(alertElement);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertElement.parentNode) {
                const bsAlert = new bootstrap.Alert(alertElement);
                bsAlert.close();
            }
        }, 5000);
    }
});