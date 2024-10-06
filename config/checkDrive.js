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
      if (data.error.code === 404) {
        return {
          success: false,
          message: 'File does not exist or is private'
        };
      }
      return {
        success: false,
        message: `Drive API Error: ${data.error.message}`
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