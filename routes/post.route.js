const express = require('express');
const { createPostController,editPostController,getPosts, getAllPosts,increaseVote } = require('../controllers/post.controller');
const { authenticateJWT } = require('../middleware/auth');
const checkDrivelink = require('../config/checkDrive'); 
const router = express.Router();


router.post('/createPost', createPostController);
router.get('/team/:teamId', getPosts);
router.put('/:id', editPostController);
router.post('/isPublicDrive', async (req, res) => {
    const url = req.body.url;
  
    console.log(url)
    // Check if URL is provided
    if (!url) {
        return res.status(400).json({ error: 'URL is required.' });
    }

    // Call the checkDrivelink function
    const result = await checkDrivelink(url);
    
    // Send the result back to the client
    return res.status(200).json(result);
});
router.get('/all', getAllPosts);
router.post("/vote/:postId",increaseVote)

module.exports = router;
