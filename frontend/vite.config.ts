import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import packageJson from "./package.json";
import { checkHealth, getInfo } from "./src/api/manage";

function manageEndpointsPlugin() {
  return {
    name: "manage-endpoints-plugin",
    configureServer(server: any) {
      server.middlewares.use((req: any, res: any, next: any) => {
        if (req.url === "/manage/health") {
          const { payload, statusCode } = checkHealth();
          res.statusCode = statusCode;
          res.setHeader("Content-Type", "application/json");
          res.end(JSON.stringify(payload));
          return;
        }
        if (req.url === "/manage/info") {
          const { payload, statusCode } = getInfo("GuíaVital", process.env.APP_VERSION || packageJson.version);
          res.statusCode = statusCode;
          res.setHeader("Content-Type", "application/json");
          res.end(JSON.stringify(payload));
          return;
        }
        next();
      });
    },
  };
}

export default defineConfig({
  plugins: [react(), manageEndpointsPlugin()],
  server: {
    port: 5173,
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./tests/setup.ts",
  },
});
