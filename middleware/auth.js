const jwt = require('jsonwebtoken');

function authenticateToken(req, res, next) {
  // Extract the token from the Authorization header
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer <token>

  console.log("token", token);

  // Check if the token is missing
  if (!token) return res.status(401).json({ message: 'Token is missing' });

  // Verify the token
  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) {
      if (err.name === 'TokenExpiredError') {
      return res.status(401).json({ message: 'Token has expired' });
      }
      return res.status(403).json({ message: 'Token is invalid' });
    }

    req.user = user;
    next();
  });
}

module.exports = authenticateToken;
