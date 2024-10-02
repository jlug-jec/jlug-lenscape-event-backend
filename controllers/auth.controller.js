const jwt = require('jsonwebtoken');
const User = require('../models/user.model');
const Invitation = require('../models/invitation.model');
exports.googleCallback = async (req, res) => {
  const { user } = req;
  
  try {
    // Check if user has a pending invitation
    const invitation = await Invitation.findOne({ email: user.email }).populate('teamId');
    if (invitation) {
      // User has a pending invitation
      res.redirect(`http://localhost:3000/onboarding?userId=${user._id}&teamId=${invitation.teamId._id}`);
    } else if (!user.isOnboarded) {
      // New user, needs to complete onboarding
      res.redirect(`http://localhost:3000/onboarding?userId=${user._id}`);
    } else {
      // User is already onboarded
      return res.redirect(`http://localhost:3000/onboarding?userId=${req.user._id}`);
    }
  } catch (error) {
    console.error('Error in Google callback:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
};