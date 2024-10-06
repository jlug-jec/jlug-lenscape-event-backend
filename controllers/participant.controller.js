const User = require('../models/user.model'); // Updated to refer to User model
const Team = require('../models/team.model');
const Invitation = require('../models/invitation.model');
const {sendEmail} = require('../config/email');
const {createPost} = require('../controllers/post.controller');

const checkLink = require('../config/checkDrive'); 
const {generateInvitationHTML,generatePartipantHTML,generateVoterHTML}=require('../templates/invitation');
const { post } = require('../routes/auth.route');
const { parse } = require('dotenv');
// Get posts for a participant

// Submit a post for a participant

exports.onboardedUser= async (req, res) => {
  
  try {
    const { id, branch, isParticipant,collegeName } = req.body;
    // Update user with onboarding data
    const user = await User.findByIdAndUpdate(
      id,
      {
        branch,
        collegeName,
        isParticipant,
        isOnboarded: true,
      },
      { new: true } // Return the updated user
    );
    console.log(user)
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
   
    const htmlContent = generateVoterHTML(userName=user.name, "https://lenscape.jlug.club/countdown");

    await sendEmail({
      email: user.email,
      subject: 'Lenscape 2024 - Countdown Begins',
      html: htmlContent
    });
    res.status(200).json({ message: 'User onboarded successfully', user });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Internal Server Error' });
  }
};

exports.onboardTeam = async (req, res) => {
  try {
   
   console.log("TEAM ONBOARDING")
  
    const { id,teamName, teamMembers, teamLeader, branch, collegeName, posts,isParticipant } = await req.body;
    const team = await Team.findOne({ teamName });
    if (team) {
      
    }


    if(isParticipant==false){
      this.onboardedUser(req,res);
      return

    }
    for (let post of posts){
      
      const result=await checkLink(post.link)
      console.log(result)
      if(result.success==false){  
        
        return res.status(400).json({ message: result.message+` for ${post.link}` });
        
      }
      post.type=result.data.mimeType; ;
  }
  
    // Filter valid team members (those with userIds)
    const validTeamMembers = teamMembers.filter(member => member.userId);

    for (const member of teamMembers) {
      const user=await User.findOne({email:member.email});  
      if(user && user.team) return res.status(420).json({ message: `${member.email} is already in another team` });
  
    }
       

  
    // Create the team with valid members
    const newTeam = new Team({
      teamName,
      teamMembers: validTeamMembers.map(member => member.userId),
      teamLeader: teamLeader.userId,
    });
    
    await newTeam.save();
    for (const post of posts) {
  
      const postPayload={
        title: post.title,
        url: post.link,
        teamId: newTeam._id,
        domain: post.category,
        type:post.type,
        teamName: teamName,
      }
      const postMetaData = await createPost(postPayload);
      console.log(postMetaData)
    }

    
    // Create posts
  
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
        await sendEmail({
          email: member.email,
          subject: 'Lenscape 2024 - Countdown Begins',
          html:generatePartipantHTML(userName=member.name,teamName,teamPageLink="lenscape.jlug.club/profile")
        });
      } else {
        // If the member doesn't have a userId, send an invitation email
        await sendEmail({
          email: member.email,
          subject: 'Lenscape 2024',
          html:generateInvitationHTML(teamName,"lenscape.jlug.club")
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
    console.log("JOIN TEAM")
    console.log(req.body)
    const { id, teamId,branch,collegeName } = req.body;
    console.log(id,teamId)
    const user = await User.findById(id);
    const team = await Team.findById(teamId);

    if (!user || !team) {
      return res.status(404).json({ message: 'User or team not found' });
    }
     
    const invitation = await Invitation.findOne({ email: user.email, teamId: teamId });
    console.log(invitation)
    if (!invitation) {
      return res.status(403).json({ message: 'User is not invited to this team' });
    }

    user.team = teamId;
    user.isParticipant = true;
    user.isOnboarded = true;
    user.branch=branch;
    user.collegeName=collegeName;
    await user.save();
    console.log(user)

    team.teamMembers.push(user._id);
    await team.save();

    // Remove the invitation
    await Invitation.findByIdAndDelete(invitation._id);
    await sendEmail({
          email: user.email,
          subject: 'Lenscape 2024 - Countdown Begins',
          html:generatePartipantHTML(userName=user.name,teamName=team.teamName,teamPageLink="lenscape.jlug.club/profile")
        });
    
    res.status(200).json({ message: 'User joined the team successfully', user });
  } catch (error) {
    console.error('Error joining team:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
};

exports.getUserDetails = async (req, res) => {
  try {
    const { userId } = req.params;


    if (!userId) {
      return res.status(400).json({ message: 'User ID is required' });
    }
    const user = await User.findById(userId).populate('team');
    
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    // Check for pending invitations
    const invitation = await Invitation.findOne({ email: user.email });
    
    res.status(200).json({
      ...user.toObject(),
      pendingInvitation: invitation ? { teamId: invitation.teamId } : null
    });
  } catch (error) {
    console.error('Error fetching user details:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
};

exports.getTeamDetails = async (req, res) => {
  try {
    console.log("TEAM DETAILS")
    let { teamId } = req.params;
    console.log(teamId)
   
    const team = await Team.findById(teamId).populate('teamMembers', 'name email picture').populate('invitations');
 
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
    const team = await Team.findById({_id:teamId}).populate('teamMembers');
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


