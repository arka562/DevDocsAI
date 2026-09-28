const express = require('express');
const router = express.Router();
const { protect } = require('../middleware/authMiddleware');
const Document = require('../models/Document');
const Conversation = require('../models/Conversation');
const Message = require('../models/Message');

router.get('/', protect, async (req, res, next) => {
  try {
    const userId = req.user.id;

    // Get documents count
    const documentsCount = await Document.countDocuments({ userId });

    // Get questions asked (user messages)
    const conversations = await Conversation.find({ userId }).select('_id title updatedAt').sort({ updatedAt: -1 }).limit(5);
    const conversationIds = conversations.map(c => c._id);
    
    // Count user messages across all their conversations
    const allUserConversations = await Conversation.find({ userId }).select('_id');
    const allUserConvIds = allUserConversations.map(c => c._id);
    const questionsCount = await Message.countDocuments({ 
      conversationId: { $in: allUserConvIds },
      role: 'user'
    });

    res.status(200).json({
      documentsCount,
      questionsCount,
      recentConversations: conversations
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
