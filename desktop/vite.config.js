import { defineConfig } from "vite";
import obfuscatorPlugin from "vite-plugin-bundle-obfuscator";

export default defineConfig(({ mode }) => {
  const isProduction = mode === "production";

  return {
    base: "./", // Crucial for Electron local file loading
    build: {
      outDir: ".vite", // Vite outputs files here
      emptyOutDir: true,
    },
    server: {
      port: 3000,
    },
    plugins: [
      isProduction &&
        obfuscatorPlugin({
          options: {
            compact: true,
            controlFlowFlattening: true,
            controlFlowFlatteningThreshold: 0.75,
            deadCodeInjection: true,
            deadCodeInjectionThreshold: 0.4,
            identifierNamesGenerator: "hexadecimal",
            renameGlobals: false,
            stringArray: true,
            stringArrayEncoding: ["base64"],
            stringArrayThreshold: 0.75,
            transformObjectKeys: true,
          },
        }),
    ].filter(Boolean),
  };
});
