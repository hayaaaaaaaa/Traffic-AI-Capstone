const video = document.getElementById('v');
const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');

// Settings for speed
const WIDTH = 480;  // Good balance of quality/speed
const HEIGHT = 360;
const QUALITY = 0.5; // 50% JPEG quality (looks fine, uploads fast)

let isUploading = false; // The Traffic Cop

navigator.mediaDevices.getUserMedia({ 
    video: { 
        facingMode: 'environment',
        width: { ideal: 640 },
        height: { ideal: 480 }
    } 
})
.then(stream => {
    video.srcObject = stream;
    console.log("Stream started");
    // Run as fast as the browser allows
    requestAnimationFrame(sendFrame);
});

function sendFrame() {
    // 1. If video isn't ready or we are still uploading the last frame, SKIP.
    if (video.readyState !== video.HAVE_ENOUGH_DATA || isUploading) {
        requestAnimationFrame(sendFrame);
        return;
    }

    // 2. Lock the upload
    isUploading = true;

    // 3. Draw & Compress
    canvas.width = WIDTH;
    canvas.height = HEIGHT;
    ctx.drawImage(video, 0, 0, WIDTH, HEIGHT);

    canvas.toBlob(blob => {
        const formData = new FormData();
        formData.append('frame', blob);

        // 4. Upload
        fetch('/upload', { method: 'POST', body: formData })
        .then(() => {
            // Success! Unlock for next frame
            isUploading = false;
        })
        .catch(err => {
            console.log("Drop");
            isUploading = false;
        });

    }, 'image/jpeg', QUALITY);

    // 5. Schedule next check
    requestAnimationFrame(sendFrame);
}