import { createRouter, createWebHistory } from 'vue-router'
import LandingView from './views/LandingView.vue'

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
    path: '/home',
    name: 'home',
    component: () => import('./views/HomeView.vue'),
  },
  {
    path: '/map',
    name: 'map-explore',
    component: () => import('./views/MapExploreView.vue'),
  },
  {
    path: '/favorites',
    name: 'favorites',
    component: () => import('./views/FavoritesView.vue'),
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('./views/ProfileView.vue'),
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
    path: '/restaurant/:slug/byo',
    name: 'byo-calculator',
    component: () => import('./views/ByoCalculatorView.vue'),
  },
  // Redirect old routes
  {
    path: '/search',
    redirect: '/home',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
