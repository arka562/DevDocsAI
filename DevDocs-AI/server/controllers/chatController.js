const Conversation = require('../models/Conversation');
const Message = require('../models/Message');
const { askQuestion } = require('../services/aiService');

// POST /api/chat/conversations
const createConversation = async (req, res, next) => {
  try {
    const conversation = await Conversation.create({
      userId: req.user._id,
      title: req.body.title || 'New conversation'
    });
    res.status(201).json(conversation);
  } catch (err) {
    next(err);
  }
};

// GET /api/chat/conversations
const listConversations = async (req, res, next) => {
  try {
    const conversations = await Conversation.find({ userId: req.user._id }).sort({ updatedAt: -1 });
    res.json(conversations);
  } catch (err) {
    next(err);
  }
};

// GET /api/chat/conversations/:id
const getConversation = async (req, res, next) => {
  try {
    const conversation = await Conversation.findOne({ _id: req.params.id, userId: req.user._id });
    if (!conversation) return res.status(404).json({ message: 'Conversation not found' });

    const messages = await Message.find({ conversationId: conversation._id }).sort({ createdAt: 1 });
    res.json({ conversation, messages });
  } catch (err) {
    next(err);
  }
};

// POST /api/chat/conversations/:id/messages
const sendMessage = async (req, res, next) => {
  try {
    const { content, documentIds } = req.body;
    if (!content || !content.trim()) {
      return res.status(400).json({ message: 'Message content is required' });
    }

    const conversation = await Conversation.findOne({ _id: req.params.id, userId: req.user._id });
    if (!conversation) return res.status(404).json({ message: 'Conversation not found' });

    const userMessage = await Message.create({
      conversationId: conversation._id,
      role: 'user',
      content
    });

    // Auto-title new conversations from the first message
    if (conversation.title === 'New conversation') {
      conversation.title = content.slice(0, 60);
    }

    let answer = '';
    let sources = [];

    try {
      const result = await askQuestion({
        userId: req.user._id.toString(),
        question: content,
        documentIds
      });
      answer = result.answer;
      sources = result.sources || [];
    } catch (err) {
      answer =
        'I ran into a problem reaching the AI service. Make sure the AI service is running and that you have at least one processed document.';
      console.error('AI service error:', err.message);
    }

    const assistantMessage = await Message.create({
      conversationId: conversation._id,
      role: 'assistant',
      content: answer,
      sources
    });

    conversation.updatedAt = new Date();
    await conversation.save();

    res.status(201).json({ userMessage, assistantMessage });
  } catch (err) {
    next(err);
  }
};

// DELETE /api/chat/conversations/:id
const deleteConversation = async (req, res, next) => {
  try {
    const conversation = await Conversation.findOne({ _id: req.params.id, userId: req.user._id });
    if (!conversation) return res.status(404).json({ message: 'Conversation not found' });

    await Message.deleteMany({ conversationId: conversation._id });
    await conversation.deleteOne();

    res.json({ message: 'Conversation deleted' });
  } catch (err) {
    next(err);
  }
};

module.exports = {
  createConversation,
  listConversations,
  getConversation,
  sendMessage,
  deleteConversation
};
