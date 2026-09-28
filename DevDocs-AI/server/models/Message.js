const mongoose = require('mongoose');

const sourceSchema = new mongoose.Schema(
  {
    documentId: { type: String },
    documentName: { type: String },
    chunkId: { type: String },
    text: { type: String }
  },
  { _id: false }
);

const messageSchema = new mongoose.Schema(
  {
    conversationId: { type: mongoose.Schema.Types.ObjectId, ref: 'Conversation', required: true, index: true },
    role: { type: String, enum: ['user', 'assistant'], required: true },
    content: { type: String, required: true },
    sources: { type: [sourceSchema], default: [] }
  },
  { timestamps: true }
);

module.exports = mongoose.model('Message', messageSchema);
