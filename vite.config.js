import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()], // Add this line!
  server: {
    cors: true,
    hmr: { host: 'localhost' },
  },
  build: {
    outDir: 'app/statics/dist',
    emptyOutDir: true,
    rollupOptions: {
      input: 'src/main.jsx', // Change .js to .jsx
      output: { entryFileNames: 'main.js' },
    },
  },
})
