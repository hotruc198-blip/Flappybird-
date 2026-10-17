import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Sky Bird",
    page_icon="🐤",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(#b9f0f5, #e9fbff);
}
.block-container {
    max-width: 900px;
    padding-top: 1rem;
}
h1 {
    text-align: center;
    color: #176b37;
}
</style>
""", unsafe_allow_html=True)

st.title("🐤 SKY BIRD")
st.markdown(
    "<p style='text-align:center'>"
    "Chạm để bay qua các đường ống!"
    "</p>",
    unsafe_allow_html=True
)

game_html = r"""
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport"
 content="width=device-width, initial-scale=1,
 maximum-scale=1, user-scalable=no">
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    background: #b8edf2;
    font-family: Arial, sans-serif;
}
canvas {
    display: block;
    width: 100%;
    max-width: 760px;
    height: auto;
    margin: auto;
    border: 3px solid #397d54;
    border-radius: 12px;
    touch-action: manipulation;
}
.hint {
    text-align: center;
    color: #235c64;
    font-size: 13px;
    padding: 8px;
}
</style>
</head>
<body>

<canvas id="game" width="900" height="600"></canvas>
<div class="hint">
  📱 Chạm để bay | 💻 Space để bay | M để bật/tắt nhạc
</div>

<script>
(() => {
"use strict";

const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

const W = 900;
const H = 600;
const GAP = 180;

let state = "menu";
let bird = {x: 205, y: 285, vy: 0, rot: 0};
let pipes = [];
let score = 0;
let frame = 0;
let lastPipe = 0;
let best = 0;
let musicOn = true;
let audioCtx = null;
let musicTimer = null;

try {
    best = Number(
        localStorage.getItem("skyBirdBest") || 0
    );
} catch (e) {
    best = 0;
}

function initAudio() {
    try {
        if (!audioCtx) {
            const AC =
                window.AudioContext ||
                window.webkitAudioContext;
            if (AC) audioCtx = new AC();
        }
        if (audioCtx &&
            audioCtx.state === "suspended") {
            audioCtx.resume();
        }
    } catch (e) {}
}

function tone(freq, duration, type, volume, delay) {
    if (!musicOn) return;

    initAudio();
    if (!audioCtx) return;

    try {
        const start = audioCtx.currentTime + (delay || 0);
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();

        osc.type = type || "sine";
        osc.frequency.setValueAtTime(freq, start);

        gain.gain.setValueAtTime(volume || 0.03, start);
        gain.gain.exponentialRampToValueAtTime(
            0.001, start + duration
        );

        osc.connect(gain);
        gain.connect(audioCtx.destination);

        osc.start(start);
        osc.stop(start + duration + 0.02);
    } catch (e) {}
}

function flapSound() {
    tone(540, 0.08, "triangle", 0.06, 0);
    tone(760, 0.07, "sine", 0.03, 0.04);
}

function pointSound() {
    tone(880, 0.10, "sine", 0.05, 0);
    tone(1175, 0.14, "sine", 0.04, 0.08);
}

function hitSound() {
    tone(180, 0.20, "sawtooth", 0.06, 0);
    tone(100, 0.25, "triangle", 0.04, 0.10);
}

function startMusic() {
    stopMusic();
    if (!musicOn) return;

    const notes = [
        523, 659, 784, 659,
        587, 698, 880, 698
    ];
    let i = 0;

    musicTimer = setInterval(() => {
        if (state !== "playing" || !musicOn) return;
        tone(notes[i % notes.length], 0.15,
             "sine", 0.018, 0);
        i++;
    }, 260);
}

function stopMusic() {
    if (musicTimer !== null) {
        clearInterval(musicTimer);
        musicTimer = null;
    }
}

function toggleMusic() {
    musicOn = !musicOn;

    if (musicOn) {
        initAudio();
        if (state === "playing") startMusic();
    } else {
        stopMusic();
    }
}

function resetGame() {
    bird = {x: 205, y: 285, vy: 0, rot: 0};
    pipes = [];
    score = 0;
    frame = 0;
    lastPipe = 0;
    state = "playing";

    initAudio();
    startMusic();
    flapSound();
}

function gameOver() {
    if (state !== "playing") return;

    state = "over";
    stopMusic();
    hitSound();

    if (score > best) {
        best = score;
        try {
            localStorage.setItem("skyBirdBest", best);
        } catch (e) {}
    }
}

function flap() {
    if (state === "menu" || state === "over") {
        resetGame();
        return;
    }

    if (state === "playing") {
        bird.vy = -7.5;
        flapSound();
    }
}

canvas.addEventListener("pointerdown", (e) => {
    e.preventDefault();

    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) * W / rect.width;
    const y = (e.clientY - rect.top) * H / rect.height;

    // Nút nhạc trên menu
    if ((state === "menu" || state === "over") &&
        y >= 432 && y <= 475 &&
        x >= 350 && x <= 550) {
        toggleMusic();
        return;
    }

    flap();
});

document.addEventListener("keydown", (e) => {
    if (e.code === "Space
