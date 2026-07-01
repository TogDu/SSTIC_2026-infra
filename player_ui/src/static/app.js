const resultEl = document.getElementById("result");
const buttons = document.querySelectorAll(".actions button");
const btnCreate = document.getElementById("btn-create");
const btnRestart = document.getElementById("btn-restart");
const btnDelete = document.getElementById("btn-delete");

function setButtons(instanceExists) {
    btnCreate.disabled = instanceExists;
    btnRestart.disabled = !instanceExists;
    btnDelete.disabled = !instanceExists;
}

function setResult(text, cls) {
    resultEl.className = "result " + cls;
    resultEl.textContent = text;
}

function formatEndpoints(endpoints) {
    if (!endpoints || Object.keys(endpoints).length === 0) return null;
    const div = document.createElement("div");
    div.className = "endpoints";
    const title = document.createElement("div");
    title.className = "endpoints-title";
    title.textContent = "Endpoints";
    div.appendChild(title);
    const list = document.createElement("div");
    list.className = "endpoints-list";
    for (const [name, value] of Object.entries(endpoints)) {
        const item = document.createElement("div");
        item.className = "endpoint-item";
        const label = document.createElement("span");
        label.className = "endpoint-label";
        label.textContent = name;
        const val = document.createElement("span");
        val.className = "endpoint-value";
        val.textContent = value;
        item.appendChild(label);
        item.appendChild(val);
        list.appendChild(item);
    }
    div.appendChild(list);
    return div;
}

const healthConfig = {
    Healthy:     { label: "Fonctionnel",        cls: "healthy" },
    Progressing: { label: "Démarrage en cours",  cls: "progressing" },
    Degraded:    { label: "Dégradé",             cls: "degraded" },
    Suspended:   { label: "Suspendu",            cls: "suspended" },
    Missing:     { label: "Inconnu",            cls: "missing" },
    Unknown:     { label: "Inconnu",             cls: "unknown" },
};

function showStatus(data) {
    const health = healthConfig[data.health] || healthConfig.Unknown;
    resultEl.className = "result status";
    resultEl.innerHTML = "";

    if (data.message) {
        const msg = document.createElement("div");
        msg.className = "status-message";
        msg.textContent = data.message;
        resultEl.appendChild(msg);
    }

    const badge = document.createElement("div");
    badge.className = "status-badge " + health.cls;
    const dot = document.createElement("span");
    dot.className = "status-dot";
    const label = document.createElement("span");
    label.textContent = health.label;
    badge.appendChild(dot);
    badge.appendChild(label);
    resultEl.appendChild(badge);

    if (data.expires_at) {
        const exp = document.createElement("div");
        exp.className = "expiration";
        const span = document.createElement("span");
        span.id = "expiration";
        const expiresDate = new Date(data.expires_at);
        span.dataset.expires = expiresDate.getTime();
        span.textContent = formatRemaining(expiresDate);
        exp.appendChild(span);
        const btn = document.createElement("button");
        btn.className = "btn-extend";
        btn.textContent = "Prolonger";
        btn.addEventListener("click", doExtend);
        exp.appendChild(btn);
        resultEl.appendChild(exp);
    }

    const endpointsEl = formatEndpoints(data.endpoints);
    if (endpointsEl) resultEl.appendChild(endpointsEl);
}

function formatRemaining(expiresDate) {
    const diff = expiresDate - Date.now();
    if (diff <= 0) return "Instance expirée";
    const mins = Math.floor(diff / 60000);
    const hours = Math.floor(mins / 60);
    const m = mins % 60;
    if (hours > 0) return `Expire dans ${hours}h${String(m).padStart(2, "0")}`;
    return `Expire dans ${m} min`;
}

let warningFired = false;

function playBell() {
    const ctx = new AudioContext();
    [0, 0.3].forEach((offset) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = "sine";
        osc.frequency.value = 830;
        gain.gain.setValueAtTime(0.3, ctx.currentTime + offset);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + offset + 0.6);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(ctx.currentTime + offset);
        osc.stop(ctx.currentTime + offset + 0.6);
    });
}

function checkExpirationWarning() {
    const el = document.getElementById("expiration");
    if (!el || !el.dataset.expires) return;
    const remaining = Number(el.dataset.expires) - Date.now();
    if (remaining > 0 && remaining <= 5 * 60000 && !warningFired) {
        warningFired = true;
        playBell();
        if (Notification.permission === "granted") {
            new Notification("SSTIC Challenge", { body: "Votre instance expire dans moins de 5 minutes !" });
        } else if (Notification.permission !== "denied") {
            Notification.requestPermission().then((p) => {
                if (p === "granted") new Notification("SSTIC Challenge", { body: "Votre instance expire dans moins de 5 minutes !" });
            });
        }
    }
    if (remaining > 5 * 60000) warningFired = false;
}

