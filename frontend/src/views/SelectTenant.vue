<script setup>
import { ref, computed, onMounted } from "vue";

import { useRouter } from "vue-router";

import {
  getTenants,
  selectTenant,
  createTenant,
  getSelectedTenantId,
} from "../services/tenant";

const creating = ref(false);

const router = useRouter();

const tenants = ref([]);

const search = ref("");

const loading = ref(true);

const error = ref(null);

const currentTenant = ref(null);

onMounted(async () => {
  try {
    await loadTenants();

    currentTenant.value = getSelectedTenantId();
  } catch (e) {
    error.value = "Impossible de charger vos espaces";
  } finally {
    loading.value = false;
  }
});

async function loadTenants() {
  const data = await getTenants();

  tenants.value = data;
}

const canCreateTenant = computed(() => {
  const value = search.value.trim();

  if (!value) {
    return false;
  }

  return !tenants.value.some(
    (tenant) => tenant.name.toLowerCase() === value.toLowerCase()
  );
});

async function createNewTenant() {
  if (!search.value.trim()) {
    return;
  }

  try {
    creating.value = true;

    const response = await createTenant(search.value);

    const tenant = response.data;

    selectTenant(tenant);

    router.push("/");
  } catch (e) {
    error.value = "Impossible de créer l'espace";
  } finally {
    creating.value = false;
  }
}

const filteredTenants = computed(() => {
  const value = search.value.toLowerCase().trim();

  if (!value) return tenants.value;

  return tenants.value.filter(
    (tenant) =>
      tenant.name.toLowerCase().includes(value) ||
      tenant.schema_name.toLowerCase().includes(value)
  );
});

function setSelectedTenant(tenant) {
  selectTenant(tenant);

  currentTenant.value = tenant;

  router.push("/");
}
</script>
<template>
  <div class="page">
    <div class="tenant-card">
      <div class="header">
        <h1>Choisir un espace</h1>

        <p>Sélectionnez l'entreprise à laquelle vous souhaitez accéder.</p>
      </div>

      <div class="search-box">
        <span>🔎</span>

        <input v-model="search" placeholder="Rechercher une entreprise..." />
      </div>

      <div v-if="loading" class="state">Chargement des espaces...</div>

      <div v-else class="tenant-list">
        <div
          v-if="canCreateTenant"
          class="tenant-item create-item"
          @click="createNewTenant"
        >
          <div class="avatar create-avatar">+</div>

          <div class="tenant-info">
            <h3>Créer "{{ search }}"</h3>

            <p>Nouvel espace entreprise</p>

            <p v-if="error" class="error-message">
              {{ error }}
            </p>
          </div>

          <div class="arrow">→</div>
        </div>

        <div
          v-for="tenant in filteredTenants"
          :key="tenant.id"
          class="tenant-item"
          :class="currentTenant == tenant.id ? 'selected-tenant' : ''"
          @click="setSelectedTenant(tenant)"
        >
          <div class="avatar">
            {{ tenant.name.charAt(0).toUpperCase() }}
          </div>

          <div class="tenant-info">
            <h3>
              {{ tenant.name }}
            </h3>

            <p>
              {{ tenant.schema_name }}
            </p>
          </div>

          <div class="arrow">→</div>
        </div>

        <div
          v-if="filteredTenants.length === 0 && !canCreateTenant"
          class="state"
        >
          Aucun espace trouvé
        </div>
      </div>
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

.tenant-card {
  width: 100%;

  max-width: 450px;

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
  margin: 0;

  color: #6b7280;
}

.search-box {
  display: flex;

  align-items: center;

  gap: 10px;

  background: #f9fafb;

  border: 1px solid #d1d5db;

  border-radius: 10px;

  padding: 12px;

  margin-bottom: 20px;
}

.search-box input {
  width: 100%;

  border: none;

  background: transparent;

  font-size: 1rem;
}

.search-box input:focus {
  outline: none;
}

.tenant-list {
  display: flex;

  flex-direction: column;

  gap: 12px;
}

.tenant-item {
  display: flex;

  align-items: center;

  gap: 14px;

  padding: 15px;

  border: 1px solid #e5e7eb;

  border-radius: 14px;

  cursor: pointer;

  transition: 0.2s;
}

.tenant-item:hover {
  border-color: #111827;

  background: #f9fafb;

  transform: translateY(-2px);
}

.avatar {
  width: 45px;

  height: 45px;

  border-radius: 50%;

  background: #111827;

  color: white;

  display: flex;

  justify-content: center;

  align-items: center;

  font-size: 1.2rem;

  font-weight: bold;
}

.tenant-info {
  flex: 1;
}

.tenant-info h3 {
  margin: 0;

  font-size: 1rem;
}

.tenant-info p {
  margin: 4px 0 0;

  font-size: 0.85rem;

  color: #6b7280;
}

.arrow {
  font-size: 1.3rem;

  color: #9ca3af;
}

.state {
  text-align: center;

  padding: 20px;

  color: #6b7280;
}

.error {
  text-align: center;

  color: #dc2626;

  padding: 20px;
}

.change-btn {
  width: 100%;

  margin-top: 20px;

  padding: 12px;

  border: none;

  border-radius: 10px;

  background: #111827;

  color: white;

  cursor: pointer;
}

.change-btn:hover {
  opacity: 0.9;
}

.selected-tenant {
  border-color: #111827;
  background: #f3f4f6;
}

.error-message {
  color: #dc2626 !important;

  margin-top: 8px;

  font-size: 0.85rem;
}

.create-avatar {
  background: #09bb2d;
}
</style>
