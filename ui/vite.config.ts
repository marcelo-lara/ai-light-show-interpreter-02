import { readdir } from "node:fs/promises";
import { extname } from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";

const SONGS_ROUTE = "/api/songs";
const SONG_DIRECTORIES = [
  fileURLToPath(new URL("./public/songs", import.meta.url)),
  fileURLToPath(new URL("../data/songs", import.meta.url)),
];

async function listSongs() {
  const songs = new Map<string, { fileName: string; stem: string }>();

  for (const directory of SONG_DIRECTORIES) {
    try {
      const entries = await readdir(directory, { withFileTypes: true });
      for (const entry of entries) {
        if (!entry.isFile() || extname(entry.name).toLowerCase() !== ".mp3") {
          continue;
        }
        songs.set(entry.name, {
          fileName: entry.name,
          stem: entry.name.replace(/\.mp3$/i, ""),
        });
      }
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== "ENOENT") {
        throw error;
      }
    }
  }

  return Array.from(songs.values()).sort((left, right) => left.stem.localeCompare(right.stem));
}

function songListPlugin(): Plugin {
  const registerRoute = (middlewares: { use: (...args: unknown[]) => void }) => {
    middlewares.use(async (request: { method?: string; url?: string }, response: { statusCode: number; setHeader: (name: string, value: string) => void; end: (body: string) => void }, next: () => void) => {
      if (request.method !== "GET" || request.url !== SONGS_ROUTE) {
        next();
        return;
      }

      try {
        const songs = await listSongs();
        response.statusCode = 200;
        response.setHeader("Content-Type", "application/json");
        response.setHeader("Cache-Control", "no-store");
        response.end(JSON.stringify({ songs }));
      } catch (error) {
        response.statusCode = 500;
        response.setHeader("Content-Type", "application/json");
        response.end(JSON.stringify({ message: error instanceof Error ? error.message : "Failed to load songs." }));
      }
    });
  };

  return {
    name: "song-list-route",
    configureServer(server) {
      registerRoute(server.middlewares);
    },
    configurePreviewServer(server) {
      registerRoute(server.middlewares);
    },
  };
}

export default defineConfig({
  plugins: [react(), songListPlugin()],
  server: {
    allowedHosts: ["s2.local"],
    host: "0.0.0.0",
    port: 3300,
  },
  preview: {
    allowedHosts: ["s2.local"],
    host: "0.0.0.0",
    port: 3300,
  },
});
