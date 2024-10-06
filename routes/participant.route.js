const express = require('express');
const { getParticipantPosts, submitPost, onboardedUser,getUserDetails,onboardTeam,joinTeam,getTeamDetails,getInvitationsByTeamId } = require('../controllers/participant.controller');
const  authenticateJWT  = require('../middleware/auth');

const router = express.Router();


router.get('/users/:userId',authenticateJWT, getUserDetails);

router.get('/team/:teamId',authenticateJWT,getTeamDetails);
router.post('/onboarding',authenticateJWT, onboardTeam);
router.post('/join-team',authenticateJWT, joinTeam);
router.get('/invitations/:teamId',authenticateJWT, getInvitationsByTeamId);





module.exports = router;
