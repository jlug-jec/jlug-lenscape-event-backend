const mongoose = require('mongoose');

// Define the team schema
const teamSchema = new mongoose.Schema({
  _id: {
    type: mongoose.Schema.Types.ObjectId, // Keep _id as ObjectId for existing data
    required: true,
    auto: true, // Let MongoDB auto-generate ObjectId
  },
  teamName: { type: String, required: true,unique:true }, 
  teamMembers: [
    {
      type: mongoose.Schema.Types.ObjectId, 
      ref: 'User',
      unique:true
    }
  ],
  teamLeader: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true ,unique:true},
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
