
const nodemailer = require('nodemailer');

require('dotenv').config(); // Make sure you have dotenv to manage environment variables
async function sendEmail(emailDetails) {
    const transporter = nodemailer.createTransport({
        service: 'gmail',
        auth: {
            user: process.env.SENDER_EMAIL,
            pass: process.env.SENDER_PASSWORD,
        },
    });

    const mailOptions = {
        from: process.env.SENDER_EMAIL,
        to: emailDetails.email,  // Ensure this is defined correctly
        subject: emailDetails.subject,
        html: emailDetails.html
    };

    try {
        await transporter.sendMail(mailOptions);
        console.log('Email sent successfully to:', emailDetails.email);
    } catch (error) {
        console.error('Error sending email:', error);
    }
}

module.exports = sendEmail;
