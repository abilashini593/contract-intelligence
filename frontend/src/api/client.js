import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

// Attach custom API key header if configured in browser session
api.interceptors.request.use((config) => {
  const customApiKey = sessionStorage.getItem('GEMINI_API_KEY');
  if (customApiKey) {
    config.headers['X-Gemini-API-Key'] = customApiKey;
  }
  return config;
});

export const getHealth = async () => {
  const resp = await api.get('/health');
  return resp.data;
};

export const listContracts = async () => {
  const resp = await api.get('/contracts');
  return resp.data;
};

export const getContract = async (contractId) => {
  const resp = await api.get(`/contracts/${contractId}`);
  return resp.data;
};

export const getContractVersion = async (contractId, versionId) => {
  const resp = await api.get(`/contracts/${contractId}/versions/${versionId}`);
  return resp.data;
};

export const uploadContract = async (formData) => {
  const resp = await api.post('/contracts/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return resp.data;
};

export const uploadContractVersion = async (contractId, formData) => {
  const resp = await api.post(`/contracts/${contractId}/upload-version`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return resp.data;
};

export const deleteContract = async (contractId) => {
  const resp = await api.delete(`/contracts/${contractId}`);
  return resp.data;
};

export const updateParty = async (itemId, payload) => {
  const resp = await api.patch(`/items/party/${itemId}`, payload);
  return resp.data;
};

export const updateClause = async (itemId, payload) => {
  const resp = await api.patch(`/items/clause/${itemId}`, payload);
  return resp.data;
};

export const updateObligation = async (itemId, payload) => {
  const resp = await api.patch(`/items/obligation/${itemId}`, payload);
  return resp.data;
};

export const updateUnclearTerm = async (itemId, payload) => {
  const resp = await api.patch(`/items/unclear-term/${itemId}`, payload);
  return resp.data;
};

export const batchUpdateStatus = async (itemType, itemIds, status) => {
  const resp = await api.post('/items/batch-status', {
    item_type: itemType,
    item_ids: itemIds,
    status: status,
  });
  return resp.data;
};

export const getContractReminders = async (contractId, params = {}) => {
  const resp = await api.get(`/contracts/${contractId}/reminders`, { params });
  return resp.data;
};

export const toggleDismissReminder = async (reminderId) => {
  const resp = await api.patch(`/contracts/reminders/${reminderId}/toggle-dismiss`);
  return resp.data;
};

export const getReviewedSummary = async (contractId, versionId = null) => {
  const url = versionId
    ? `/contracts/${contractId}/summary?version_id=${versionId}`
    : `/contracts/${contractId}/summary`;
  const resp = await api.get(url);
  return resp.data;
};

export const getSummaryMarkdownUrl = (contractId, versionId = null) => {
  return versionId
    ? `/api/contracts/${contractId}/summary/markdown?version_id=${versionId}`
    : `/api/contracts/${contractId}/summary/markdown`;
};

export default api;
