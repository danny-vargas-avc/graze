import apiClient from './client'

export async function getRestaurants() {
  const response = await apiClient.get('/restaurants')
  return response.data
}

export async function getRestaurant(slug) {
  const response = await apiClient.get(`/restaurants/${slug}`)
  return response.data
}

export async function getByoComponents(slug) {
  const response = await apiClient.get(`/restaurants/${slug}/byo`)
  return response.data
}

export async function getStats() {
  const response = await apiClient.get('/stats')
  return response.data
}
