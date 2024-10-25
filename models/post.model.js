const mongoose = require('mongoose');

// Define the post schema
const postSchema = new mongoose.Schema({
  teamId: { // Add teamId to reference the Team model
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Team',
  },
  teamName: { 
    type: String, 
    required: true 
  }, 
  title: { 
    type: String, 
    required: true 
  }, 
  url: { 
    type: String, 
    required: true 
  }, 
  fileId:{
    type:String
  },
  type: { 
    type: String, 
    required: true 
  },
  domain:{
    type:String,
    required:true
    
  },
  votes: [
    {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User', // Assuming votes are from users
    }
  ],
}, {
  timestamps: true // Automatically adds createdAt and updatedAt fields
});

// Create a Post model
const Post = mongoose.model('Post', postSchema);

module.exports = Post;
