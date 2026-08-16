<template>
  <div class="home">
    <BrainCanvas ref="brainRef" @formed="uploadVisible = true" />

    <header class="home-header">
      <span class="logo">NEURO·AI</span>
    </header>

    <Transition name="fade">
      <section v-if="!started" class="hero">
        <h1 class="hero-title">NEURO·AI</h1>
        <p class="hero-subtitle">Neural Emotion Recognition System</p>
        <p class="hero-copy">
          Understand the mind.<br />
          Decode human emotions.<br />
          Through brain waves.
        </p>
        <button class="start-btn" @click="onStart">START ANALYSIS</button>
      </section>
    </Transition>

    <Transition name="fade">
      <div v-if="uploadVisible" class="upload-overlay">
        <UploadZone />
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import BrainCanvas from '../components/BrainCanvas.vue'
import UploadZone from '../components/UploadZone.vue'

const brainRef = ref(null)
const started = ref(false)
const uploadVisible = ref(false)

function onStart() {
  started.value = true
  brainRef.value?.startTransition()
}
</script>

<style scoped>
.home {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background:
    radial-gradient(ellipse 70% 55% at 65% 45%, rgba(48, 56, 130, 0.22), transparent 70%),
    #05060f;
}

.home-header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10;
  padding: 28px 40px;
  pointer-events: none;
}

.logo {
  font-size: 13px;
  letter-spacing: 0.45em;
  color: rgba(190, 200, 245, 0.6);
}

.hero {
  position: absolute;
  z-index: 10;
  left: clamp(40px, 8vw, 120px);
  top: 50%;
  transform: translateY(-50%);
  max-width: 420px;
}

.hero-title {
  font-size: clamp(40px, 5vw, 64px);
  font-weight: 200;
  letter-spacing: 0.18em;
  color: #eef1ff;
  margin: 0 0 14px;
}

.hero-subtitle {
  font-size: 12px;
  letter-spacing: 0.4em;
  text-transform: uppercase;
  color: #8ea0ff;
  margin: 0 0 34px;
}

.hero-copy {
  font-size: 15px;
  font-weight: 300;
  line-height: 2.1;
  letter-spacing: 0.12em;
  color: rgba(200, 208, 240, 0.65);
  margin: 0 0 44px;
}

.start-btn {
  padding: 15px 44px;
  font-size: 12px;
  letter-spacing: 0.4em;
  color: #dfe6ff;
  background: transparent;
  border: 1px solid rgba(140, 160, 255, 0.45);
  border-radius: 999px;
  cursor: pointer;
  transition: box-shadow 0.3s, border-color 0.3s, background 0.3s;
}

.start-btn:hover {
  border-color: rgba(170, 130, 255, 0.9);
  background: rgba(90, 90, 220, 0.12);
  box-shadow: 0 0 24px rgba(110, 110, 255, 0.35);
}

.upload-overlay {
  position: absolute;
  z-index: 10;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.upload-overlay > * {
  pointer-events: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.7s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .hero {
    left: 50%;
    top: auto;
    bottom: 8vh;
    transform: translateX(-50%);
    text-align: center;
  }
}
</style>
