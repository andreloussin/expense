# Expenzo Desktop

Application desktop **Windows** basée sur :

* **Backend** : Django + API
* **Frontend** : Vue / Vite
* **Desktop** : Electron + Vite (géré via Electron Builder)

Le projet permet de construire une application Windows embarquant le frontend compilé, le backend packagé et l’exécutable final.

---

## Arborescence simplifiée

```text
expense/
├── backend/
├── frontend/
├── desktop/
│   ├── resources/
│   │   └── backend/     # Reçoit le binaire Django
│   ├── .vite/           # Reçoit le build du main process d'Electron
│   └── release/         # Reçoit l'exécutable final d'electron-builder
├── docs/
└── dev.py
```

---

## Prérequis

Avant de lancer le build, il faut disposer de :

* **Python** installé
* **Node.js** et **npm** installés
* Les dépendances backend et frontend déjà présentes dans le projet
* Un environnement compatible **Windows** pour générer l’exécutable `.exe`

---

## Structure du build

Le build suit cet ordre :

1. Build du **frontend Vue**
2. Build du **backend Django**
3. Copie de l'exécutable Django dans `desktop/resources/backend/`
4. Build et obfuscation d'**Electron (Vite)**
5. Génération de l'installateur Windows (NSIS) via `electron-builder`

---

## 1. Build du backend Django

Se placer dans le dossier backend :

```bash
cd backend
```

Activer l’environnement virtuel puis installer les dépendances :

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

Obfusquer le code du backend avec pyarmor (*les fichiers obfusqués seront placés dans `.pyarmor_dist/`*) :

```bash
pyarmor gen -O .pyarmor_dist server.py accounts config expenses tenants
```

Générer l’exécutable du backend avec PyInstaller :

```bash
pyinstaller expense-server.spec
```

### Fichier généré

Le backend compilé se trouve ici :

```text
backend/dist/expense-server.exe
```

---

## 2. Build du frontend Vue

Se placer dans le dossier frontend :

```bash
cd frontend
```

Installer les dépendances :

```bash
npm install
```

Compiler le frontend en mode production :

```bash
npm run build
```

### Fichiers générés

Le build frontend est disponible dans :

```text
frontend/dist/
```

---

## 3. Copier le backend vers Electron

L’application Electron utilise le dossier `resources/` pour embarquer le serveur.

### Copier le binaire Django

Copier le fichier :

```text
backend/dist/expense-server.exe
```

vers :

```text
desktop/resources/backend/
```

*(Note : Lors du build final, `electron-builder` utilise la règle `extraResources` pour inclure automatiquement ce dossier dans l'application).*

---

## 4. Build de l’application Electron

Se placer dans le dossier desktop :

```bash
cd desktop
```

Installer les dépendances :

```bash
npm install
```

### Commandes disponibles

* **Lancer l'application en développement** :

```bash
npm run dev
```

Cette commande démarre simultanément :

* Le serveur de développement Vite.
* Electron avec rechargement automatique via Electronmon.

Le mode développement utilise directement les fichiers sources Electron :

```text
src/
├── main.js
└── preload.js
```

ainsi que les ressources locales :

```text
resources/
├── frontend/
└── backend/
```

---

* **Générer l'installateur Windows de production** :

```bash
npm run build
```

Cette commande exécute automatiquement :

1. L'obfuscation du code Electron :

```bash
npm run obfuscate-electron
```

Le code :

```text
src/
├── main.js
└── preload.js
```

est transformé en :

```text
electron-dist/
├── main.js
└── preload.js
```

2. La génération de l'application Windows via Electron Builder.

Electron Builder assemble ensuite :

```text
electron-dist/
└──  Code Electron obfusqué

resources/frontend/
└──  Frontend Vue déjà compilé et obfusqué

resources/backend/
└──  Backend Django compilé et protégé
```

 pour produire l'installateur final.

---

## 5. Fichiers générés par Electron

Les fichiers de sortie sont générés dans :

```text
desktop/release/
```

Vous y trouverez notamment :

```text
desktop/release/
├── Expenzo Setup x.x.x.exe
├── latest.yml
└── win-unpacked/
```

### Caractéristiques de l'installateur Expenzo

* Assistant d'installation Windows (NSIS).
* Choix du répertoire d'installation.
* Création d'un raccourci sur le Bureau.
* Création d'un raccourci dans le Menu Démarrer.
* Installation simplifiée pour l'utilisateur final.

---

## 6. Build complet en une commande

Depuis la racine du projet :

```bash
bash build-app.sh
```

Cette commande exécute généralement :

1. Nettoyage des anciens fichiers générés :
    - `backend/build/`
    - `backend/dist/`
    - `backend/.pyarmor_dist/`
    - `frontend/dist/`
    - `desktop/electron-dist/`
    - `desktop/release/`
2. `npm run build` dans `frontend/`
3. Copie de `frontend/dist/` vers `desktop/resources/frontend/`
4. Obfuscation du backend avec **PyArmor** dans `backend/` :
    ```bash
    pyarmor gen -O .pyarmor_dist server.py accounts config expenses tenants
    pyinstaller expense-server.spec dans backend/
    ```
5. Copie de `backend/dist/` vers `desktop/resources/backend/`
6. `npm run package` dans `desktop/`
7. `npm run dist` dans `desktop/`

---

## 7. Nettoyage avant un build propre

Si nécessaire, supprimez les dossiers temporaires avant de relancer un build :

### Backend
```text
backend/build/
backend/dist/
backend/.pyarmor_dist/
```

### Frontend
```text
frontend/dist/
```

### Electron
```text
desktop/electron-dist/
desktop/release/
```

---

## 8. Résumé rapide

| Étape          | Commande                          | Résultat de sortie                     |
| -------------- | --------------------------------- | -------------------------------------- |
| Build backend  | `pyarmor gen -O .pyarmor_dist server.py accounts config expenses tenants` et `pyinstaller expense-server.spec` | `backend/dist/expense-server.exe`      |
| Build frontend | `npm run build`                   | `frontend/dist/`                       |
| Build Electron | `npm run dist`                    | `desktop/release/Expenzo Setup...exe`  |
| Build complet  | `bash build-app.sh`    | Package d'installation Windows final   |

---

## 9. Points importants

* **Sécurité** : Le code JavaScript principal de l'application est protégé lors de la compilation grâce à `vite-plugin-bundle-obfuscator`.
* **Ressources** : Le binaire Django doit obligatoirement être présent dans `desktop/resources/backend/` avant de lancer le `npm run dist`.
* **Identifiant Unique** : L'application est enregistrée sous l'AppId `com.loussin.expenzo`.
