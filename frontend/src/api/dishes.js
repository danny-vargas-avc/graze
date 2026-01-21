import apiClient from './client'

export async function getDishes(params = {}) {
  const response = await apiClient.get('/dishes', { params })
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
