<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'

const categories = ref([])
const expenses = ref([])

const categoryForm = ref({ name: '' })
const expenseForm = ref({
  title: '',
  amount: '',
  spent_on: new Date().toISOString().slice(0, 10),
  category: '',
  note: '',
})

const loading = ref(false)
const errorMessage = ref('')

const totalExpenses = computed(() =>
  expenses.value.reduce((sum, item) => sum + Number(item.amount), 0).toFixed(2)
)

async function fetchCategories() {
  const { data } = await axios.get(`${API_BASE}/categories/`)
  categories.value = data
}

async function fetchExpenses() {
  const { data } = await axios.get(`${API_BASE}/expenses/`)
  expenses.value = data
}

async function loadAll() {
  loading.value = true
  errorMessage.value = ''
  try {
    await Promise.all([fetchCategories(), fetchExpenses()])
  } catch (error) {
    errorMessage.value = "Impossible de charger les données."
    console.error(error)
  } finally {
    loading.value = false
  }
}

async function addCategory() {
  if (!categoryForm.value.name.trim()) return

  try {
    await axios.post(`${API_BASE}/categories/`, categoryForm.value)
    categoryForm.value.name = ''
    await fetchCategories()
  } catch (error) {
    errorMessage.value = "Impossible d'ajouter la catégorie."
    console.error(error)
  }
}

async function addExpense() {
  if (!expenseForm.value.title.trim() || !expenseForm.value.amount) return

  try {
    await axios.post(`${API_BASE}/expenses/`, {
      ...expenseForm.value,
      category: expenseForm.value.category || null,
    })

    expenseForm.value.title = ''
    expenseForm.value.amount = ''
    expenseForm.value.note = ''
    expenseForm.value.category = ''
    expenseForm.value.spent_on = new Date().toISOString().slice(0, 10)

    await fetchExpenses()
  } catch (error) {
    errorMessage.value = "Impossible d'ajouter la dépense."
    console.error(error)
  }
}

async function deleteExpense(id) {
  try {
    await axios.delete(`${API_BASE}/expenses/${id}/`)
    await fetchExpenses()
  } catch (error) {
    errorMessage.value = "Impossible de supprimer la dépense."
    console.error(error)
  }
}

onMounted(loadAll)
</script>

<template>
  <div class="app">
    <header class="hero">
      <h1>Mini Suivi de Dépenses</h1>
      <p>Application Django + Vue + PostgreSQL, prête pour Electron plus tard.</p>
      <div class="stats">
        <div class="card">
          <strong>{{ expenses.length }}</strong>
          <span>Dépenses</span>
        </div>
        <div class="card">
          <strong>{{ categories.length }}</strong>
          <span>Catégories</span>
        </div>
        <div class="card">
          <strong>{{ totalExpenses }} FCFA</strong>
          <span>Total</span>
        </div>
      </div>
    </header>

    <p v-if="loading">Chargement...</p>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

    <section class="grid">
      <div class="panel">
        <h2>Ajouter une catégorie</h2>
        <form @submit.prevent="addCategory" class="form">
          <input v-model="categoryForm.name" placeholder="Ex: Transport" />
          <button type="submit">Ajouter</button>
        </form>
      </div>

      <div class="panel">
        <h2>Ajouter une dépense</h2>
        <form @submit.prevent="addExpense" class="form">
          <input v-model="expenseForm.title" placeholder="Ex: Essence" />
          <input v-model="expenseForm.amount" type="number" step="0.01" placeholder="Montant" />
          <input v-model="expenseForm.spent_on" type="date" />
          <select v-model="expenseForm.category">
            <option value="">Aucune catégorie</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
          <textarea v-model="expenseForm.note" placeholder="Note"></textarea>
          <button type="submit">Ajouter</button>
        </form>
      </div>
    </section>

    <section class="panel">
      <h2>Liste des dépenses</h2>
      <div v-if="expenses.length === 0">Aucune dépense pour le moment.</div>

      <div v-for="expense in expenses" :key="expense.id" class="expense">
        <div>
          <h3>{{ expense.title }}</h3>
          <p>
            {{ expense.amount }} FCFA
            <span v-if="expense.category_name">· {{ expense.category_name }}</span>
            · {{ expense.spent_on }}
          </p>
          <small v-if="expense.note">{{ expense.note }}</small>
        </div>

        <button class="danger" @click="deleteExpense(expense.id)">Supprimer</button>
      </div>
    </section>
  </div>
</template>

<style scoped>
:global(*) {
  box-sizing: border-box;
  font-family: Arial, sans-serif;
}

:global(body) {
  margin: 0;
  background: #f5f7fb;
  color: #1f2937;
}

.app {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px;
}

.hero {
  margin-bottom: 24px;
}

.hero h1 {
  margin: 0 0 8px;
  font-size: 2rem;
}

.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 16px;
}

.card,
.panel {
  background: white;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.06);
}

.card strong {
  display: block;
  font-size: 1.4rem;
}

.card span {
  color: #6b7280;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.form {
  display: grid;
  gap: 10px;
}

input,
select,
textarea,
button {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid #d1d5db;
  font-size: 1rem;
}

button {
  cursor: pointer;
  background: #111827;
  color: white;
  border: none;
}

button.danger {
  background: #dc2626;
}

.expense {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-top: 1px solid #e5e7eb;
}

.error {
  color: #dc2626;
}

@media (max-width: 800px) {
  .grid,
  .stats {
    grid-template-columns: 1fr;
  }

  .expense {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>