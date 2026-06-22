# Guide d'Obfuscation et de Sécurisation pour une Application Vue.js + Electron

Ce document explique comment obfusquer le code d'une application Vue.js (Vite) et l'intégrer de manière sécurisée dans un exécutable Electron afin de protéger votre propriété intellectuelle.

---

## 🎯 Objectif de la configuration

1. **Obfusquer le code Vue (Frontend) :** Rendre le code JavaScript du dossier `dist/` illisible.
2. **Masquer le code Electron (Backend/Main process) :** Compiler les scripts principaux d'Electron.
3. **Encapsuler l'application :** Utiliser le format ASAR pour éviter l'accès direct aux fichiers sources par l'utilisateur.

---

## 🛠️ Étape 1 : Obfusquer le code Vue.js (avec Vite)

Si votre application Vue utilise **Vite**, nous allons configurer un plugin pour appliquer une obfuscation agressive lors de la compilation de production.

### 1. Installation des dépendances

Installez le plugin d'obfuscation pour Vite :

```bash
npm install vite-plugin-bundle-obfuscator --save-dev
```

### 2. Configuration de `vite.config.js`

Modifiez votre fichier de configuration pour activer l'obfuscation uniquement lors du build de production :

```javascript
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import obfuscatorPlugin from "vite-plugin-bundle-obfuscator";

export default defineConfig(({ mode }) => {
  const isProduction = mode === "production";

  return {
    plugins: [
      vue(),
      // L'obfuscation est activée UNIQUEMENT en production pour ne pas ralentir le développement
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
    ].filter(Boolean), // Filtre les valeurs falsy (comme false en mode dev)
    build: {
      sourcemap: false, // OBLIGATOIRE : Désactiver les sourcemaps pour ne pas exposer le code original
      outDir: "dist",
    },
  };
});
```

---

## 🔒 Étape 2 : Sécuriser et compiler le code Electron (Main & Preload)

Le processus principal d'Electron (`main.js` ou `index.js`) et le script `preload.js` doivent également être protégés, car ils ont un accès complet au système de l'utilisateur.

### 1. Utiliser un Bundler pour Electron

Au lieu de copier vos fichiers Electron bruts, utilisez **Vite**, **Webpack** ou **esbuild** pour compiler et minifier le code d'Electron en un seul fichier compact avant l'empaquetage.
Si vous utilisez des frameworks comme `electron-vite`, cette étape est gérée automatiquement de manière optimisée.

### 2. Désactiver les Outils de Développement (DevTools) en Production

Dans votre fichier principal Electron (ex: `main.js`), assurez-vous de bloquer l'accès aux DevTools et aux raccourcis clavier associés pour empêcher l'utilisateur d'inspecter le code Vue en cours d'exécution.

```javascript
const { app, BrowserWindow, globalShortcut } = require("electron");

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false, // Recommandé pour la sécurité
      contextIsolation: true, // Recommandé pour la sécurité
      preload: path.join(__dirname, "preload.js"),
    },
  });

  win.loadFile("dist/index.html");

  // Bloquer l'ouverture des DevTools via le code
  win.webContents.on("devtools-opened", () => {
    win.webContents.closeDevTools();
  });
}

app.whenReady().then(() => {
  createWindow();

  // Bloquer les raccourcis clavier courants des DevTools (F12, Ctrl+Shift+I, Cmd+Orf+I)
  globalShortcut.register("CommandOrControl+Shift+I", () => {
    return false; // Ne fait rien
  });
  globalShortcut.register("F12", () => {
    return false;
  });
});

app.on("will-quit", () => {
  globalShortcut.unregisterAll();
});
```

---

## 📦 Étape 3 : Empaqueter l'application avec ASAR (Chiffrement de base)

Pour distribuer votre application, utilisez **electron-builder**. Par défaut, il regroupe vos fichiers obfusqués dans une archive `.asar`. Sans cela, vos fichiers seraient visibles d'un simple clic droit dans le dossier d'installation.

### 1. Configuration de `electron-builder.json` (ou `package.json`)

Assurez-vous que l'option `asar` est bien définie sur `true`.

```json
{
  "appId": "com.monentreprise.monappvue",
  "productName": "MonAppObfusquee",
  "directories": {
    "output": "dist_electron"
  },
  "files": [
    "dist/**/*", // Votre code Vue obfusqué
    "main.js", // Votre code Electron minifié
    "preload.js"
  ],
  "asar": true, // Compresse et masque l'arborescence des fichiers
  "mac": { "target": "dmg" },
  "win": { "target": "nsis" },
  "linux": { "target": "AppImage" }
}
```

---

## 🚀 Flux de déploiement (Workflow)

Pour générer votre application finale, vous devez exécuter les commandes dans l'ordre suivant. Configurez vos scripts dans le fichier `package.json` :

```json
"scripts": {
  "dev": "vite",
  "build:vue": "vite build --mode production",
  "build:electron": "electron-builder"
}
```

### Commande finale pour générer l'application sécurisée :

```bash
npm run build:vue && npm run build:electron
```

---

## 🚨 Limites importantes à connaître

- **L'obfuscation n'est pas un chiffrement inviolable :** Un ingénieur très déterminé avec des outils de reverse-engineering avancés pourra finir par comprendre des parties du code. L'obfuscation sert à **décourager** 99% des tentatives.
- **Ne stockez JAMAIS de clés secrètes :** Les clés privées d'API (Firebase, Stripe, AWS) intégrées dans le code Vue ou Electron peuvent être extraites de la mémoire de l'application. Utilisez toujours un serveur intermédiaire (Backend) pour effectuer les requêtes sensibles.
