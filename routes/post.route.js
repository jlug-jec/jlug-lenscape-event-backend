const express = require('express');
const { createPostController,editPostController,getPosts } = require('../controllers/post.controller');
const { authenticateJWT } = require('../middleware/auth');

const router = express.Router();


router.post('/createPost', createPostController);

router.get('/team/:teamId', getPosts);

router.put('/:id', editPostController);
module.exports = router;
