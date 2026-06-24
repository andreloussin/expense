import axios from "axios";
import { getAccessToken, logout } from "./auth";
import router from "../router";
import { getSelectedTenantId } from "./tenant";

const api = axios.create({
  baseURL: window.config?.API_URL ?? import.meta.env.VITE_API_BASE_URL,
});

api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    const tenantId = getSelectedTenantId();

    if (tenantId) {
      config.headers["X-Tenant-Id"] = tenantId;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,

  (error) => {
    if (error.response && error.response.status === 401) {
      logout();

      router.push("/login");
    }

    return Promise.reject(error);
  }
);

export default api;
