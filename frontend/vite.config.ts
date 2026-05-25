import { fileURLToPath, URL } from 'node:url';
import { defineConfig, type Plugin } from 'vite';
import vue from '@vitejs/plugin-vue';
import tailwindcss from '@tailwindcss/vite';

const apiProxyTarget = process.env.VITE_API_PROXY_TARGET ?? 'http://localhost:8000';
const devHost = 'localhost';
const devPort = 5173;

function canonicalLocalhostRedirect(): Plugin {
  return {
    name: 'canonical-localhost-redirect',
    configureServer(server) {
      server.middlewares.use((request, response, next) => {
        const host = request.headers.host ?? '';
        const [hostname, port] = host.split(':');

        if (hostname === '127.0.0.1') {
          response.statusCode = 308;
          response.setHeader(
            'Location',
            `http://${devHost}:${port || devPort}${request.url ?? '/'}`,
          );
          response.end();
          return;
        }

        next();
      });
    },
  };
}

export default defineConfig({
  plugins: [canonicalLocalhostRedirect(), vue(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: '0.0.0.0',
    port: devPort,
    strictPort: true,
    proxy: {
      '/api': {
        target: apiProxyTarget,
        changeOrigin: true,
      },
    },
  },
});
