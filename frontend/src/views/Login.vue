<script setup>
import { ref } from "vue";
import { login } from "../services/auth";
import { useRouter } from "vue-router";

const username = ref("");
const password = ref("");
const error = ref("");

const router = useRouter();

async function submit() {
  error.value = "";

  try {
    await login(username.value, password.value);

    router.push("/");
  } catch (e) {
    error.value = "Nom d'utilisateur ou mot de passe incorrect.";
  }
}
</script>

<template>
  <div class="page">
    <div class="login-card">
      <div class="header">
        <h1>Connexion</h1>
        <p>Connectez-vous pour accéder à vos dépenses.</p>
      </div>

      <form @submit.prevent="submit" class="form">
        <div class="field">
          <label>Nom utilisateur</label>
          <input v-model="username" placeholder="Votre username" />
        </div>

        <div class="field">
          <label>Mot de passe</label>
          <input
            v-model="password"
            type="password"
            placeholder="Votre mot de passe"
          />
        </div>

        <button type="submit">Se connecter</button>

        <p v-if="error" class="error">
          {{ error }}
        </p>
      </form>

      <p class="register">
        Pas encore de compte ?
        <router-link to="/register"> Créer un compte </router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f7fb;
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: white;
  padding: 32px;
  border-radius: 18px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
}

.header {
  text-align: center;
  margin-bottom: 25px;
}

.header h1 {
  margin: 0 0 8px;
  font-size: 2rem;
}

.header p {
  color: #6b7280;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

label {
  font-size: 0.9rem;
  color: #374151;
}

input {
  padding: 12px;
  border-radius: 10px;
  border: 1px solid #d1d5db;
  font-size: 1rem;
}

input:focus {
  outline: none;
  border-color: #111827;
}

button {
  margin-top: 10px;
  padding: 12px;
  border-radius: 10px;
  border: none;
  background: #111827;
  color: white;
  font-size: 1rem;
  cursor: pointer;
}

button:hover {
  opacity: 0.9;
}

.error {
  color: #dc2626;
  text-align: center;
}

.register {
  margin-top: 20px;
  text-align: center;
  color: #6b7280;
}

.register a {
  color: #111827;
  font-weight: bold;
  text-decoration: none;
}
</style>
