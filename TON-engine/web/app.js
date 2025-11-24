const WALLET_BASE_URL = "http://localhost:8081"; // ערוך לפי ה-URL שבו רץ שירות SLH Wallet

async function callEndpoint(path, opts = {}) {
    const outputEl = opts.output;
    if (outputEl) {
        outputEl.textContent = "טוען...";
    }
    try {
        const res = await fetch(path, { method: "GET" });
        const txt = await res.text();
        let data;
        try {
            data = JSON.parse(txt);
        } catch {
            data = txt;
        }
        if (outputEl) {
            outputEl.textContent = JSON.stringify(data, null, 2);
        }
    } catch (err) {
        if (outputEl) {
            outputEl.textContent = "שגיאה בבקשה: " + err.message;
        }
    }
}

async function callWallet(path, opts = {}) {
    const outputEl = opts.output;
    if (outputEl) {
        outputEl.textContent = "טוען נתוני ארנק...";
    }
    try {
        const res = await fetch(WALLET_BASE_URL + path, { method: "GET" });
        const txt = await res.text();
        let data;
        try {
            data = JSON.parse(txt);
        } catch {
            data = txt;
        }
        if (outputEl) {
            outputEl.textContent = JSON.stringify(data, null, 2);
        }
    } catch (err) {
        if (outputEl) {
            outputEl.textContent = "שגיאה בבקשה לארנק: " + err.message;
        }
    }
}

window.addEventListener("DOMContentLoaded", () => {
    const healthOut = document.getElementById("health-output");
    const analysisOut = document.getElementById("analysis-output");
    const walletOut = document.getElementById("wallet-output");
    const symbolInput = document.getElementById("symbol-input");

    document.getElementById("check-health")?.addEventListener("click", () => {
        callEndpoint("/health", { output: healthOut });
    });

    document.getElementById("run-analysis")?.addEventListener("click", () => {
        callEndpoint("/analysis?symbol=TONUSDT", { output: analysisOut });
    });

    document.getElementById("run-multi")?.addEventListener("click", () => {
        callEndpoint("/multi_analysis", { output: analysisOut });
    });

    document.getElementById("run-custom")?.addEventListener("click", () => {
        const symbol = symbolInput.value || "TONUSDT";
        callEndpoint(`/analysis?symbol=${encodeURIComponent(symbol)}`, { output: analysisOut });
    });

    document.getElementById("check-wallet")?.addEventListener("click", () => {
        callWallet("/balances", { output: walletOut });
    });
});
