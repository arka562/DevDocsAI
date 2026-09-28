const path = require('path');
const fs = require('fs');
const Document = require('../models/Document');
const { processDocument, removeDocumentVectors } = require('../services/aiService');

// POST /api/documents/upload
const uploadDocument = async (req, res, next) => {
  try {
    if (!req.file) {
      return res.status(400).json({ message: 'No file uploaded' });
    }

    const title = req.body.title || req.file.originalname;

    const doc = await Document.create({
      userId: req.user._id,
      title,
      fileName: req.file.originalname,
      filePath: req.file.path,
      fileType: path.extname(req.file.originalname).replace('.', '') || 'pdf',
      fileSize: req.file.size,
      status: 'uploaded'
    });

    res.status(201).json(doc);

    // Fire-and-forget processing so the upload response isn't blocked
    // on embedding generation, which can take a while for larger PDFs.
    processDocumentAsync(doc);
  } catch (err) {
    next(err);
  }
};

const processDocumentAsync = async (doc) => {
  try {
    doc.status = 'processing';
    await doc.save();

    const result = await processDocument({
      documentId: doc._id.toString(),
      userId: doc.userId.toString(),
      filePath: doc.filePath,
      title: doc.title
    });

    doc.status = 'completed';
    doc.chunkCount = result.chunk_count || 0;
    await doc.save();
  } catch (err) {
    doc.status = 'failed';
    doc.errorMessage = err.message;
    await doc.save();
    console.error(`Document processing failed for ${doc._id}:`, err.message);
  }
};

// GET /api/documents
const listDocuments = async (req, res, next) => {
  try {
    const docs = await Document.find({ userId: req.user._id }).sort({ createdAt: -1 });
    res.json(docs);
  } catch (err) {
    next(err);
  }
};

// GET /api/documents/:id
const getDocument = async (req, res, next) => {
  try {
    const doc = await Document.findOne({ _id: req.params.id, userId: req.user._id });
    if (!doc) return res.status(404).json({ message: 'Document not found' });
    res.json(doc);
  } catch (err) {
    next(err);
  }
};

// DELETE /api/documents/:id
const deleteDocument = async (req, res, next) => {
  try {
    const doc = await Document.findOne({ _id: req.params.id, userId: req.user._id });
    if (!doc) return res.status(404).json({ message: 'Document not found' });

    await removeDocumentVectors({ documentId: doc._id.toString(), userId: req.user._id.toString() }).catch((e) =>
      console.error('Vector cleanup failed:', e.message)
    );

    if (fs.existsSync(doc.filePath)) {
      fs.unlinkSync(doc.filePath);
    }

    await doc.deleteOne();
    res.json({ message: 'Document deleted' });
  } catch (err) {
    next(err);
  }
};

module.exports = { uploadDocument, listDocuments, getDocument, deleteDocument };
