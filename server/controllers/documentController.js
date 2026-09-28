const Document = require('../models/Document');
const fs = require('fs');
const path = require('path');

// @desc    Get all documents for a user
// @route   GET /api/documents
// @access  Private
const getDocuments = async (req, res, next) => {
  try {
    const documents = await Document.find({ userId: req.user.id }).sort({ createdAt: -1 });
    res.status(200).json(documents);
  } catch (error) {
    next(error);
  }
};

// @desc    Upload a new document
// @route   POST /api/documents/upload
// @access  Private
const uploadDocument = async (req, res, next) => {
  try {
    if (!req.file) {
      res.status(400);
      throw new Error('Please upload a file');
    }

    const { title } = req.body;
    
    if (!title) {
      fs.unlinkSync(req.file.path);
      res.status(400);
      throw new Error('Please provide a title');
    }

    // 1. Create document in DB with 'processing' status
    const document = await Document.create({
      userId: req.user.id,
      title: title,
      fileName: req.file.filename,
      fileType: req.file.mimetype,
      fileSize: req.file.size,
      status: 'processing',
    });

    res.status(201).json(document); // Send immediate response to frontend

    // 2. Process document asynchronously via FastAPI
    const aiServiceUrl = process.env.AI_SERVICE_URL || 'http://localhost:8000';
    
    try {
      const formData = new FormData();
      const fileStream = fs.createReadStream(req.file.path);
      // Constructing form data for node-fetch is tricky natively, so we can use standard fetch with File/Blob
      // or simply pass the file buffer. Since Node 18 fetch doesn't perfectly support streams in FormData out of the box,
      // we'll send it as a Blob.
      const fileBuffer = fs.readFileSync(req.file.path);
      const blob = new Blob([fileBuffer], { type: req.file.mimetype });
      
      const aiFormData = new FormData();
      aiFormData.append('file', blob, req.file.filename);

      const aiRes = await fetch(`${aiServiceUrl}/ai/process-document`, {
        method: 'POST',
        body: aiFormData
      });

      if (aiRes.ok) {
        const aiData = await aiRes.json();
        document.status = 'completed';
        document.chunkCount = aiData.chunk_count || 0;
        await document.save();
      } else {
        document.status = 'failed';
        await document.save();
        console.error('AI Service Error:', await aiRes.text());
      }
    } catch (err) {
      document.status = 'failed';
      await document.save();
      console.error('Failed to communicate with AI Service:', err);
    }
  } catch (error) {
    next(error);
  }
};

// @desc    Get a single document
// @route   GET /api/documents/:id
// @access  Private
const getDocument = async (req, res, next) => {
  try {
    const document = await Document.findById(req.params.id);

    if (!document) {
      res.status(404);
      throw new Error('Document not found');
    }

    // Check for user ownership
    if (document.userId.toString() !== req.user.id) {
      res.status(401);
      throw new Error('User not authorized');
    }

    res.status(200).json(document);
  } catch (error) {
    next(error);
  }
};

// @desc    Delete a document
// @route   DELETE /api/documents/:id
// @access  Private
const deleteDocument = async (req, res, next) => {
  try {
    const document = await Document.findById(req.params.id);

    if (!document) {
      res.status(404);
      throw new Error('Document not found');
    }

    // Check for user ownership
    if (document.userId.toString() !== req.user.id) {
      res.status(401);
      throw new Error('User not authorized');
    }

    // Delete file from filesystem
    const filePath = path.join(__dirname, '..', 'uploads', document.fileName);
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
    }

    await document.deleteOne();

    res.status(200).json({ id: req.params.id });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getDocuments,
  uploadDocument,
  getDocument,
  deleteDocument,
};
