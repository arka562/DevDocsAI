const mongoose = require('mongoose');

const documentSchema = new mongoose.Schema(
  {
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true, index: true },
    title: { type: String, required: true },
    fileName: { type: String, required: true },
    filePath: { type: String, required: true },
    fileType: { type: String, default: 'pdf' },
    fileSize: { type: Number },
    status: {
      type: String,
      enum: ['uploaded', 'processing', 'completed', 'failed'],
      default: 'uploaded'
    },
    chunkCount: { type: Number, default: 0 },
    errorMessage: { type: String }
  },
  { timestamps: true }
);

module.exports = mongoose.model('Document', documentSchema);
