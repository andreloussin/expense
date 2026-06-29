import fs from "fs";
import path from "path";

let publicKey = process.env.LICENSE_PUBLIC_KEY;

// 1. Si la variable n'est pas dans le système, on tente de lire le .env local (Dev local)
if (!publicKey) {
  const envPath = path.resolve(".env");

  if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, "utf8");
    const match = envContent.match(/LICENSE_PUBLIC_KEY=["']([\s\S]*?)["']/);
    if (match) {
      publicKey = match[1].replace(/\\n/g, "\n");
    }
  }
}

// 2. Blocage si la variable reste introuvable partout
if (!publicKey) {
  console.error(
    "Erreur : LICENSE_PUBLIC_KEY introuvable dans process.env ET dans le fichier .env !"
  );
  process.exit(1);
}

// Nettoyage des sauts de ligne si la clé provient d'une chaîne brute avec des "\n" textuels
publicKey = publicKey.replace(/\\n/g, "\n");

// 3. Écrire la clé dans le fichier JS temporaire
const configContent = `// Fichier généré automatiquement au build - Ne pas modifier\nexport const LICENSE_PUBLIC_KEY = \`${publicKey}\`;\n`;
fs.writeFileSync(path.join("src", "license-config.js"), configContent);

console.log("✅ Clé publique injectée avec succès dans src/license-config.js");
