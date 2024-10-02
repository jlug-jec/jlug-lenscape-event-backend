const mongoose = require('mongoose');

// Define the team schema
const teamSchema = new mongoose.Schema({
  teamName: { type: String, required: true }, 
  teamMembers: [
    {
      type: mongoose.Schema.Types.ObjectId, 
      ref: 'User'
    }
  ],
  teamLeader: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  invitations: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Invitation' }],
  posts: [
    {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Post'
    }
  ],
  votes: [
    {
      post: { type: mongoose.Schema.Types.ObjectId, ref: 'Post' }
    }
  ],
});


const Team = mongoose.model('Team', teamSchema);

module.exports = Team;
