const express = require('express');
const passport = require('passport');
const { googleCallback,exchangeCode, regenerateJWT } = require('../controllers/auth.controller');
const router = express.Router();

// Redirect to Google for authentication
router.get('/google', passport.authenticate('google', { scope: ['profile', 'email'], session: false }));

// Callback URL after Google login
router.get(
    '/google/callback',
    passport.authenticate('google', { failureRedirect: '/', session: false }), // Disable session
   googleCallback
  );
  

router.post('/exchange-code', exchangeCode);

router.post('/regenerate-jwt',regenerateJWT);

module.exports = router;

