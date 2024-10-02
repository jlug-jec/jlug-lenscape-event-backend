const User = require('../models/user.model'); // Updated to refer to User model
const Team = require('../models/team.model');
const Invitation = require('../models/invitation.model');
const sendEmail = require('../config/email');
const createPost = require('../models/post.model');
// Get posts for a participant

// Submit a post for a participant

exports.onboardedUser= async (req, res) => {
  console.log("ONBOARDING")
  console.log(req.body);
  try {
    const { userId, branch, instagramId, isParticipant, domains,teamName } = req.body;

    // Update user with onboarding data
    const user = await User.findByIdAndUpdate(
      userId,
      {
        branch,
        instagramId,
        isParticipant,
        isOnboarded: true,
        domains,
        teamName
      },
      { new: true } // Return the updated user
    );
    
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    res.status(200).json({ message: 'User onboarded successfully', user });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Internal Server Error' });
  }
};
exports.onboardTeam = async (req, res) => {
  try {
    const { teamName, teamMembers, teamLeader, branch, collegeName, posts } = req.body;

    // Filter valid team members (those with userIds)
    const validTeamMembers = teamMembers.filter(member => member.userId);

    // Create the team with valid members
    const newTeam = new Team({
      teamName,
      teamMembers: validTeamMembers.map(member => member.userId),
      teamLeader: teamLeader.userId,
    });

    await newTeam.save();

    // Create posts
    for (const post of posts) {
      await createPost({
        title: post.title,
        url: post.link,
        user: newTeam._id,
        domain: post.type,
        teamName: teamName,
      });
    }

    // Loop through all team members to send invitations if needed
    for (const member of teamMembers) {
      // If the member has a valid userId, update their info
      if (member.userId) {
        await User.findByIdAndUpdate(member.userId, {
          team: newTeam._id,
          isParticipant: true,
          isTeamLeader: member.userId.toString() === teamLeader.userId.toString(),
          branch: member.branch || branch,
          collegeName: member.collegeName || collegeName,
          isOnboarded: true
        });
      } else {
        // If the member doesn't have a userId, send an invitation email
        await sendEmail({
          email: member.email,
          subject: 'Team Invitation',
          message: `You've been invited to join the team "${teamName}". Please sign in to complete your registration.`
        });

        const invitation = new Invitation({
          email: member.email,
          teamId: newTeam._id
        });

        await invitation.save();
      }
    }

    res.status(200).json({ message: 'Team created successfully', teamId: newTeam._id });
  } catch (error) {
    console.error('Error in team onboarding:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
}
exports.joinTeam = async (req, res) => {
  try {
    const { userId, teamId } = req.body;
    const user = await User.findById(userId);
    const team = await Team.findById(teamId);

    if (!user || !team) {
      return res.status(404).json({ message: 'User or team not found' });
    }

    const invitation = await Invitation.findOne({ email: user.email, team: teamId });
    if (!invitation) {
      return res.status(403).json({ message: 'User is not invited to this team' });
    }

    user.team = teamId;
    user.isParticipant = true;
    user.isOnboarded = true;
    await user.save();

    team.teamMembers.push(user._id);
    await team.save();

    // Remove the invitation
    await Invitation.findByIdAndDelete(invitation._id);

    res.status(200).json({ message: 'User joined the team successfully', user });
  } catch (error) {
    console.error('Error joining team:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
};

exports.getUserDetails = async (req, res) => {
  try {
    const { userId } = req.params;
    console.log("USER DETAILS")
    console.log(userId)
    if (!userId) {
      return res.status(400).json({ message: 'User ID is required' });
    }
    const user = await User.findById(userId).populate('team');
    
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    // Check for pending invitations
    const invitation = await Invitation.findOne({ email: user.email }).populate('teamId');
    
    res.status(200).json({
      ...user.toObject(),
      pendingInvitation: invitation ? { teamId: invitation.teamId._id } : null
    });
  } catch (error) {
    console.error('Error fetching user details:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
};

exports.getTeamDetails = async (req, res) => {
  try {

    const { teamId } = req.params;
    console.log(teamId)
    const team = await Team.findById(teamId).populate('teamMembers', 'name email picture').populate('invitations');
    console.log("TEAM DETAILS")
    console.log(team)
    if (!team) {
      return res.status(404).json({ message: 'Team not found' });
    }
    
    res.status(200).json(team);
  } catch (error) {
    console.error('Error fetching team details:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
};




exports.getInvitationsByTeamId = async (req, res) => {
  try {
    const { teamId } = req.params;
    console.log("TEAM ID", teamId);
    
    // Find the team to ensure it exists
    const team = await Team.findById(teamId);
    if (!team) {
      return res.status(404).json({ message: 'Team not found' });
    }

    // Find all invitations for the given team ID
    const invitations = await Invitation.find({ teamId: teamId });
    
    // Extract emails from invitations
    const invitationEmails = invitations.map(invitation => invitation.email);

    console.log("Invitations found:", invitations.length);

    res.status(200).json({ 
      teamMembers: team.teamMembers, 
      invitations: invitationEmails 
    });
  } catch (error) {
    console.error('Error fetching invitations by team ID:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
};



