const express = require('express');
const router = express.Router();
const {
  getConversations,
  createConversation,
  getMessages,
  sendMessage,
  deleteConversation,
} = require('../controllers/chatController');
const { protect } = require('../middleware/authMiddleware');

router.route('/conversations')
  .get(protect, getConversations)
  .post(protect, createConversation);

router.route('/conversations/:id')
  .get(protect, getMessages)
  .delete(protect, deleteConversation);

router.route('/conversations/:id/messages')
  .post(protect, sendMessage);

module.exports = router;
