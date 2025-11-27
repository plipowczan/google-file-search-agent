import axios from 'axios';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getStores = async () => {
  const response = await api.get('/stores/');
  return response.data;
};

export const createStore = async (displayName) => {
  const response = await api.post('/stores/', { display_name: displayName });
  return response.data;
};

export const deleteStore = async (storeId) => {
  await api.delete(`/stores/${storeId}`);
};

export const getFiles = async (storeId) => {
  const response = await api.get(`/stores/${storeId}/files/`);
  return response.data;
};

export const uploadFile = async (storeId, file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post(`/stores/${storeId}/files/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const deleteFile = async (storeId, fileId) => {
  await api.delete(`/stores/${storeId}/files/${fileId}`);
};

export const chatWithStore = async (storeId, message, model = 'gemini-2.5-flash') => {
  const response = await api.post('/chat/', {
    store_id: storeId,
    message: message,
    model: model,
  });
  return response.data;
};

export default api;
