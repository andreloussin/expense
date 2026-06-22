import { createRouter, createWebHistory } from "vue-router";

import Login from "./views/Login.vue";
import Register from "./views/Register.vue";
import App from "./App.vue";
import { isAuthenticated } from "./services/auth.js";
import Home from "./views/Home.vue";

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
    },
  },
];

export default createRouter({
  history: createWebHistory(),

  routes,
});
