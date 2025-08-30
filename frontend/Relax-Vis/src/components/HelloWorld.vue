<script setup>
import { ref } from 'vue'

defineProps({
  msg: String,
})

const count = ref(0)

const handleFileUpload = (event) => {
  // Get the selected file
  const file = event.target.files[0];

  // Ensure a file was selected
  if (!file) return;
  console.log("Selected file:", file.name);

  // Read the file content
  const reader = new FileReader();
  reader.onload = (e) => {
    console.log("--- File Content ---");
    console.log(e.target.result);
  };

  // Read the file as text
  reader.readAsText(file);

};

// Dropdown menu state
const isOpen = ref(false)
const toggleMenu = () => {
  isOpen.value = !isOpen.value
}

</script>

<template>
  <div class="upload-section">
    <!-- hide input -->
    <input 
      type="file" 
      id="ir-upload" 
      @change="handleFileUpload" 
      class="hidden-input"
    >
    
    <!-- button -->
    <label for="ir-upload" class="upload-btn">
      Open Model
    </label>
  </div>

  <div class="app">
    <!-- hamburger button -->
    <div class="hamburger" @click="toggleMenu">
      <span></span>
      <span></span>
      <span></span>
    </div>
    
    <!-- menu -->
    <div class="sidebar" :class="{ open: isOpen }">
      <ul>
        <li><a href="https://github.com/byte616/RelaxVis/issues">Report Issue</a></li>
      </ul>
    </div>
    
    <!-- mask -->
    <div v-if="isOpen" class="overlay" @click="toggleMenu"></div>
  </div>
  
</template>


<style scoped>
.read-the-docs {
  color: #888;
}
.upload-section {
  margin-top: 2rem;
  text-align: center;
}

.hidden-input {
  display: none;
}

.upload-btn {
  display: inline-block;
  padding: 10px 20px;
  border: 1px solid #888;
  border-radius: 20px;
  background-color: transparent;
  color: #ccc;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.upload-btn:hover {
  background-color: #333;
  color: white;
}

/* hamburger button */
.hamburger {
  position: absolute;
  top: 10px;
  left: 10px;
  cursor: pointer;
  z-index: 1001;
}

.hamburger span {
  display: block;
  width: 20px;
  height: 2px;
  margin: 4px;
  background: #ccc;
}

/* menu */
.sidebar {
  position: fixed;
  top: 0;
  left: -250px; /* hide */
  width: 250px;
  height: 100%;
  background: #2a2a2a;
  padding: 20px;
  transition: left 0.3s ease;
  z-index: 1000;
}

.sidebar.open {
  left: 0; /* show */
}

.sidebar ul {
  list-style: none;
  padding: 0;
}

.sidebar li {
  margin: 20px 0;
}

.sidebar a {
  color: #ccc;
  text-decoration: none;
  transition: color 0.2s;
}

.sidebar a:hover {
  color: white;
}

/* mask */
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.4);
  z-index: 999;
}
</style>
