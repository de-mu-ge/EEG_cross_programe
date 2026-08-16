<template>
  <div
    class="upload-zone"
    :class="{ 'is-dragover': isDragover }"
    @click="inputRef.click()"
    @dragover.prevent="isDragover = true"
    @dragleave.prevent="isDragover = false"
    @drop.prevent="onDrop"
  >
    <input ref="inputRef" type="file" accept=".dat" class="upload-input" @change="onPick" />

    <template v-if="status === 'idle'">
      <p class="upload-hint">DROP EEG FILE HERE</p>
      <p class="upload-sub">.dat · or click to browse</p>
    </template>
    <p v-else-if="status === 'uploading'" class="upload-hint">ANALYZING {{ fileName }} …</p>
    <template v-else-if="status === 'done'">
      <p class="upload-hint upload-result">{{ resultText }}</p>
      <p class="upload-sub">click to analyze another file</p>
    </template>
    <template v-else>
      <p class="upload-hint upload-error">ANALYSIS FAILED</p>
      <p class="upload-sub">{{ errorMessage }}</p>
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { getEegResult, uploadEegFile } from '../api/eeg'

const inputRef = ref(null)
const isDragover = ref(false)
const status = ref('idle')
const fileName = ref('')
const result = ref(null)
const errorMessage = ref('')

const resultText = computed(() => {
  if (!result.value) return ''
  const data = result.value?.data ?? result.value
  const emotion = data?.emotion ?? data?.result?.emotion
  const confidence = data?.confidence ?? data?.result?.confidence
  if (emotion == null) return 'DONE'
  const pct = confidence != null ? ` · ${(confidence * 100).toFixed(1)}%` : ''
  return `${String(emotion).toUpperCase()}${pct}`
})

function onPick(e) {
  const file = e.target.files?.[0]
  if (file) upload(file)
  e.target.value = ''
}

function onDrop(e) {
  isDragover.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) upload(file)
}

async function upload(file) {
  fileName.value = file.name
  status.value = 'uploading'
  errorMessage.value = ''
  try {
    const uploadRes = await uploadEegFile(file)
    const fileId = uploadRes?.data?.data?.fileId
    result.value = fileId ? (await getEegResult(fileId)).data : uploadRes.data
    status.value = 'done'
  } catch (err) {
    errorMessage.value = err?.response?.data?.message || err.message || 'network error'
    status.value = 'error'
  }
}
</script>

<style scoped>
.upload-zone {
  width: min(420px, 80vw);
  padding: 48px 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  text-align: center;
  cursor: pointer;
  border: 1px dashed rgba(120, 150, 255, 0.35);
  border-radius: 18px;
  background: rgba(10, 14, 32, 0.35);
  backdrop-filter: blur(6px);
  transition: border-color 0.25s, background 0.25s;
}

.upload-zone:hover,
.upload-zone.is-dragover {
  border-color: rgba(160, 120, 255, 0.8);
  background: rgba(20, 24, 52, 0.5);
}

.upload-input {
  display: none;
}

.upload-hint {
  font-size: 13px;
  letter-spacing: 0.35em;
  color: #cfd8ff;
}

.upload-result {
  color: #9d7bff;
}

.upload-error {
  color: #ff6b8a;
}

.upload-sub {
  font-size: 11px;
  letter-spacing: 0.2em;
  color: rgba(160, 175, 220, 0.55);
}
</style>
