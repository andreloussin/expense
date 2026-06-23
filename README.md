# Expense Desktop

Application desktop **Windows** basée sur :

* **Backend** : Django + API
* **Frontend** : Vue / Vite
* **Desktop** : Electron

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

* **Python** installé
* **Node.js** et **npm** installés
* Les dépendances backend et frontend déjà présentes dans le projet
* Un environnement compatible **Windows** pour générer l’exécutable `.exe`

---

## Structure du build

Le build suit cet ordre :

1. Build du **frontend Vue**
2. Build du **backend Django**
3. Copie des fichiers générés dans `desktop/resources/`
4. Build de **Electron**
5. Génération de l’exécutable Windows

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

Générer l’exécutable Windows :

```bash
npm run make
```

---

## 5. Fichiers générés par Electron

Les fichiers de sortie se trouvent généralement dans :

```text
desktop/out/
```

Selon la configuration d’Electron Forge, on peut y trouver :

```text
desktop/out/
├── expense-desktop-win32-x64/
└── make/
    └── squirrel.windows/
        └── ExpenseDesktopSetup.exe
```

Le fichier principal à distribuer est souvent :

```text
desktop/out/make/**/ExpenseDesktopSetup.exe
```

---

## 6. Build complet en une commande

Depuis la racine du projet :

```bash
python dev.py electron-build
```

Cette commande exécute généralement :

1. `npm run build` dans `frontend/`
2. copie de `frontend/dist/` vers `desktop/resources/frontend/`
3. `pyinstaller expense-server.spec` dans `backend/`
4. copie de `backend/dist/expense-server.exe` vers `desktop/resources/backend/`
5. `npm run make` dans `desktop/`

---

## 7. Nettoyage avant un build propre

Si nécessaire, supprimer les dossiers générés puis relancer le build :

### Backend

```text
backend/build/
backend/dist/
```

### Frontend

```text
frontend/dist/
```

### Electron

```text
desktop/out/
```

---

## 8. Résumé rapide

| Étape          | Commande                          | Résultat                          |
| -------------- | --------------------------------- | --------------------------------- |
| Build backend  | `pyinstaller expense-server.spec` | `backend/dist/expense-server.exe` |
| Build frontend | `npm run build`                   | `frontend/dist/`                  |
| Build Electron | `npm run make`                    | Exécutable Windows                |
| Build complet  | `python dev.py electron-build`    | Package final                     |

---

## 9. Points importants

* Le backend doit être buildé avant Electron.
* Le frontend doit être compilé avant la copie dans `desktop/resources/frontend/`.
* Le contenu de `desktop/resources/` est intégré dans l’application Electron finale.
* L’exécutable final est généré dans `desktop/out/`.

---

## 10. Fichier de référence

Commande principale recommandée pour générer l’application Windows :

```bash
python dev.py electron-build
```
