const mongoose = require('mongoose');

const sourceSchema = mongoose.Schema({
  documentName: { type: String, required: true },
});

const messageSchema = mongoose.Schema(
  {
    conversationId: {
      type: mongoose.Schema.Types.ObjectId,
      required: true,
      ref: 'Conversation',
    },
    role: {
      type: String,
      required: true,
      enum: ['user', 'assistant'],
    },
    content: {
      type: String,
      required: true,
    },
    sources: [sourceSchema],
  },
  {
    timestamps: true,
  }
);

module.exports = mongoose.model('Message', messageSchema);
