const Conversation = require('../models/Conversation');
const Message = require('../models/Message');

const getInternalApiKey = () => {
  const key = process.env.INTERNAL_API_KEY;
  if (!key) throw new Error('INTERNAL_API_KEY is not configured');
  return key;
};

// @desc    Get all conversations for a user
// @route   GET /api/chat/conversations
// @access  Private
const getConversations = async (req, res, next) => {
  try {
    const conversations = await Conversation.find({ userId: req.user.id }).sort({ updatedAt: -1 });
    res.status(200).json(conversations);
  } catch (error) {
    next(error);
  }
};

// @desc    Create a new conversation
// @route   POST /api/chat/conversations
// @access  Private
const createConversation = async (req, res, next) => {
  try {
    const { title } = req.body;
    const conversation = await Conversation.create({
      userId: req.user.id,
      title: title || 'New Conversation',
    });
    res.status(201).json(conversation);
  } catch (error) {
    next(error);
  }
};

// @desc    Get messages for a conversation
// @route   GET /api/chat/conversations/:id
// @access  Private
const getMessages = async (req, res, next) => {
  try {
    const conversation = await Conversation.findById(req.params.id);
    if (!conversation || conversation.userId.toString() !== req.user.id) {
      res.status(404);
      throw new Error('Conversation not found');
    }
    const messages = await Message.find({ conversationId: req.params.id }).sort({ createdAt: 1 });
    res.status(200).json(messages);
  } catch (error) {
    next(error);
  }
};

// @desc    Send a message and get AI response
// @route   POST /api/chat/conversations/:id/messages
// @access  Private
const sendMessage = async (req, res, next) => {
  try {
    const { content } = req.body;
    if (!content || typeof content !== 'string' || !content.trim()) {
      res.status(400);
      throw new Error('Message content is required');
    }

    const conversationId = req.params.id;
    const conversation = await Conversation.findById(conversationId);
    if (!conversation || conversation.userId.toString() !== req.user.id) {
      res.status(404);
      throw new Error('Conversation not found');
    }

    const userMessage = await Message.create({
      conversationId,
      role: 'user',
      content: content.trim(),
    });

    const previousMessages = await Message.find({
      conversationId,
      _id: { $ne: userMessage._id },
    })
      .sort({ createdAt: -1 })
      .limit(4);

    const history = previousMessages.reverse().map((msg) => ({
      role: msg.role,
      content: msg.content,
    }));

    const aiServiceUrl = process.env.AI_SERVICE_URL || 'http://localhost:8000';
    const response = await fetch(`${aiServiceUrl}/ai/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': getInternalApiKey(),
      },
      body: JSON.stringify({
        user_id: req.user.id,
        question: content.trim(),
        history,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('AI Service Error:', response.status, errorText);
      throw new Error('Failed to fetch an answer from the AI service');
    }

    const aiData = await response.json();
    const aiMessage = await Message.create({
      conversationId,
      role: 'assistant',
      content: aiData.answer,
      sources: aiData.sources || [],
    });

    if (conversation.title === 'New Conversation') {
      conversation.title = content.trim().substring(0, 30) + (content.trim().length > 30 ? '...' : '');
    }
    await conversation.save();

    res.status(201).json(aiMessage);
  } catch (error) {
    next(error);
  }
};

// @desc    Delete a conversation and its messages
// @route   DELETE /api/chat/conversations/:id
// @access  Private
const deleteConversation = async (req, res, next) => {
  try {
    const conversation = await Conversation.findById(req.params.id);
    if (!conversation || conversation.userId.toString() !== req.user.id) {
      res.status(404);
      throw new Error('Conversation not found');
    }
    await Message.deleteMany({ conversationId: req.params.id });
    await conversation.deleteOne();
    res.status(200).json({ id: req.params.id });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getConversations,
  createConversation,
  getMessages,
  sendMessage,
  deleteConversation,
};
