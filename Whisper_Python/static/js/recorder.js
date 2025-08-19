// Whisper.cpp Web App - Recorder JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const recordButton = document.getElementById('recordButton');
    const pauseButton = document.getElementById('pauseButton');
    const stopButton = document.getElementById('stopButton');
    const recordingStatus = document.getElementById('recordingStatus');
    const recordingTime = document.getElementById('recordingTime');
    const audioPreview = document.getElementById('audioPreview');
    const audioPreviewContainer = document.getElementById('audioPreviewContainer');

    let mediaRecorder;
    let chunks = [];
    let timerInterval;
    let seconds = 0;

    // Event Listeners
    if (recordButton) {
        recordButton.addEventListener('click', toggleRecording);
    }

    if (pauseButton) {
        pauseButton.addEventListener('click', togglePause);
    }

    if (stopButton) {
        stopButton.addEventListener('click', stopRecording);
    }

    // Functions
    function toggleRecording() {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            stopRecording();
        } else {
            startRecording();
        }
    }

    function togglePause() {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.pause();
            pauseButton.innerHTML = '<i class="fas fa-play me-1"></i> Retomar';
            recordingStatus.classList.add('paused');
        } else if (mediaRecorder && mediaRecorder.state === 'paused') {
            mediaRecorder.resume();
            pauseButton.innerHTML = '<i class="fas fa-pause me-1"></i> Pausar';
            recordingStatus.classList.remove('paused');
        }
    }

    function startRecording() {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();

                mediaRecorder.ondataavailable = function(e) {
                    chunks.push(e.data);
                }

                mediaRecorder.onstop = function() {
                    const blob = new Blob(chunks, { 'type' : 'audio/wav' });
                    chunks = [];
                    const audioURL = window.URL.createObjectURL(blob);

                    if (audioPreview) {
                        audioPreview.src = audioURL;
                    }
                    if (audioPreviewContainer) {
                        audioPreviewContainer.classList.remove('d-none');
                    }

                    // Pass the audio blob to main.js
                    if (window.mainApp && typeof window.mainApp.setAudioBlob === 'function') {
                        window.mainApp.setAudioBlob(blob, audioURL);
                    }

                    // UI updates
                    recordButton.innerHTML = '<i class="fas fa-microphone me-1"></i> Iniciar Gravação';
                    recordButton.disabled = false;
                    stopButton.disabled = true;
                    pauseButton.disabled = true;
                    if (recordingStatus) recordingStatus.classList.add('d-none');
                    stopTimer();
                }

                // UI updates
                recordButton.innerHTML = '<i class="fas fa-stop me-1"></i> Parar Gravação';
                stopButton.disabled = false;
                pauseButton.disabled = false;
                if (recordingStatus) recordingStatus.classList.remove('d-none');
                startTimer();

            })
            .catch(err => {
                console.error('Error getting user media:', err);
                alert('Erro ao acessar o microfone. Por favor, verifique as permissões do seu navegador.');
            });
    }

    function stopRecording() {
        if (mediaRecorder) {
            mediaRecorder.stop();
        }
    }

    function startTimer() {
        seconds = 0;
        timerInterval = setInterval(() => {
            seconds++;
            if (recordingTime) {
                const minutes = Math.floor(seconds / 60);
                const remainingSeconds = seconds % 60;
                recordingTime.textContent = `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
            }
        }, 1000);
    }

    function stopTimer() {
        clearInterval(timerInterval);
        if (recordingTime) {
            recordingTime.textContent = '00:00';
        }
    }
});
