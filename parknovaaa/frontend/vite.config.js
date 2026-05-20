import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const isVercel = Boolean(process.env.VERCEL)

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: isVercel ? '/' : '/app/',
  build: {
    outDir: isVercel ? 'dist' : '../src/main/resources/static/app',
    emptyOutDir: true
  }
})
