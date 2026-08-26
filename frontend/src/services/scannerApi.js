const API_BASE_URL = "http://127.0.0.1:8000/api";

async function request(endpoint, options = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || `Request failed with status ${response.status}`);
    }

    return data;
}

export async function startScanner() {
    return request("/scanner/start", {
        method: "POST",
    });
}

export async function stopScanner() {
    return request("/scanner/stop", {
        method: "POST",
    });
}

export async function getScannerStatus() {
    return request("/scanner/status");
}

export async function getScannerSummary() {
    return request("/scanner/summary");
}

export async function sendFrame(frameBlob) {
    const formData = new FormData();
    formData.append("file", frameBlob, "frame.jpg");

    const response = await fetch(`${API_BASE_URL}/scanner/frame`, {
        method: "POST",
        body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || `Frame upload failed with status ${response.status}`);
    }

    return data;
}