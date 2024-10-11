const { file } = require("googleapis/build/src/apis/file");

const API_KEY = process.env.GOOGLE_DRIVE_API_KEY;

const extractGoogleDriveFileId = (url) => {
  const regex = /(?:\/d\/|id=)([a-zA-Z0-9_-]+)/;
  const match = url.match(regex);
  return match ? match[1] : null;
};

const isYoutubeUrl = (url) => {
  const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
  return youtubeRegex.test(url);
};

async function checkLink(url) {
  if (!url) {
    return { 
      success: false,
      message: 'No URL provided' 
    };
  }

  // Check if it's a YouTube URL
  if (isYoutubeUrl(url)) {
    return {
      success: true,
      data: {
        mimeType: 'video',
        url: url
      }
    };
  }

  // Handle Google Drive URLs
  const fileId = extractGoogleDriveFileId(url);
  console.log("Checking file via google drive")
  console.log(url)
  console.log(fileId)
  if (!fileId) {
    return { 
      success: false,
      message: 'Invalid URL format - not a YouTube or Google Drive URL' 
    };
  }

  try {
    const response = await fetch(
      `https://www.googleapis.com/drive/v3/files/${fileId}?key=${API_KEY}`,
      {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      }
    );

    const data = await response.json();

    // Handle error response
    if (data.error) {
      console.log(data.error.code)
      console.log(data.error.message)
      if (data.error.code === 404) {
        return {
          success: false,
          message: 'File does not exist or is private'
        };
      }
      console.log(data.error.message)
      return {
        success: false,
        message: `There was an error, please try again later`
      };
    }

    // Handle successful response
    if (data.id && data.mimeType) {
      return {
        success: true,
        data: {
          type: 'drive',
          fileId: data.id,
          mimeType: data.mimeType,
          fileName: data.name
        }
      };
    }

    return {
      success: false,
      message: 'Unexpected response format from Google Drive API'
    };
  } catch (error) {
    console.error('Error checking link:', error);
    return {
      success: false,
      message: 'Failed to verify link: Network or server error'
    };
  }
}

module.exports = checkLink;