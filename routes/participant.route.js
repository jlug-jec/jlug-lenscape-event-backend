const express = require('express');
const { getParticipantPosts, submitPost, onboardedUser,getUserDetails,onboardTeam,joinTeam,getTeamDetails,getInvitationsByTeamId } = require('../controllers/participant.controller');
const { authenticateJWT } = require('../middleware/auth');

const router = express.Router();


router.get('/users/:userId', getUserDetails);

// router.post('/onboarding', onboardedUser);
// router.get('/onboarding', (req, res) => {
//     res.send('Onboarding route');
// }
// );


router.get('/team/:teamId',getTeamDetails);
router.post('/onboarding', onboardTeam);
router.post('/join-team', joinTeam);
router.get('/invitations/:teamId', getInvitationsByTeamId);





module.exports = router;
