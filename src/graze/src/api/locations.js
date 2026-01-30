import apiClient from './client'

export async function getLocations(params = {}, signal = null) {
  const config = { params }
  if (signal) {
    config.signal = signal
  }
  const response = await apiClient.get('/locations', config)
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
