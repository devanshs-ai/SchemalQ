import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 60000,
})

// Response interceptor — surfaces the backend's detail field as the error message
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.data?.detail) {
      const detail = error.response.data.detail
      error.message =
        typeof detail === 'string' ? detail : JSON.stringify(detail)
    }
    return Promise.reject(error)
  }
)

export default client
