import api from "./api";

async function getTenants() {
  const response = await api.get("/tenants/");

  return response.data;
}

async function getTenant(id) {
  const response = await api.get(`/tenants/${id}/`);

  return response.data;
}

function selectTenant(tenant) {
  localStorage.setItem("tenant_id", tenant.id);
  localStorage.setItem("tenant_name", tenant.name);
}
function getSelectedTenantId() {
  return localStorage.getItem("tenant_id");
}

function clearTenant() {
  localStorage.removeItem("tenant_id");
  localStorage.removeItem("tenant_name");
}

function getSelectedTenantName() {
  return localStorage.getItem("tenant_name");
}

function isTenantSelected() {
  return !!localStorage.getItem("tenant_id");
}

function createTenant(name) {
  return api.post("/tenants/", { name });
}

export {
  getTenants,
  getTenant,
  selectTenant,
  getSelectedTenantId,
  getSelectedTenantName,
  clearTenant,
  isTenantSelected,
  createTenant
};
