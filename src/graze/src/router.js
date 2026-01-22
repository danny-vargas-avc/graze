import { createRouter, createWebHistory } from 'vue-router'
import LandingView from './views/LandingView.vue'
import SearchView from './views/SearchView.vue'

const routes = [
  {
    path: '/',
    name: 'landing',
    component: LandingView,
  },
  {
    path: '/search',
    name: 'search',
    component: SearchView,
  },
  {
    path: '/dish/:id',
    name: 'dish-detail',
    component: () => import('./views/DishDetailView.vue'),
  },
  {
    path: '/restaurant/:slug',
    name: 'restaurant-detail',
    component: () => import('./views/RestaurantView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
