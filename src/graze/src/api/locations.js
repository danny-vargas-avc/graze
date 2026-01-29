import apiClient from './client'

export async function getLocations(params = {}) {
  const response = await apiClient.get('/locations', { params })
  return response.data
}

export async function getLocation(id) {
  const response = await apiClient.get(`/locations/${id}`)
  return response.data
}

export async function createLocationFlag(data) {
  const response = await apiClient.post('/location-flags', data)
  return response.data
}
