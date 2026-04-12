import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { viteSingleFile } from 'vite-plugin-singlefile'

// Special config for single-file offline distribution
export default defineConfig({
  plugins: [
    react(), 
    tailwindcss(),
    viteSingleFile()
  ],
  build: {
    outDir: 'offline',
    emptyOutDir: true,
  }
})
