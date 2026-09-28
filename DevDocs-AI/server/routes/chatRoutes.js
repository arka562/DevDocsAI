const express = require('express');
const {
  createConversation,
  listConversations,
  getConversation,
  sendMessage,
  deleteConversation
} = require('../controllers/chatController');
const { protect } = require('../middleware/authMiddleware');

const router = express.Router();

router.use(protect);
router.post('/conversations', createConversation);
router.get('/conversations', listConversations);
router.get('/conversations/:id', getConversation);
router.post('/conversations/:id/messages', sendMessage);
router.delete('/conversations/:id', deleteConversation);

module.exports = router;
