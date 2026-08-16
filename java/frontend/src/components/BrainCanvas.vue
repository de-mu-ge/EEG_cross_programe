<template>
  <div ref="containerRef" class="brain-canvas"></div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { BrainScene } from '../three/BrainScene'

const emit = defineEmits(['formed'])

const containerRef = ref(null)
let scene = null

onMounted(() => {
  scene = new BrainScene(containerRef.value, {
    onFormed: () => emit('formed')
  })
})

onBeforeUnmount(() => {
  scene?.dispose()
  scene = null
})

defineExpose({
  startTransition: () => scene?.startTransition()
})
</script>

<style scoped>
.brain-canvas {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.brain-canvas :deep(canvas) {
  display: block;
}
</style>
