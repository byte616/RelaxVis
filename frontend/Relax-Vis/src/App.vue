<script setup>
import { useRoute } from "vue-router";

const route = useRoute();
</script>

<template>
  <div>
    <!-- show logo only on home page -->
    <a v-if="route.name === 'Home'" href="https://github.com/byte616/RelaxVis/tree/main" target="_blank">
      <img src="./assets/cover.png" class="logo vue" alt="Vue logo" />
    </a>
  </div>

  <!-- router switch between homepage & graph page -->
  <router-view />
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
