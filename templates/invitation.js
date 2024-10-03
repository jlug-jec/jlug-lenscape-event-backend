const generateInvitationHTML = (teamName, registrationLink) => {
    return `
      <!DOCTYPE html>
      <html lang="en">
      <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>You have been Invited to Lenscape</title>
      </head>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
          <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
              <tr>
                  <td align="center">
                      <img src="https://instagram.fdel4-2.fna.fbcdn.net/v/t51.29350-15/461912966_1997122384057222_6997011529901067544_n.webp?stp=dst-jpg_e35&efg=eyJ2ZW5jb2RlX3RhZyI6ImltYWdlX3VybGdlbi4xMDc5eDEwNzkuc2RyLmYyOTM1MC5kZWZhdWx0X2ltYWdlIn0&_nc_ht=instagram.fdel4-2.fna.fbcdn.net&_nc_cat=110&_nc_ohc=UspS01KKv4YQ7kNvgEKh1DV&_nc_gid=6f3950e6044c421dbbb3d37ae314d7c7&edm=AP4sbd4BAAAA&ccb=7-5&ig_cache_key=MzQ3MDEwODI1NjA5NjYwNzMwMA%3D%3D.3-ccb7-5&oh=00_AYA6Qd24GlgdSMziMmiVJbnqBz4J9YFzPhZiX9BtyDSbpg&oe=67045C76&_nc_sid=7a9f4b" 
                      alt="Artist Invitation" style="max-width: 100%; height: auto; margin-bottom: 20px;">
                      
                      <h1 style="color: #4a4a4a; font-size: 28px; margin-bottom: 20px;">Ahoy Artists!</h1>
                      
                      <p style="font-size: 18px; margin-bottom: 30px;">
                          You have been invited to join team <strong style="color: #e44d26;">${teamName}</strong>.
                      </p>
                      
                      <a href="${registrationLink}" style="background-color: #e44d26; color: white; padding: 12px 24px; text-decoration: none; font-weight: bold; border-radius: 5px; font-size: 16px; display: inline-block;">COMPLETE YOUR REGISTRATION NOW</a>
                      
                      <p style="margin-top: 30px; font-size: 14px; color: #777;">
                          We're excited to have you on board! If you have any questions, please don't hesitate to reach out.
                      </p>
                  </td>
              </tr>
          </table>
      </body>
      </html>
    `;
  };

const generatePartipantHTML = (userName,teamName,teamPageLink) => {
    return `
        <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to the Lenscape</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
        <tr>
            <td align="center">
                <img src="https://instagram.fdel4-2.fna.fbcdn.net/v/t51.29350-15/461912966_1997122384057222_6997011529901067544_n.webp?stp=dst-jpg_e35&efg=eyJ2ZW5jb2RlX3RhZyI6ImltYWdlX3VybGdlbi4xMDc5eDEwNzkuc2RyLmYyOTM1MC5kZWZhdWx0X2ltYWdlIn0&_nc_ht=instagram.fdel4-2.fna.fbcdn.net&_nc_cat=110&_nc_ohc=UspS01KKv4YQ7kNvgEKh1DV&_nc_gid=6f3950e6044c421dbbb3d37ae314d7c7&edm=AP4sbd4BAAAA&ccb=7-5&ig_cache_key=MzQ3MDEwODI1NjA5NjYwNzMwMA%3D%3D.3-ccb7-5&oh=00_AYA6Qd24GlgdSMziMmiVJbnqBz4J9YFzPhZiX9BtyDSbpg&oe=67045C76&_nc_sid=7a9f4b" alt="Welcome to the Team" style="max-width: 100%; height: auto; margin-bottom: 20px;">
                
                <h1 style="color: #4a4a4a; font-size: 28px; margin-bottom: 20px;">Welcome to Team  ${teamName}<br><strong style="color: #e44d26;">${userName}</strong>!</h1>
                
                <p style="font-size: 18px; margin-bottom: 30px;">
                    Congratulations on successfully registering the team! We're thrilled to have you on board. 
                </p>
                
                <a href="${teamPageLink}" style="background-color: #e44d26; color: white; padding: 12px 24px; text-decoration: none; font-weight: bold; border-radius: 5px; font-size: 16px; display: inline-block;">VIEW YOUR TEAM PAGE</a>
                
                <p style="margin-top: 30px; font-size: 14px; color: #777;">
                    We can't wait to see the amazing work you'll do. If you have any questions, feel free to reach out to us.
                </p>
            </td>
        </tr>
    </table>
</body>
</html>
`
}
const generateVoterHTML = (userName, votingLink) => {
    return `
      <!DOCTYPE html>
      <html lang="en">
      <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Welcome Voter to Lenscape!</title>
      </head>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
          <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
              <tr>
                  <td align="center">
                      <img src="https://instagram.fdel4-2.fna.fbcdn.net/v/t51.29350-15/461912966_1997122384057222_6997011529901067544_n.webp?stp=dst-jpg_e35&efg=eyJ2ZW5jb2RlX3RhZyI6ImltYWdlX3VybGdlbi4xMDc5eDEwNzkuc2RyLmYyOTM1MC5kZWZhdWx0X2ltYWdlIn0&_nc_ht=instagram.fdel4-2.fna.fbcdn.net&_nc_cat=110&_nc_ohc=UspS01KKv4YQ7kNvgEKh1DV&_nc_gid=6f3950e6044c421dbbb3d37ae314d7c7&edm=AP4sbd4BAAAA&ccb=7-5&ig_cache_key=MzQ3MDEwODI1NjA5NjYwNzMwMA%3D%3D.3-ccb7-5&oh=00_AYA6Qd24GlgdSMziMmiVJbnqBz4J9YFzPhZiX9BtyDSbpg&oe=67045C76&_nc_sid=7a9f4b" 
                      alt="Welcome Voter" style="max-width: 100%; height: auto; margin-bottom: 20px;">
                      
                      <h1 style="color: #4a4a4a; font-size: 28px; margin-bottom: 20px;">Hello, ${userName}!</h1>
                      
                      <p style="font-size: 18px; margin-bottom: 30px;">
                          We're excited to have you join as a voter! Your input helps decide the best submissions.
                      </p>
                      
                      <a href="${votingLink}" style="background-color: #e44d26; color: white; padding: 12px 24px; text-decoration: none; font-weight: bold; border-radius: 5px; font-size: 16px; display: inline-block;">Voting will begin shortly!</a>
                      
                      <p style="margin-top: 30px; font-size: 14px; color: #777;">
                          Thank you for being a part of our community. Every vote counts!
                      </p>
                  </td>
              </tr>
          </table>
      </body>
      </html>
    `;
  };
  

  module.exports={generateInvitationHTML,generatePartipantHTML,generateVoterHTML}