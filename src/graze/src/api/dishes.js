import apiClient from './client'

export async function getDishes(params = {}, signal = null) {
  const config = { params }
  if (signal) {
    config.signal = signal
  }
  const response = await apiClient.get('/dishes', config)
  return response.data
}

export async function getDish(id) {
  const response = await apiClient.get(`/dishes/${id}`)
  return response.data
}

export async function createFlag(data) {
  const response = await apiClient.post('/flags', data)
  return response.data
}
