<template>
  <div ref="containerRef" class="neural-scene"></div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { NeuralScene } from '../three/NeuralScene'

const emit = defineEmits(['formed'])

const containerRef = ref(null)
let scene = null

onMounted(() => {
  scene = new NeuralScene(containerRef.value, {
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
.neural-scene {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.neural-scene :deep(canvas) {
  display: block;
}
</style>
