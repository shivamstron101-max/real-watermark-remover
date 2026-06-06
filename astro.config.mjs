import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'astro/config';

export default defineConfig({
  output: 'static',
  vite: {
    plugins: [tailwindcss()],
    server: {
      proxy: {
        '/api/proxy/detect': {
          target: 'https://shivamstron304--watermark-remover-v3-web.modal.run',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api\/proxy\/detect/, '/detect')
        },
        '/api/proxy/ping': {
          target: 'https://shivamstron304--watermark-remover-v3-web.modal.run',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api\/proxy\/ping/, '/')
        },
        '/api/proxy/test': {
          target: 'https://shivamstron304--watermark-remover-v3-web.modal.run',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api\/proxy\/test/, '/test-post')
        },
        '/api/proxy': {
          target: 'https://shivamstron304--watermark-remover-v3-web.modal.run',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api\/proxy/, '/process')
        }
      }
    }
  },
});
