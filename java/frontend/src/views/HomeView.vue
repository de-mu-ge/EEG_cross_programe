<template>
  <div class="home">
    <NeuralScene ref="sceneRef" @formed="uploadVisible = true" />

    <div class="hud hud-top" :class="{ 'hud-hidden': started }">
      <h1 class="title">NEURO-AI</h1>
      <p class="subtitle">Decode the hidden signals of human emotion.</p>
    </div>

    <div class="hud hud-bottom" :class="{ 'hud-hidden': started }">
      <button class="start-btn" @click="onStart">START ANALYSIS</button>
      <p class="hint" :class="{ 'hint-hidden': explored }">
        move your cursor — you are the only light source
      </p>
    </div>

    <Transition name="fade">
      <div v-if="uploadVisible" class="upload-overlay">
        <UploadZone />
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { onBeforeUnmount, ref } from 'vue'
import NeuralScene from '../components/NeuralScene.vue'
import UploadZone from '../components/UploadZone.vue'

const sceneRef = ref(null)
const started = ref(false)
const uploadVisible = ref(false)
const explored = ref(false)

const onFirstMove = () => {
  explored.value = true
  window.removeEventListener('pointermove', onFirstMove)
}
window.addEventListener('pointermove', onFirstMove)
onBeforeUnmount(() => window.removeEventListener('pointermove', onFirstMove))

function onStart() {
  started.value = true
  sceneRef.value?.startTransition()
}
</script>

<style scoped>
.home {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: #030303;
}

.hud {
  position: absolute;
  left: 0;
  right: 0;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  pointer-events: none;
  transition: opacity 0.9s ease;
}

.hud-hidden {
  opacity: 0;
}

.hud-top {
  top: 8vh;
  text-align: center;
}

.title {
  margin: 0 0 16px;
  font-size: clamp(20px, 2.4vw, 30px);
  font-weight: 200;
  letter-spacing: 0.55em;
  padding-left: 0.55em; /* 抵消末字符字距，保持视觉居中 */
  color: rgba(235, 238, 242, 0.92);
}

.subtitle {
  margin: 0;
  font-size: 12px;
  font-weight: 300;
  letter-spacing: 0.3em;
  padding-left: 0.3em;
  color: rgba(138, 147, 155, 0.75);
}

.hud-bottom {
  bottom: 9vh;
  gap: 26px;
}

.start-btn {
  pointer-events: auto;
  padding: 16px 54px;
  font-size: 12px;
  letter-spacing: 0.45em;
  padding-left: calc(54px + 0.45em);
  color: rgba(235, 238, 242, 0.7);
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 2px;
  cursor: pointer;
  transition:
    color 0.4s,
    border-color 0.4s,
    box-shadow 0.4s;
}

.start-btn:hover {
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow:
    0 0 32px rgba(255, 255, 255, 0.1),
    inset 0 0 14px rgba(255, 255, 255, 0.04);
}

.hint {
  margin: 0;
  font-size: 10px;
  letter-spacing: 0.32em;
  padding-left: 0.32em;
  color: rgba(138, 147, 155, 0.4);
  transition: opacity 1.2s ease;
}

.hint-hidden {
  opacity: 0;
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
  transition: opacity 0.8s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
