const GoogleStrategy = require('passport-google-oauth20').Strategy;
const User = require('../models/user.model'); // Adjust the path as needed
module.exports = function (passport) {
  passport.use(
    new GoogleStrategy(
      {
        clientID: process.env.GOOGLE_CLIENT_ID,
        clientSecret: process.env.GOOGLE_CLIENT_SECRET,
        callbackURL: '/auth/google/callback',
      },
      async (accessToken, refreshToken, profile, done) => {
        try {
          let user = await User.findOne({ googleId: profile.id });

          if (!user) {
            // Create a new user if not found
            user = new User({
              googleId: profile.id,
              name: profile.displayName,
              email: profile.emails[0].value,
              picture: profile.photos[0].value,
            });
            await user.save();
          }

          // If the user already exists, check if they have a valid refresh token
          let newRefreshToken;
          if (!user.refreshToken || isTokenExpired(user.refreshToken)) {
            newRefreshToken = user.generateRefreshToken();
            user.refreshToken = newRefreshToken;
            await user.save();
          } else {
            newRefreshToken = user.refreshToken;
          }

          // Generate JWT for this session
          const jwtToken = user.generateJwtToken();

          return done(null, { user, jwtToken, refreshToken: newRefreshToken });
        } catch (err) {
          console.error(err);
          return done(err, false);
        }
      }
    )
  );
};

// Helper function to check if refresh token is expired
function isTokenExpired(token) {
  try {
    const decoded = jwt.verify(token, process.env.JWT_REFRESH_SECRET);
    return false; // Token is valid
  } catch (err) {
    return true; // Token is expired or invalid
  }
}
