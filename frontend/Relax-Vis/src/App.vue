<script setup>
import HelloWorld from './components/HelloWorld.vue'
</script>

<template>
  <div>
    <a href="https://github.com/byte616/RelaxVis/tree/main" target="_blank">
      <img src="./assets/cover.png" class="logo vue" alt="Vue logo" />
    </a>
  </div>
  <HelloWorld msg="Relax Visualization" />
</template>

<style scoped>
.logo {
  height: 16em;
  padding: 1.0em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
