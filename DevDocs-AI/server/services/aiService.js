const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');

const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000';

// Send an uploaded document to the Python AI service for processing
// (text extraction -> cleaning -> chunking -> embeddings -> FAISS storage)
const processDocument = async ({ documentId, userId, filePath, title }) => {
  const form = new FormData();
  form.append('document_id', documentId);
  form.append('user_id', userId);
  form.append('title', title);
  form.append('file', fs.createReadStream(filePath));

  const { data } = await axios.post(`${AI_SERVICE_URL}/ai/process-document`, form, {
    headers: form.getHeaders(),
    maxBodyLength: Infinity,
    maxContentLength: Infinity
  });

  return data; // { status, chunk_count }
};

// Ask a question against a user's indexed documents (RAG)
const askQuestion = async ({ userId, question, documentIds }) => {
  const { data } = await axios.post(`${AI_SERVICE_URL}/ai/chat`, {
    user_id: userId,
    question,
    document_ids: documentIds || null
  });

  return data; // { answer, sources }
};

const removeDocumentVectors = async ({ documentId, userId }) => {
  const { data } = await axios.delete(`${AI_SERVICE_URL}/ai/documents/${documentId}`, {
    params: { user_id: userId }
  });
  return data;
};

module.exports = { processDocument, askQuestion, removeDocumentVectors };
