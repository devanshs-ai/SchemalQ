import client from './client'

export const runQuery = (datasetId, prompt) =>
  client.post('/query', { dataset_id: datasetId, prompt })
