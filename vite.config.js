import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    cors: true,
    hmr: { host: 'localhost' },
  },
  build: {
    outDir: 'app/statics/dist',
    emptyOutDir: true,
    assetsDir: '', // Keeps assets in the root of the dist folder
    rollupOptions: {
      input: 'src/main.jsx',
      output: {
        entryFileNames: 'main.js',
        assetFileNames: (assetInfo) => {
          if (assetInfo.name.endsWith('.css')) return 'main.css';
          return assetInfo.name;
        },
      },
    },
  },
})
