const Invitation = require('../models/invitation.model');
const User = require('../models/user.model');
require('dotenv').config();
const jwt = require('jsonwebtoken');


frontend_url=process.env.FRONTEND_URL || "http://localhost:3000"
console.log(frontend_url)
frontend_url="https://b00e-103-199-225-144.ngrok-free.app"
const tempAuthCodes = new Map();


setInterval(() => {
  const now = Date.now();
  for (const [code, data] of tempAuthCodes.entries()) {
    if (now > data.expiresAt) {
      tempAuthCodes.delete(code);
    }
  }
}, 60 * 60 * 1000);

exports.googleCallback = async (req, res) => {
  const { user, jwtToken, refreshToken } = req;
  console.log("user" ,  user)
  try {
    // Generate a random code
    const tempCode = Math.random().toString(36).substring(2) + Date.now().toString(36);
    
    // Store data with 5-minute expiry
    tempAuthCodes.set(tempCode, {
      data: {
        user
      },
      expiresAt: Date.now() + 5 * 60 * 1000 // 5 minutes
    });

    const invitation = await Invitation.findOne({ email: user.user.email });
   
    if (invitation) {
      res.redirect(`${frontend_url}/onboarding?code=${tempCode}&teamId=${invitation.teamId}`);
    } else if (!user.user.isOnboarded) {
      res.redirect(`${frontend_url}/onboarding?code=${tempCode}`);
    } else if(user.user.isParticipant){
      res.redirect(`${frontend_url}/onboarding?onboarded=true&code=${tempCode}`);
    }
    else{
      res.redirect(`${frontend_url}/countdown`);
    }
  } catch (error) {
    console.error('Error in Google callback:', error);
    res.status(500).json({ message: 'An error occurend, Please Log in again' });
  }
};

// Endpoint to exchange code for tokens
exports.exchangeCode = async (req, res) => {
  const { code } = req.body;
  try {
    const storedData = tempAuthCodes.get(code);
    
    if (!storedData || Date.now() > storedData.expiresAt) {
      return res.status(404).json({ message: 'Code expired or invalid' });
    }
    tempAuthCodes.delete(code);
    console.log(storedData.data)
    return res.json(storedData.data);
  } catch (error) {
    console.error('Error exchanging code:', error);
    return res.status(500).json({ message: 'Internal server error' });
  }
};



exports.regenerateJWT=async (req, res) => {
  const { refreshToken } = req.body; 
  console.log('\n\n\n')
  console.log(refreshToken)
  console.log('\n\n\n')
  if (!refreshToken) {
    return res.status(403).json({ message: 'Refresh token is required' });
  }

  try {
    const user = await User.findOne({ refreshToken });
    console.log(user)
    if (!user) {
      return res.status(403).json({ message: 'Refresh token is invalid' });
    }

    jwt.verify(refreshToken, process.env.REFRESH_TOKEN_SECRET, (err, decoded) => {
      if (err) {
        return res.status(403).json({ message: 'Refresh token is invalid' });
      }

      const newAccessToken = jwt.sign({ userId: user._id }, process.env.JWT_SECRET, { expiresIn: '1h' });



      // Send back the new access token
      res.status(200).json({ accessToken: newAccessToken });
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Internal Server Error' });
  }
};