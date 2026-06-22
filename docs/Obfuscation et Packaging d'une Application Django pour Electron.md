# Guide Complet : Obfuscation et Packaging d'une Application Django pour Electron

Ce guide détaille le processus de sécurisation d'un backend Django destiné à être embarqué comme processus enfant (_child process_) dans une application de bureau Electron.

Pour contrer le fait que PyInstaller extrait par défaut ses fichiers dans un dossier temporaire visible (le dossier `_MEIxxxxxx`), nous appliquons une **double barrière de protection** :

1. **L'obfuscation stricte via PyArmor** (chiffrement et transformation du code en bytecode opaque).
2. **Le packaging monolithique via PyInstaller** (`--onefile`) qui ne contiendra que les fichiers chiffrés et exclura tout code source `.py` en clair du dossier d'extraction temporaire.

---

## Architecture du Projet Final

```text
mon-app-desktop/
├── electron/                  # Code de l'application Electron
│   ├── main.js                # Lanceur du processus Django
│   └── package.json           # Configuration Electron
├── django_app/                # Votre projet Django source (à ne jamais distribuer)
│   ├── manage.py
│   └── core/
└── dist_bin/                  # Dossier de sortie final
    └── backend_django.exe     # L'unique binaire obfusqué à inclure dans Electron
```

---

## Étape 1 : Préparation du Script d'Entrée (`prod_server.py`)

Au lieu d'utiliser `manage.py runserver` (lent et lourd), nous créons un script d'entrée épuré utilisant un serveur WSGI de production comme **Waitress** (excellent sur Windows) ou **CherryPy**.

Créez un fichier nommé `prod_server.py` à la racine de votre projet Django :

```python
import os
import sys
from waitress import serve
from django.core.wsgi import get_wsgi_application

def start_server():
    # Configuration des variables d'environnement Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

    # Récupération dynamique du port (passé par Electron)
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

    print(f"Démarrage du backend Django obfusqué sur le port {port}...")

    # Chargement de l'application WSGI Django
    application = get_wsgi_application()

    # Lancement du serveur de production
    serve(application, host='127.0.0.1', port=port, threads=4)

if __name__ == '__main__':
    start_server()
```

---

## Étape 2 : Obfuscation avec PyArmor (Génération du code opaque)

PyArmor va compiler vos scripts Python en bytecode et y injecter une extension binaire de protection empêchant la décompilation standard.

1. **Installez PyArmor** :

   ```bash
   pip install pyarmor
   ```

2. **Générez l'application obfusquée** :
   Sélectionnez votre dossier Django ainsi que le script d'entrée. Nous demandons à PyArmor de tout placer dans un répertoire intermédiaire nommé `dist_obfuscated` :
   ```bash
   pyarmor gen -O dist_obfuscated --pack run-at-once prod_server.py django_app/
   ```
   _Note : L'argument `--pack run-at-once` configure PyArmor de manière optimale pour fonctionner main dans la main avec un bundler comme PyInstaller._

À ce stade, si vous inspectez le dossier `dist_obfuscated`, tous les fichiers `.py` ont été remplacés par des structures de code chiffrées impossibles à lire, accompagnées d'un runtime binaire PyArmor.

---

## Étape 3 : Compilation Monolithique avec PyInstaller (`--onefile`)

C'est ici que l'on gère la problématique des fichiers temporaires `_MEIxxxxxx`.

Lorsque l'exécutable PyInstaller s'exécute, il décompresse ses dépendances dans le dossier `_MEIxxxxxx` de l'utilisateur. En couplant PyInstaller avec les fichiers **déjà obfusqués par PyArmor**, le dossier temporaire `_MEIxxxxxx` ne contiendra **que le bytecode chiffré** et l'interpréteur Python standard. Aucun pirate ne pourra reconstruire votre logique métier à partir de ce dossier.

1. **Installez PyInstaller** :

   ```bash
   pip install pyinstaller
   ```

2. **Générez le binaire unique** en ciblant le script d'entrée présent dans le dossier obfusqué :
   ```bash
   pyinstaller --onefile \
               --name="backend_django" \
               --distpath="./dist_bin" \
               --noconfirm \
               --clean \
               dist_obfuscated/prod_server.py
   ```

### Optionnel : Gestion des fichiers non-Python (Static, Templates, DB)

Si vos fichiers HTML/CSS ou votre base de données SQLite initiale doivent être embarqués, il ne faut pas les masquer via PyArmor (qui ne traite que le Python), mais les inclure dans le binaire via PyInstaller grâce au drapeau `--add-data` :

```bash
--add-data "django_app/static;django_app/static"
```

_Astuce de sécurité :_ Pour minimiser au maximum l'exposition dans le dossier `_MEI`, configurez votre application pour que l'interface Electron lise les assets statiques directement (via des fichiers compilés dans le build d'Electron) plutôt que de laisser Django les servir.

---

## Étape 4 : Intégration et Lancement Opaque dans Electron

Une fois le fichier `dist_bin/backend_django.exe` (ou binaire sans extension sur macOS/Linux) généré, déplacez-le dans un sous-dossier de votre application Electron (par exemple `electron/bin/`).

Voici comment configurer `main.js` pour exécuter le binaire en tâche de fond de manière totalement transparente pour l'utilisateur :

```javascript
const { app, BrowserWindow } = require("electron");
const path = require("path");
const { spawn } = require("child_process");

let mainWindow;
let djangoProcess = null;

function startObfuscatedBackend() {
  // Détermination du chemin vers le binaire obfusqué
  const isPackaged = app.isPackaged;
  const backendPath = isPackaged
    ? path.join(process.resourcesPath, "bin", "backend_django.exe") // En production
    : path.join(__dirname, "bin", "backend_django.exe"); // En développement

  const port = "8000";

  // Lancement du binaire en arrière-plan sans ouvrir de fenêtre d'invite de commande (cmd)
  djangoProcess = spawn(backendPath, [port], {
    windowsHide: true, // Masque complètement la fenêtre du terminal sur Windows
    shell: false,
  });

  djangoProcess.stdout.on("data", (data) => {
    console.log(`[Django]: ${data}`);
  });

  djangoProcess.stderr.on("data", (data) => {
    console.error(`[Django Error]: ${data}`);
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  // Temporisation légère pour laisser au serveur obfusqué le temps d'initialiser la boucle WSGI
  setTimeout(() => {
    mainWindow.loadURL("http://127.0.0.1:8000");
  }, 1200);

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

app.on("ready", () => {
  startObfuscatedBackend();
  createWindow();
});

// Sécurité : Tuer impérativement le processus Django dès qu'Electron se ferme
app.on("will-quit", () => {
  if (djangoProcess) {
    djangoProcess.kill();
  }
});
```

---

## Synthèse des Verrous de Sécurité Appliqués

| Risque                                 | Mécanisme de Protection                                          | Statut dans le dossier `_MEI`              |
| :------------------------------------- | :--------------------------------------------------------------- | :----------------------------------------- |
| **Lecture des fichiers `.py`**         | PyArmor transforme le code source en un flux binaire obfusqué.   | Aucun fichier `.py` lisible n'est extrait. |
| **Décompilation du Bytecode (`.pyc`)** | Chiffrement dynamique au runtime par la clé PyArmor.             | Les outils comme `uncompyle6` échouent.    |
| **Rétro-ingénierie des variables**     | `windowsHide: true` empêche l'inspection des arguments systèmes. | Invisible pour l'utilisateur standard.     |
