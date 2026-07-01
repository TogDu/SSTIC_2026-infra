// Proof-of-Work Web Worker — synchronous pure-JS SHA-256
// Finds nonce such that SHA-256(challenge || nonce) has `difficulty` leading zero bits.

"use strict";

// ---------- Pure-JS SHA-256 ----------

const K = new Uint32Array([
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
    0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
    0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]);

function sha256(data) {
    // Pre-processing: padding
    const msgLen = data.length;
    const bitLen = msgLen * 8;
    // message + 1 byte (0x80) + padding + 8 bytes length
    const totalLen = Math.ceil((msgLen + 9) / 64) * 64;
    const buf = new Uint8Array(totalLen);
    buf.set(data);
    buf[msgLen] = 0x80;
    // Big-endian 64-bit length at end (only lower 32 bits needed here)
    const view = new DataView(buf.buffer);
    view.setUint32(totalLen - 4, bitLen, false);

    let h0 = 0x6a09e667, h1 = 0xbb67ae85, h2 = 0x3c6ef372, h3 = 0xa54ff53a;
    let h4 = 0x510e527f, h5 = 0x9b05688c, h6 = 0x1f83d9ab, h7 = 0x5be0cd19;

    const w = new Uint32Array(64);

    for (let offset = 0; offset < totalLen; offset += 64) {
        for (let i = 0; i < 16; i++) {
            w[i] = view.getUint32(offset + i * 4, false);
        }
        for (let i = 16; i < 64; i++) {
            const s0 = (rotr(w[i-15], 7)) ^ (rotr(w[i-15], 18)) ^ (w[i-15] >>> 3);
            const s1 = (rotr(w[i-2], 17)) ^ (rotr(w[i-2], 19)) ^ (w[i-2] >>> 10);
            w[i] = (w[i-16] + s0 + w[i-7] + s1) | 0;
        }

        let a = h0, b = h1, c = h2, d = h3, e = h4, f = h5, g = h6, h = h7;

        for (let i = 0; i < 64; i++) {
            const S1 = (rotr(e, 6)) ^ (rotr(e, 11)) ^ (rotr(e, 25));
            const ch = (e & f) ^ (~e & g);
            const temp1 = (h + S1 + ch + K[i] + w[i]) | 0;
            const S0 = (rotr(a, 2)) ^ (rotr(a, 13)) ^ (rotr(a, 22));
            const maj = (a & b) ^ (a & c) ^ (b & c);
            const temp2 = (S0 + maj) | 0;

            h = g; g = f; f = e; e = (d + temp1) | 0;
            d = c; c = b; b = a; a = (temp1 + temp2) | 0;
        }

        h0 = (h0 + a) | 0; h1 = (h1 + b) | 0;
        h2 = (h2 + c) | 0; h3 = (h3 + d) | 0;
        h4 = (h4 + e) | 0; h5 = (h5 + f) | 0;
        h6 = (h6 + g) | 0; h7 = (h7 + h) | 0;
    }

    const out = new Uint8Array(32);
    const ov = new DataView(out.buffer);
    ov.setUint32(0, h0, false);  ov.setUint32(4, h1, false);
    ov.setUint32(8, h2, false);  ov.setUint32(12, h3, false);
    ov.setUint32(16, h4, false); ov.setUint32(20, h5, false);
    ov.setUint32(24, h6, false); ov.setUint32(28, h7, false);
    return out;
}

function rotr(x, n) {
    return (x >>> n) | (x << (32 - n));
}

// ---------- Helpers ----------

function hexToBytes(hex) {
    const bytes = new Uint8Array(hex.length / 2);
    for (let i = 0; i < bytes.length; i++) {
        bytes[i] = parseInt(hex.substr(i * 2, 2), 16);
    }
    return bytes;
}

function bytesToHex(bytes) {
    let hex = "";
    for (let i = 0; i < bytes.length; i++) {
        hex += bytes[i].toString(16).padStart(2, "0");
    }
    return hex;
}

function checkDifficulty(hash, difficulty) {
    let bits = 0;
    for (let i = 0; i < hash.length && bits < difficulty; i++) {
        if (hash[i] === 0) { bits += 8; continue; }
        bits += Math.clz32(hash[i]) - 24;
        break;
    }
    return bits >= difficulty;
}

// ---------- Worker entry point ----------

self.onmessage = function (e) {
    const { challenge, difficulty } = e.data;
    const challengeBytes = hexToBytes(challenge);

    // Nonce is an 8-byte big-endian counter
    const combined = new Uint8Array(challengeBytes.length + 8);
    combined.set(challengeBytes);
    const nonceView = new DataView(combined.buffer, challengeBytes.length, 8);

    const REPORT_INTERVAL = 50000;
    let nonce = 0;

    while (true) {
        nonceView.setUint32(0, (nonce / 0x100000000) >>> 0, false);
        nonceView.setUint32(4, nonce >>> 0, false);

        const hash = sha256(combined);

        if (checkDifficulty(hash, difficulty)) {
            const nonceBytes = new Uint8Array(combined.buffer, challengeBytes.length, 8);
            self.postMessage({ type: "solved", nonce: bytesToHex(nonceBytes) });
            return;
        }

        nonce++;
        if (nonce % REPORT_INTERVAL === 0) {
            self.postMessage({ type: "progress", iterations: nonce });
        }
    }
};
