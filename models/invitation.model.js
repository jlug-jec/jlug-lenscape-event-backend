const mongoose = require('mongoose');


const invitationSchema = new mongoose.Schema({
    email: { type: String, required: true },
    teamId: { type: mongoose.Schema.Types.ObjectId, ref: 'Team', required: true },
});


const Invitation = mongoose.model('Invitation', invitationSchema);

module.exports = Invitation;
