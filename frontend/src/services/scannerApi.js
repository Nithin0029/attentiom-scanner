const BASE_URL = "http://127.0.0.1:8000";

async function request(path, options = {}) {
    let response;

    try {
        response = await fetch(`${BASE_URL}${path}`, {
            ...options,
            headers: {
                "Content-Type": "application/json",
                ...(options.headers || {}),
            },
        });
    } catch (networkError) {
        throw new Error(
            "Cannot reach the backend server. Make sure it is running."
        );
    }

    let data = null;

    try {
        data = await response.json();
    } catch (parseError) {
        data = null;
    }

    if (!response.ok) {
        const detail =
            data && data.detail
                ? data.detail
                : `Request failed with status ${response.status}.`;

        throw new Error(detail);
    }

    return data;
}

export async function getHealth() {
    return request("/health");
}

export async function startScanner() {
    return request("/api/scanner/start", {
        method: "POST",
    });
}

export async function stopScanner() {
    return request("/api/scanner/stop", {
        method: "POST",
    });
}

export async function getScannerStatus() {
    return request("/api/scanner/status");
}

export async function getScannerSummary() {
    return request("/api/scanner/summary");
}

export async function sendFrame(frameBlob) {
    const formData = new FormData();
    formData.append("file", frameBlob, "frame.jpg");

    let response;

    try {
        response = await fetch(`${BASE_URL}/api/scanner/frame`, {
            method: "POST",
            body: formData,
        });
    } catch (networkError) {
        throw new Error("Cannot reach the backend server.");
    }

    let data = null;

    try {
        data = await response.json();
    } catch (parseError) {
        data = null;
    }

    if (!response.ok) {
        const detail =
            data && data.detail
                ? data.detail
                : `Frame upload failed with status ${response.status}.`;

        throw new Error(detail);
    }

    return data;
}
