const jwt = require('jsonwebtoken');
const User = require('../models/user.model');
const Invitation = require('../models/invitation.model');
load

frontend_url=process.env.FRONTEND_URL || "http://localhost:3000"

exports.googleCallback = async (req, res) => {
  const { user } = req;
  console.log("Google Auth")

  
  try {
    // Check if user has a pending invitation
    const invitation = await Invitation.findOne({ email: user.email });
    if (invitation) {
      // User has a pending invitation
      res.redirect(`${frontend_url}/onboarding?userId=${user._id}&teamId=${invitation.teamId}`);
    } else if (!user.isOnboarded) {
      // New user, needs to complete onboarding
      res.redirect(`${frontend_url}/onboarding?userId=${user._id}`);
    } else {
      // User is already onboarded
      return res.redirect(`${frontend_url}//onboarding?userId=${req.user._id}`);
    }
  } catch (error) {
    console.error('Error in Google callback:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
};