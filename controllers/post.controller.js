// const Vote = require('../models/vote.model');
const Post = require('../models/post.model');
const User = require('../models/user.model');
const Team=require('../models/team.model')
const checkLink = require('../config/checkDrive'); 



async function createPost(postDetails) {
 console.log("POST DETAILS")
  const newPost = new Post({
    title: postDetails.title,
    url: postDetails.url,
    teamId: postDetails.teamId,
    domain: postDetails.category || postDetails.domain,
    type: postDetails.type,
    teamName: postDetails.teamName,
  });


  try {



    await newPost.save();
    console.log("POST DETAILS")

    // Update the associated team with the new post's ID
    await Team.findByIdAndUpdate(postDetails.teamId, {
      $push: { posts: newPost._id } // Add the post ID to the team's posts array
    });
  console.log("adding here")

    return newPost;
  } catch (error) {
    console.error('Error creating post:', error);
    throw error; // Handle the error appropriately
  }
}

exports.createPost=createPost


// Create a new post
exports.createPostController = async (req, res) => {
  try {
    const postDetails = req.body;
    console.log("POST DETAILS")
    console.log("\n\n\n\n\n\n")
    console.log(postDetails)
    console.log("\n\n\n\n\n\n")
    const result=await checkLink(postDetails.url)

    if(result.success==false){  
      return res.status(400).json({ message: result.message });
      
    }
   
    console.log(result)
    postDetails.fileId=result.data.fileId
    postDetails.type=result.data.mimeType;

    console.log(postDetails)
    const newPost = await createPost(postDetails);
    

    // Send a success response
    console.log("post created successfully")
    return res.status(201).json({
      message: 'Post created successfully'
    });
  } catch (error) {
    console.error('Error creating post:', error);
    return res.status(500).json({
      message: 'Error creating post',
      error: error.message,
    });
  }
};


async function editPost(postId, postDetails) {

  const updatedPost = await Post.findByIdAndUpdate(
    postDetails._id,
    {
      title: postDetails.title,
      url: postDetails.url,
      teamId: postDetails.teamId,
      domain: postDetails.category,
      type: postDetails.type,
      teamName: postDetails.teamName,
    },
    { new: true }
  );
  
  return updatedPost;
}

exports.editPostController = async (req, res) => {
  try {
    const postId = req.params.id;
    const postDetails = req.body;
   
    const result=await checkLink(postDetails.url)

    if(result.success==false){  
      return res.status(400).json({ message: result.message });
      
    }
    console.log(postDetails)
    postDetails.fileId=result.data.fileId
    postDetails.type=result.data.mimeType;
    console.log("POST DETAILS")
    console.log("\n\n\n\n\n\n")
    console.log(postDetails)
    console.log("\n\n\n\n\n\n")
    const updatedPost = await editPost(postId, postDetails);
    console.log(updatedPost)



    if (!updatedPost) {
      return res.status(404).json({ message: 'Post not found' });
    }

    // Send a success response
    return res.status(200).json({
      message: 'Post updated successfully',
      post: updatedPost,
    });
  } catch (error) {
    console.error('Error updating post:', error);
    return res.status(500).json({
      message: 'Error updating post',
      error: error.message,
    });
  }
};



exports.getPosts = async (req, res) => {
  try {
    const { teamId } = req.params;

    // Fetch the team and populate the posts
    const team = await Team.findById(teamId)
      .populate('teamMembers', 'name email') // Fetch team members
      .populate('posts') // Populate the posts associated with the team
      .populate('votes.post'); // Optionally populate votes if needed

    if (!team) {
      return res.status(404).json({ message: 'Team not found' });
    }

    // Send the populated team data, including posts
    console.log(team)
    return res.status(200).json(team);
  } catch (error) {
    console.error('Error fetching team posts:', error);
    return res.status(500).json({ message: 'Internal Server Error' });
  }
};

exports.getAllPosts = async (req, res) => {
  try {
    const posts = await Post.find();

    return res.status(200).json(posts);
  } catch (error) {
    console.error('Error fetching posts:', error);
    return res.status(500).json({ message: 'Internal Server Error' });
  }
}


exports.increaseVote = async (req, res) => {
  try {
   
    const { postId } = req.params;
    const { userId } = req.body;
    console.log(postId,userId)

    // Find the post
    const post = await Post.findById(postId);
    if (!post) {
      return res.status(404).json({ message: 'Post not found' });
    }
    if (post.votes.includes(userId)) {
      console.log("user has already voted")
      return res.status(400).json({ message: 'You have already voted for this post' });
    }
    

    // Update the post's vote count
    post.votes.push(userId)

    await post.save();
   
    // Send a success response
    return res.status(200).json({
      message: 'Vote increased successfully',

    });
    } catch (error) {
    console.error('Error increasing vote:', error);
    return res.status(500).json({
      message: 'Error increasing vote',
      error: error.message,
    });
    }
  };


  exports.decreaseVote = async (req, res) => {
    try {
      const { postId } = req.params;
      const { userId } = req.body;
      console.log('Removing vote:', postId, userId);
  
      // Find the post
      const post = await Post.findById(postId);
      if (!post) {
        return res.status(404).json({ message: 'Post not found' });
      }
  
      // Convert votes to strings for proper comparison
      const userIdStr = userId.toString();
      const hasVoted = post.votes.some(vote => vote.toString() === userIdStr);
  
      if (!hasVoted) {
        console.log("User hasn't voted yet");
        return res.status(400).json({ message: 'You have not voted for this post yet' });
      }
  
      // Use MongoDB's $pull operator to remove the vote
      const updatedPost = await Post.findByIdAndUpdate(
        postId,
        { $pull: { votes: userId } },
        { new: true } // Return the updated document
      );
  
      if (!updatedPost) {
        return res.status(404).json({ message: 'Post not found during update' });
      }
  
      console.log('Updated votes:', updatedPost.votes);
  
      return res.status(200).json({
        message: 'Vote removed successfully',
        updatedVotes: updatedPost.votes
      });
    } catch (error) {
      console.error('Error removing vote:', error);
      return res.status(500).json({
        message: 'Error removing vote',
        error: error.message,
      });
    }
  };