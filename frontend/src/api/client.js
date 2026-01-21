import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      const errorData = error.response.data?.error || {
        code: 'SERVER_ERROR',
        message: 'Something went wrong',
      }
      return Promise.reject(errorData)
    } else if (error.request) {
      // Network error
      return Promise.reject({
        code: 'NETWORK_ERROR',
        message: 'Unable to connect. Please check your internet connection.',
      })
    }
    return Promise.reject(error)
  }
)

export default apiClient
