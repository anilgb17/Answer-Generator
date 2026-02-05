import axios from 'axios'

// Use import.meta.env for Vite, fallback to process.env for Jest compatibility
const getApiBaseUrl = () => {
  // Vite environment variable
  if (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL
  }
  // Jest/Node environment variable
  if (typeof process !== 'undefined' && process.env?.VITE_API_BASE_URL) {
    return process.env.VITE_API_BASE_URL
  }
  // Default to backend port 8000
  return 'http://localhost:8000'
}

const API_BASE_URL = getApiBaseUrl()

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Response Error:', error)
    
    if (error.response) {
      // Server responded with error status
      const errorData = {
        title: 'Server Error',
        message: error.response.data?.message || error.message,
        details: error.response.data?.details,
        guidance: error.response.data?.guidance,
        severity: 'error',
        status: error.response.status,
      }
      return Promise.reject(errorData)
    } else if (error.request) {
      // Request made but no response
      return Promise.reject({
        title: 'Network Error',
        message: 'Unable to reach the server. Please check your connection.',
        guidance: 'Ensure the backend server is running and accessible.',
        severity: 'error',
      })
    } else {
      // Something else happened
      return Promise.reject({
        title: 'Request Error',
        message: error.message,
        severity: 'error',
      })
    }
  }
)

export const uploadFile = async (file, language, provider = 'gemini', userId = null) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('language', language)
  formData.append('provider', provider)
  if (userId) {
    formData.append('user_id', userId)
  }

  const response = await api.post('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })

  return response.data
}

export const getStatus = async (sessionId) => {
  const response = await api.get(`/api/status/${sessionId}`)
  return response.data
}

export const downloadPDF = async (sessionId) => {
  const response = await api.get(`/api/download/${sessionId}`, {
    responseType: 'blob',
  })
  return response.data
}

export const getLanguages = async () => {
  const response = await api.get('/api/languages')
  return response.data
}

export const regenerateAnswer = async (sessionId, questionIndex, changeRequest) => {
  const formData = new FormData()
  formData.append('change_request', changeRequest)
  
  const response = await api.post(
    `/api/regenerate/${sessionId}/${questionIndex}`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  )
  
  return response.data
}

export default api
