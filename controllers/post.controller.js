// const Vote = require('../models/vote.model');
const Post = require('../models/post.model');
const User = require('../models/user.model');
const Team=require('../models/team.model')
const checkDrivelink = require('../config/checkDrive'); 

const convertToDirectDownloadUrl = (url) => {
  // Check if the URL is already in the required format
  const regex = /https:\/\/drive\.google\.com\/uc\?id=([a-zA-Z0-9_-]+)/;
  if (regex.test(url)) {
      return url; // Return the URL if it's already in the correct format
  }
  
  // Extract the file ID from the original URL
  const idMatch = url.match(/d\/([a-zA-Z0-9_-]+)/);
  if (idMatch && idMatch[1]) {
      const fileId = idMatch[1];
      // Return the direct download URL
      return `https://drive.google.com/uc?id=${fileId}`;
  }
  
  // If the URL is not valid, return the original URL or handle accordingly
  console.error("Invalid Google Drive URL:", url);
  return url; // Return the original URL if conversion fails
};

async function createPost(postDetails) {

  const newPost = new Post({
    title: postDetails.title,
    url: postDetails.url,
    teamId: postDetails.teamId,
    domain: postDetails.category || postDetails.domain,
    type: postDetails.type,
    teamName: postDetails.teamName,
  });
  console.log(newPost)

  try {



    await newPost.save();

    // Update the associated team with the new post's ID
    await Team.findByIdAndUpdate(postDetails.teamId, {
      $push: { posts: newPost._id } // Add the post ID to the team's posts array
    });

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
    const result=await checkDrivelink(postDetails.url)

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

  postDetails.url = convertToDirectDownloadUrl(postDetails.url);

  const updatedPost = await Post.findByIdAndUpdate(
    postDetails._id,
    {
      title: postDetails.title,
      url: postDetails.url,
      teamId: postDetails.teamId,
      domain: postDetails.category,
      type: postDetails.mediaType,
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
   
    const result=await checkDrivelink(postDetails.url)

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