setInterval(() => {
    const el = document.getElementById("expiration");
    if (!el || !el.dataset.expires) return;
    el.textContent = formatRemaining(new Date(Number(el.dataset.expires)));
    checkExpirationWarning();
}, 30000);

const eventSource = new EventSource(BASE_URL + "/stream");

eventSource.onmessage = (e) => {
    const data = JSON.parse(e.data);
    if (data.success) {
        showStatus(data);
        setButtons(true);
    } else {
        setResult(data.message, "error");
        setButtons(false);
    }
};

const POW_URL = BASE_URL.replace("/instance", "/pow");

function solvePoW(challenge, difficulty) {
    return new Promise((resolve, reject) => {
        const worker = new Worker("/static/pow-worker.js");
        worker.onmessage = (e) => {
            if (e.data.type === "solved") {
                worker.terminate();
                resolve(e.data.nonce);
            }
        };
        worker.onerror = () => {
            worker.terminate();
            reject(new Error("Proof of Work failed"));
        };
        worker.postMessage({ challenge, difficulty });
    });
}

async function doAction(action) {
    buttons.forEach((b) => (b.disabled = true));

    const body = new URLSearchParams();
    body.set("action", action);

    if (action === "create") {
        setResult("Loading ...", "loading");
        try {
            const powResp = await fetch(POW_URL);
            if (powResp.status === 401) {
                setResult("Invalid session cookie.", "error");
                return;
            }
            if (powResp.status === 429) {
                setResult("Too many requests, please try again later.", "error");
                return;
            }
            const powData = await powResp.json();
            if (!powData.success) {
                setResult(powData.message || "PoW error", "error");
                return;
            }

            setResult("Loading captcha ...", "loading");
            const nonce = await solvePoW(powData.challenge, powData.difficulty);
            body.set("pow_challenge", powData.challenge);
            body.set("pow_nonce", nonce);
        } catch (e) {
            setResult("Error: " + e.message, "error");
            return;
        }
    }

    setResult("Please wait ...", "loading");

    try {
        const resp = await fetch(BASE_URL, { method: "POST", body });

        if (resp.status === 401) {
            setResult("Invalid session cookie.", "error");
            return;
        }
        if (resp.status === 429) {
            setResult("Too many requests, please try again later.", "error");
            return;
        }

        const data = await resp.json();

        if (!data.success) {
            setResult(data.message, "error");
        }
    } catch (e) {
        setResult("Network error: " + e.message, "error");
    }
}

buttons.forEach((btn) => {
    btn.addEventListener("click", () => doAction(btn.dataset.action));
});

setButtons(false);

// Extend instance
async function doExtend() {
    const btn = document.querySelector(".btn-extend");
    if (btn) btn.disabled = true;
    try {
        const resp = await fetch(BASE_URL + "/extend", { method: "POST" });
        const data = await resp.json();
        if (data.success && data.expires_at) {
            const el = document.getElementById("expiration");
            if (el) {
                const expiresDate = new Date(data.expires_at);
                el.dataset.expires = expiresDate.getTime();
                el.textContent = formatRemaining(expiresDate);
            }
        }
    } catch (e) {
        // silently ignore
    } finally {
        if (btn) btn.disabled = false;
    }
}

// Flag submission
const flagInput = document.getElementById("flag-input");
const btnFlag = document.getElementById("btn-flag");
const flagResultEl = document.getElementById("flag-result");

btnFlag.addEventListener("click", async () => {
    const flag = flagInput.value.trim();
    if (!flag) return;

    btnFlag.disabled = true;
    flagResultEl.className = "flag-result loading";
    flagResultEl.textContent = "Checking ...";

    const body = new URLSearchParams();
    body.set("flag", flag);

    try {
        const resp = await fetch(BASE_URL.replace("/instance", "/flag"), { method: "POST", body });
        const data = await resp.json();

        if (data.success) {
            flagResultEl.className = "flag-result success";
            if (data.next_step) {
                flagResultEl.innerHTML = "";
                flagResultEl.appendChild(document.createTextNode(data.message + " "));
                const link = document.createElement("a");
                link.href = data.next_step;
                link.textContent = "Go to next step";
                flagResultEl.appendChild(link);
            } else {
                flagResultEl.textContent = data.message;
            }
        } else {
            flagResultEl.className = "flag-result error";
            flagResultEl.textContent = data.message;
        }
    } catch (e) {
        flagResultEl.className = "flag-result error";
        flagResultEl.textContent = "Network error: " + e.message;
    } finally {
        btnFlag.disabled = false;
    }
});
