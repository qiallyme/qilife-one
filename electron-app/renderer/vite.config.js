import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  root: '.', // use root index.html
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: resolve(__dirname, 'index.html'),
    },
  },
})
