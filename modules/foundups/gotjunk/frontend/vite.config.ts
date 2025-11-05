import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
    // Load .env from project root (4 levels up)
    const envDir = path.resolve(__dirname, '../../../../');
    const env = loadEnv(mode, envDir, '');
    return {
      server: {
        port: 3000,
        host: '0.0.0.0',
      },
      plugins: [
        react()
      ],
      define: {
        'process.env.API_KEY': JSON.stringify(env.GEMINI_API_KEY_GotJunk),
        'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY_GotJunk)
      },
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '.'),
        }
      },
      optimizeDeps: {
        include: ['leaflet', 'react-leaflet', 'helia', '@helia/unixfs', '@helia/strings', 'blockstore-idb', 'multiformats']
      },
      build: {
        commonjsOptions: {
          transformMixedEsModules: true
        },
        rollupOptions: {
          external: [],
          output: {
            manualChunks: {
              'ipfs': ['helia', '@helia/unixfs', '@helia/strings', 'blockstore-idb', 'multiformats']
            }
          }
        }
      }
    };
});
