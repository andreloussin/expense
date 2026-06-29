import * as machineIdModule from "node-machine-id";
import crypto from "crypto";
import Store from "electron-store";
import { PUBLIC_KEY } from './license-config.js';

// On extrait la fonction synchrone depuis le module complet
const machineIdSync = machineIdModule.default
  ? machineIdModule.default.machineIdSync
  : machineIdModule.machineIdSync;

export function getMachineId() {
  // Récupération de l'ID natif unique de la machine
  const rawId = machineIdSync({ original: false });

  // Hachage SHA256 court et standardisé (8 caractères, majuscules, sans espaces)
  return crypto
    .createHash("sha256")
    .update(rawId)
    .digest("hex")
    .slice(0, 8)
    .toUpperCase();
}

/**
 * Valide mathématiquement la licence stockée sans aucun accès à Internet
 */
export function verifyLicenseOffline() {
  const licenseKey = getLicense();
  if (!licenseKey) return { valid: false, reason: "Aucune licence trouvée." };

  try {
    // 1. Décoder la structure Base64url globale
    const decodedRaw = Buffer.from(licenseKey, "base64url").toString("utf8");
    const { data, sig } = JSON.parse(decodedRaw);

    console.log("License Data : ", data);

    // 2. Reconstituer le message original signé par Django
    const dataString = JSON.stringify(data);

    // 3. Valider la signature avec la clé publique intégrée
    const verifier = crypto.createVerify("SHA256");
    verifier.update(dataString);
    verifier.end();

    const isSignatureValid = verifier.verify(PUBLIC_KEY, sig, "base64");
    if (!isSignatureValid) {
      return { valid: false, reason: "Clé de licence corrompue ou falsifiée." };
    }

    // 4. VERIFICATION DU HARDWARE BINDING (Lien avec la machine)
    const currentMachineId = getMachineId();
    if (data.mid !== currentMachineId) {
      return {
        valid: false,
        reason: "Cette licence est activée pour un autre ordinateur.",
      };
    }

    // 5. VERIFICATION DE LA DATE D'EXPIRATION
    const today = new Date();
    const expirationDate = new Date(data.exp);
    if (today > expirationDate) {
      return { valid: false, reason: "Votre abonnement a expiré." };
    }

    // Tout est OK
    return {
      valid: true,
      plan: data.plan,
      expires_at: data.exp,
      email: data.email,
    };
  } catch (error) {
    return { valid: false, reason: "Format de licence invalide." };
  }
}

const store = new Store({
  name: "license",
});

export function saveLicense(license) {
  store.set("license", license);
}

export function getLicense() {
  return store.get("license");
}

export function clearLicense() {
  store.delete("license");
}
