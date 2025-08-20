# Development Checklist: Real-time Karaoke Application

This file tracks the development of the new features for the real-time karaoke application.

## Core Tasks

- [x] **Create a tabbed interface:** Redesign the main page to support three distinct tabs.
- [x] **Implement Tab 1: Real-time STT (Streaming):**
    - [x] Add UI elements (Start/Stop buttons, text display area).
    - [x] Implement backend logic for real-time audio capture.
    - [x] Use websockets to stream audio to the server and send text back to the client.
    - [x] Integrate with the `whisper` streaming executable.
- [x] **Implement Tab 2: Audio Transcription:**
    - [x] Add a slider for selecting a duration (3-50 seconds).
    - [x] Add a file input for the audio file.
    - [x] Implement backend logic to process the audio file.
- [x] **Implement Tab 3: Video with SRT Generation:**
    - [x] Add a file input for the video file.
    - [x] Implement backend logic to extract audio from the video (using ffmpeg).
    - [x] Run the extracted audio through `whisper` to generate an SRT file.
    - [x] Use `ffmpeg` to burn the SRT subtitles into the original video.
    - [x] Provide a download link for the final video.

## Backend (app.py)

- [x] Add new Flask routes for each tab's functionality.
- [x] Refactor existing code to fit the new tabbed structure.
- [x] Manage dependencies in `requirements.txt`.

## Frontend (HTML/CSS/JS)

- [x] Create the HTML structure for the tabs.
- [x] Style the new interface to match the existing application.
- [x] Write JavaScript to handle tab switching and interactions with the backend (e.g., AJAX calls, websocket communication).