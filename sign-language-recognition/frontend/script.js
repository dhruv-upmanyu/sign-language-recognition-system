// API Base URL - change for production
const API_BASE = 'https://sign-language-backend-uf7m.onrender.com';

// Sign meanings
const SIGN_MEANINGS = {
    'Coca-Cola': 'A popular carbonated soft drink brand.',
    'Happy': 'Feeling or showing pleasure or contentment.',
    'Sleep': 'A condition of body and mind which typically recurs for several hours every night.',
    'Thank You': 'An expression of gratitude or appreciation.',
    'Hello': 'Used as a greeting or to begin a phone conversation.'
};

let currentMode = null;
let mediaStream = null;
let video = document.getElementById('video');
let canvas = document.getElementById('canvas');
let ctx = canvas.getContext('2d');
let autoCaptureInterval = null;
let timerInterval = null;
let timeLeft = 3;

document.addEventListener('DOMContentLoaded', () => {
    // Mode selection
    document.querySelectorAll('.mode-card').forEach(card => {
        card.addEventListener('click', () => selectMode(card.dataset.mode));
    });
    
    document.getElementById('start-btn').addEventListener('click', startMode);
    document.getElementById('file-input').addEventListener('change', previewFile);
    document.getElementById('stop-btn').addEventListener('click', stopAutoCapture);
});

function selectMode(mode) {
    currentMode = mode;
    document.querySelectorAll('.mode-card').forEach(c => c.classList.remove('active'));
    event.target.classList.add('active');
    
    document.querySelector('.modes').style.display = 'none';
    document.getElementById('start-section').style.display = 'block';
    document.getElementById('start-btn').textContent = `START ${mode.toUpperCase()}`;
}

function startMode() {
    document.getElementById('start-section').style.display = 'none';
    document.getElementById('input-section').style.display = 'block';
    
    const preview = document.getElementById('media-preview');
    const fileInput = document.getElementById('file-input');
    
    if (currentMode === 'live') {
        fileInput.style.display = 'none';
        video.style.display = 'block';
        canvas.style.display = 'block';
        startCamera();
    } else {
        video.style.display = 'none';
        canvas.style.display = 'none';
        fileInput.accept = currentMode === 'image' ? 'image/*' : 'video/*';
        fileInput.style.display = 'block';
        preview.innerHTML = '<p>Select file to auto-predict</p>';
    }
}

async function startCamera() {
    try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = mediaStream;
        video.onloadedmetadata = () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            startAutoCapture();
        };
    } catch (err) {
        alert('Error accessing camera: ' + err.message);
    }
}

function startAutoCapture() {
    autoCaptureInterval = setInterval(() => {
        ctx.drawImage(video, 0, 0);
        const base64Image = canvas.toDataURL('image/jpeg', 0.8).split(',')[1];
        predictFrame(base64Image);
    }, 3000);
    
    timerInterval = setInterval(() => {
        timeLeft--;
        document.getElementById('timer').textContent = timeLeft;
        if (timeLeft <= 0) {
            timeLeft = 3;
        }
    }, 1000);
    
    document.getElementById('live-controls').style.display = 'block';
}

function stopAutoCapture() {
    if (autoCaptureInterval) clearInterval(autoCaptureInterval);
    if (timerInterval) clearInterval(timerInterval);
    document.getElementById('live-controls').style.display = 'none';
    document.getElementById('timer').textContent = '3';
    timeLeft = 3;
    document.getElementById('sidebar-content').innerHTML = '<p>Start live detection to see meaning here</p>';
}

function previewFile(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const preview = document.getElementById('media-preview');
    const url = URL.createObjectURL(file);
    
    if (file.type.startsWith('image/')) {
        preview.innerHTML = `<img src="${url}" alt="Preview">`;
        predictFile();
    } else {
        const vid = document.createElement('video');
        vid.src = url;
        vid.controls = true;
        preview.innerHTML = '';
        preview.appendChild(vid);
        predictFile();
    }
}

async function predictFile() {
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    const endpoint = currentMode === 'image' ? '/predict-image' : '/predict-video';
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            body: formData
        });
        if (!response.ok) throw new Error('API error');
        const result = await response.json();
        showResult(result);
    } catch (err) {
        alert('Prediction error: ' + err.message);
    } finally {
        showLoading(false);
    }
}

async function predictFrame(base64Image) {
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/predict-frame`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ base64_image: `data:image/jpeg;base64,${base64Image}` })
        });
        if (!response.ok) throw new Error('API error');
        const result = await response.json();
        updateSidebar(result);
        showResult(result);
    } catch (err) {
        console.error('Prediction error:', err);
    } finally {
        showLoading(false);
    }
}

function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
    document.getElementById('result').style.display = 'none';
}

function showResult(result) {
    document.getElementById('label').textContent = result.label;
    document.getElementById('confidence').textContent = `Confidence: ${(result.confidence * 100).toFixed(1)}%`;
    document.getElementById('result').style.display = 'block';
    document.getElementById('loading').style.display = 'none';
}

function updateSidebar(result) {
    const meaning = SIGN_MEANINGS[result.label] || 'Unknown sign';
    document.getElementById('sidebar-content').innerHTML = `
        <div style="text-align: center;">
            <h2 style="color: white; margin-bottom: 10px;">${result.label}</h2>
            <div style="font-size: 1.1em; opacity: 0.9;">${meaning}</div>
            <div style="margin-top: 15px; color: var(--success); font-weight: bold;">
                Confidence: ${(result.confidence * 100).toFixed(1)}%
            </div>
        </div>
    `;
}

// Cleanup
window.addEventListener('beforeunload', () => {
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
    }
    stopAutoCapture();
});
