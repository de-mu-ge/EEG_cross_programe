import axios from 'axios'

export function uploadEegFile(file) {
  const form = new FormData()
  form.append('file', file)
  return axios.post('/api/eeg/upload', form)
}

export function getEegResult(fileId) {
  return axios.get(`/api/eeg/result/${fileId}`)
}
