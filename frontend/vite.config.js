import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import obfuscatorPlugin from "vite-plugin-bundle-obfuscator";

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const isProduction = mode === "production";

  return {
    plugins: [
      vue(),
      isProduction &&
        obfuscatorPlugin({
          options: {
            compact: true,
            controlFlowFlattening: true, // Modifie la structure du code pour perdre le fil logique
            controlFlowFlatteningThreshold: 0.75,
            deadCodeInjection: true, // Injecte du faux code inutile
            deadCodeInjectionThreshold: 0.4,
            identifierNamesGenerator: "hexadecimal", // Renomme les variables en hexadécimal
            renameGlobals: false, // Garder à false pour éviter de casser l'intégration Electron/Window
            stringArray: true,
            stringArrayEncoding: ["base64"], // Chiffre les chaînes de caractères
            stringArrayThreshold: 0.75,
            transformObjectKeys: true,
          },
        }),
    ].filter(Boolean),
    build: {
      sourcemap: false, // OBLIGATOIRE : Désactiver les sourcemaps pour ne pas exposer le code original
      outDir: "dist",
    },
    base: "./",
    server: {
      port: 5173,
    },
  };
});
