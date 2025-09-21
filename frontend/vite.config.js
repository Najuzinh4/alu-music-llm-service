import { defineConfig } from 'vite'

export default defineConfig({
  root: '.',
  base: '/dashboard/app/',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})
