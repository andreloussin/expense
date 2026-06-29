import { createRouter, createWebHashHistory } from "vue-router";

import Login from "./views/Login.vue";
import Register from "./views/Register.vue";
import { isAuthenticated } from "./services/auth.js";
import Home from "./views/Home.vue";
import SelectTenant from "./views/SelectTenant.vue";
import { isTenantSelected } from "./services/tenant.js";

const routes = [
  {
    path: "/login",
    component: Login,
  },

  {
    path: "/register",
    component: Register,
  },

  {
    path: "/",
    component: Home,
    beforeEnter: () => {
      if (!isAuthenticated()) {
        return "/login";
      }

      if (!isTenantSelected()) {
        return "/select-tenant";
      }
    },
  },

  {
    path: "/select-tenant",
    component: SelectTenant,
    beforeEnter: () => {
      if (!isAuthenticated()) {
        return "/login";
      }
    },
  },
];

export default createRouter({
  history: createWebHashHistory(),

  routes,
});
