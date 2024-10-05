const fetch = require('node-fetch'); // Import node-fetch to enable fetch in Node.js
require('dotenv').config(); // Ensure environment variables are loaded

async function sendEmail(emailDetails) {
    const myHeaders = {
        "Content-Type": "application/json",
        "X-Smtp2go-Api-Key": process.env.SMTP2GO_API_KEY // Environment variable for API key
    };

    const raw = JSON.stringify({
        "sender": process.env.SENDER_EMAIL,  // The sender's email address from env variables
        "to": [emailDetails.email],          // The recipient's email address
        "subject": emailDetails.subject,     // Email subject
        "html_body": emailDetails.html       // HTML version of the email
    });

    const requestOptions = {
        method: "POST",
        headers: myHeaders,
        body: raw,
        redirect: "follow"
    };

    try {
        const response = await fetch("https://api.smtp2go.com/v3/email/send", requestOptions);
        const result = await response.json();
        console.log('Email sent successfully to:', emailDetails.email);
        console.log(result);
    } catch (error) {
        console.error('Error sending email:', error);
    }
}

module.exports = {sendEmail};
