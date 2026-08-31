import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base: "./" is required. The built app is served from a Hugging Face Space at a
// path that is not guaranteed to be the domain root; absolute asset paths give a
// blank page there while working fine on localhost.
export default defineConfig({
  plugins: [react()],
  base: "./",
  build: { outDir: "dist", sourcemap: false },
  server: {
    port: 5173,
    // Dev only. In production the API and the app are same-origin.
    proxy: { "/api": { target: "http://localhost:8000", changeOrigin: true } },
  },
});
