<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()

console.log("Graph page params:", route.query.filename)
</script>

<template>
  <div class="graph-page">
    <h1>Graph Page</h1>
    
  </div>
</template>

<style scoped>
.graph-page {
  text-align: center;
  padding: 2rem;
  color: #eee;
}
</style>
