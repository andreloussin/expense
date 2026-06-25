# Expense Desktop

Application desktop **Windows** basée sur :

- **Backend** : Django + API
- **Frontend** : Vue / Vite
- **Desktop** : Electron

Le projet permet de construire une application Windows embarquant le frontend compilé, le backend packagé et l’exécutable Electron final.

---

## Arborescence simplifiée

```text
expense/
├── backend/
├── frontend/
├── desktop/
├── docs/
└── dev.py
```

---

## Prérequis

Avant de lancer le build, il faut disposer de :

- **Python** installé
- **Node.js** et **npm** installés
- Les dépendances backend et frontend déjà présentes dans le projet
- Un environnement compatible **Windows** pour générer l’exécutable `.exe`

---

## Structure du build

Le build suit cet ordre :

1. Build du **frontend Vue**
2. Build du **backend Django**
3. Copie des fichiers générés dans `desktop/resources/`
4. Package de l’application **Electron**
5. Génération de l’installeur Windows avec **electron-builder**

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

Obfusquer le code du backend avec PyArmor. Les fichiers obfusqués seront placés dans `.pyarmor_dist/` :

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

Compiler le frontend en mode production. Le code sera automatiquement obfusqué :

```bash
npm run build
```

### Fichiers générés

Le build frontend est disponible dans :

```text
frontend/dist/
```

Contenu typique :

```text
frontend/dist/
├── index.html
└── assets/
```

---

## 3. Copier les fichiers vers Electron

L’application Electron utilise le dossier :

```text
desktop/resources/
```

La structure attendue est :

```text
desktop/resources/
├── backend/
│   └── expense-server.exe
└── frontend/
    ├── index.html
    └── assets/
```

### Copier le backend

Copier :

```text
backend/dist/expense-server.exe
```

vers :

```text
desktop/resources/backend/
```

### Copier le frontend

Copier tout le contenu de :

```text
frontend/dist/
```

vers :

```text
desktop/resources/frontend/
```

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

Tester l’application en local :

```bash
npm start
```

Cette commande sert uniquement au développement et au test local.

### Préparer le package Electron

Avant de générer l’installeur, il faut créer le package Electron :

```bash
npm run package
```

Cette commande génère les fichiers de build Electron dans :

```text
desktop/.vite/
```

### Générer l’installeur Windows

```bash
npm run dist
```

Cette commande utilise **electron-builder** pour générer l’installeur final Windows.

---

## 5. Fichiers générés par Electron Builder

Les fichiers de sortie se trouvent généralement dans :

```text
desktop/release/
```

Selon la configuration d’Electron Builder, on peut y trouver :

```text
desktop/release/
├── win-unpacked/
└── Expenzo Setup 1.0.0.exe
```

Le fichier principal à distribuer est souvent :

```text
desktop/release/Expenzo Setup 1.0.0.exe
```

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
    - `desktop/.vite/`
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

Si nécessaire, supprimer les dossiers générés puis relancer le build :

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
desktop/.vite/
desktop/release/
```

---

## 8. Résumé rapide

| Étape | Commande | Résultat |
|---|---|---|
| Build backend | `pyinstaller expense-server.spec` | `backend/dist/expense-server.exe` |
| Build frontend | `npm run build` | `frontend/dist/` |
| Test Electron | `npm start` | Application locale |
| Package Electron | `npm run package` | `desktop/.vite/` |
| Build installateur | `npm run dist` | `desktop/release/` |
| Build complet | `python dev.py electron-build` | Installeur Windows final |

---

## 9. Points importants

- Le backend doit être buildé avant Electron.
- Le frontend doit être compilé avant la copie dans `desktop/resources/frontend/`.
- Le contenu de `desktop/resources/` est intégré dans l’application Electron finale.
- `electron-builder` utilise les fichiers déjà préparés par le package Electron.
- Avant un `npm run dist`, il faut s’assurer que le package Electron a bien été généré avec `npm run package`.
- Après modification de :
  - `vite.main.config.mjs`
  - `vite.preload.config.mjs`
  - la configuration d’obfuscation
  - les fichiers Electron principaux

  il faut refaire le package puis l’installeur.

---

## 10. Fichier de référence

Commande principale recommandée pour générer l’application Windows :

```bash
python dev.py electron-build
```