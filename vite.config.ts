import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";
import { defineConfig, type UserConfig } from "vite";

export default defineConfig((): UserConfig => {
  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: { "@": path.resolve(__dirname, "src") },
    },
    server: {
      port: 5173,
      strictPort: true,
      proxy: {
        "/api": { target: "http://127.0.0.1:8000", changeOrigin: true, secure: false },
        "/media": { target: "http://127.0.0.1:8000", changeOrigin: true, secure: false },
      },
    },
  };
});

