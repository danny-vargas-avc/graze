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
    meta: { headerMode: 'home' },
    component: () => import('./views/HomeView.vue'),
  },
  {
    path: '/map',
    redirect: '/home',
  },
  {
    path: '/settings',
    redirect: '/home',
  },
  {
    path: '/dish/:id',
    name: 'dish-detail',
    meta: { hideHeader: true },
    component: () => import('./views/DishDetailView.vue'),
  },
  {
    path: '/restaurants',
    name: 'restaurants-list',
    meta: { hideHeader: true },
    component: () => import('./views/RestaurantsListView.vue'),
  },
  {
    path: '/restaurant/:slug',
    name: 'restaurant-detail',
    meta: { hideHeader: true },
    component: () => import('./views/RestaurantView.vue'),
  },
  {
    path: '/restaurant/:slug/byo',
    name: 'byo-calculator',
    meta: { hideHeader: true },
    component: () => import('./views/ByoCalculatorView.vue'),
  },
  {
    path: '/restaurant/:slug/drinks',
    name: 'drink-customizer',
    meta: { hideHeader: true },
    component: () => import('./views/DrinkCustomizerView.vue'),
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
