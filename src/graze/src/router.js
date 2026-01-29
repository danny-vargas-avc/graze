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
    path: '/loading',
    name: 'loading',
    component: () => import('./views/LoadingView.vue'),
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
  {
    path: '/map-test',
    name: 'map-test',
    component: () => import('./views/MapTestView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
