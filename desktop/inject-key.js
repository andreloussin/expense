import fs from 'fs';
import path from 'path';

// 1. Lire manuellement le fichier .env local
const envPath = path.resolve('.env');
if (!fs.existsSync(envPath)) {
  console.error("Erreur : Fichier .env introuvable !");
  process.exit(1);
}

const envContent = fs.readFileSync(envPath, 'utf8');

// Extraction de la valeur de la clé publique
const match = envContent.match(/PUBLIC_KEY=["']([\s\S]*?)["']/);

if (!match) {
  console.error("Erreur : PUBLIC_KEY non trouvée dans le .env");
  process.exit(1);
}

const publicKey = match[1].replace(/\\n/g, '\n');

// 2. Écrire la clé dans un fichier JS temporaire dans votre dossier src
const configContent = `// Fichier généré automatiquement au build - Ne pas modifier\nexport const PUBLIC_KEY = \`${publicKey}\`;\n`;
fs.writeFileSync(path.join('src', 'license-config.js'), configContent);

console.log("✅ Clé publique injectée avec succès dans src/license-config.js");
