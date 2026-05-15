import client from './client'

export const uploadCSV = (file, onProgress) => {
  const form = new FormData()
  form.append('file', file)
  return client.post('/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded / e.total) * 100))
      }
    },
  })
}

export const listDatasets = () => client.get('/datasets')

export const getDataset = (id) => client.get(`/datasets/${id}`)

export const deleteDataset = (id) => client.delete(`/datasets/${id}`)
