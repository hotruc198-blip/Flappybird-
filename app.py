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
    background: linear-gradient(#74d3e5, #e8fff0);
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
    "Chạm để bay qua các đường ống xanh!"
    "</p>",
    unsafe_allow_html=True
)

game_html = r'''
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport"
 content="width=device-width, initial-scale=1">
<style>
body {
    margin: 0;
    background: #80d6e5;
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
p {
    text-align: center;
    color: #205d46;
    font-size: 14px;
}
</style>
</head>
<body>

<canvas id="game" width="800" height="530"></canvas>
<p>📱 Chạm màn hình để bay | 💻 Nhấn Space để bay</p>

<script>
(function () {
"use strict";

const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const W = 800, H = 530, GAP = 165;

let state = "menu";
let bird = {x: 160, y: 250, vy: 0, angle: 0};
let pipes = [];
let score = 0;
let best = 0;
let frame = 0;
let lastPipe = 0;
let musicOn = true;
let audio = null;
let musicTimer = null;

try {
    best = Number(localStorage.getItem("skyBest") || 0);
} catch (e) {}

function startAudio() {
    try {
        if (!audio) {
            const AC = window.AudioContext ||
                       window.webkitAudioContext;
            if (AC) audio = new AC();
        }
        if (audio && audio.state === "suspended") {
            audio.resume();
        }
    } catch (e) {}
}

function sound(freq, duration, type, volume) {
    if (!musicOn) return;
    startAudio();
    if (!audio) return;

    try {
        const osc = audio.createOscillator();
        const gain = audio.createGain();

        osc.type = type || "sine";
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(
            volume || 0.04, audio.currentTime
        );
        gain.gain.exponentialRampToValueAtTime(
            0.001, audio.currentTime + duration
        );

        osc.connect(gain);
        gain.connect(audio.destination);
        osc.start();
        osc.stop(audio.currentTime + duration);
    } catch (e) {}
}

function stopMusic() {
    if (musicTimer !== null) {
        clearInterval(musicTimer);
        musicTimer = null;
    }
}

function startMusic() {
    stopMusic();
    if (!musicOn) return;

    const notes = [523, 659, 784, 659, 587, 698, 784, 659];
    let i = 0;

    musicTimer = setInterval(function () {
        if (state === "playing") {
            sound(notes[i % notes.length], 0.16, "sine", 0.018);
            i++;
        }
    }, 260);
}

function resetGame() {
    bird = {x: 160, y: 250, vy: 0, angle: 0};
    pipes = [];
    score = 0;
    frame = 0;
    lastPipe = 0;
    state = "playing";
    startAudio();
    startMusic();
    sound(600, 0.08, "triangle", 0.06);
}

function gameOver() {
    if (state !== "playing") return;
    state = "over";
    stopMusic();
    sound(150, 0.3, "sawtooth", 0.06);

    if (score > best) {
        best = score;
        try {
            localStorage.setItem("skyBest", String(best));
        } catch (e) {}
    }
}

function flap() {
    if (state !== "playing") {
        resetGame();
    } else {
        bird.vy = -7.2;
        sound(650, 0.07, "triangle", 0.05);
    }
}

canvas.addEventListener("pointerdown", function (e) {
    e.preventDefault();

    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) * W / rect.width;
    const y = (e.clientY - rect.top) * H / rect.height;

    if (state !== "playing" &&
        x > 300 && x < 500 &&
        y > 365 && y < 440) {
        toggleMusic();
        return;
    }

    flap();
});

document.addEventListener("keydown", function (e) {
    if (e.code === "Space" || e.code === "ArrowUp") {
        e.preventDefault();
        flap();
    }
    if (e.code === "KeyM") toggleMusic();
});

function toggleMusic() {
    musicOn = !musicOn;
    if (musicOn) {
        startAudio();
        if (state === "playing") startMusic();
    } else {
        stopMusic();
    }
}

function text(str, x, y, size, color, outline) {
    ctx.font = "bold " + size + "px Arial";
    ctx.textAlign = "center";
    ctx.lineWidth = 4;
    ctx.strokeStyle = outline || "#276b45";
    ctx.strokeText(str, x, y);
    ctx.fillStyle = color || "white";
    ctx.fillText(str, x, y);
}

function background() {
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, "#61c7d8");
    g.addColorStop(1, "#c4f2ed");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
    
