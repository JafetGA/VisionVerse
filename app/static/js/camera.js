document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video');
    const startButton = document.getElementById('startCamera');
    const stopButton = document.getElementById('stopCamera');
    let stream = null;
    let mediaRecorder = null;
    let chunks = [];
    let frameInterval = null;

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

            frameInterval = setInterval(() => {
                if (stream) {
                    sendFrame();
                }
            }, 500);
            
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
        if (frameInterval) {
            clearInterval(frameInterval);
            frameInterval = null;
        }
    }

    function sendFrame() {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        const frameData = canvas.toDataURL('image/png');

        fetch('/detect_hand', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ frame: frameData })
        })
        .then(response => response.json())
        .then(data => console.log('Server response:', data))
        .catch(error => console.error('Error sending frame:', error));
    }

    startButton.addEventListener('click', startCamera);
    stopButton.addEventListener('click', stopCamera);
    stopButton.disabled = true;
    

});