document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video');
    const startButton = document.getElementById('startCamera');
    const stopButton = document.getElementById('stopCamera');
    let stream = null;
    let mediaRecorder = null;
    let chunks = [];

    async function startCamera() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                },
                audio: false
            });
            video.srcObject = stream;
            startButton.disabled = true;
            stopButton.disabled = false;

            // Start recording the video stream
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = (event) => {
                chunks.push(event.data);
            };
        } catch (err) {
            console.error('Error accessing camera:', err);
        }
    }

    function stopCamera() {
        if (stream) {
            mediaRecorder.stop();
            stream.getTracks().forEach(track => track.stop());
            video.srcObject = null;
            startButton.disabled = false;
            stopButton.disabled = true;
        }
    }

    startButton.addEventListener('click', startCamera);
    stopButton.addEventListener('click', stopCamera);
    stopButton.disabled = true;
});