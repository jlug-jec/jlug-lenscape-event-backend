const https = require('https');
const { URL } = require('url');

class DriveFileTypeChecker {
    extractFileId(driveLink) {
        const patterns = [
            /\/file\/d\/([a-zA-Z0-9-_]+)/,
            /id=([a-zA-Z0-9-_]+)/,
            /\/open\?id=([a-zA-Z0-9-_]+)/
        ];

        for (const pattern of patterns) {
            const match = driveLink.match(pattern);
            if (match && match[1]) {
                return match[1];
            }
        }
        return null;
    }

    makeRequest(url, options = {}) {
        return new Promise((resolve, reject) => {
            const req = https.get(url, {
                ...options,
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Accept': '*/*',
                    ...options.headers
                }
            }, (res) => {
                let data = '';
                res.on('data', (chunk) => { data += chunk; });
                res.on('end', () => resolve({ response: res, body: data }));
            });

            req.on('error', reject);
            req.end();
        });
    }

    async getFileType(driveLink) {
        try {
            const fileId = this.extractFileId(driveLink);
            if (!fileId) {
                return { message: 'Invalid Drive link' };
            }

            const largeFileUrl = `https://drive.google.com/uc?export=download&id=${fileId}&confirm=t`;
            const { response, body } = await this.makeRequest(largeFileUrl);
            console.log(body)
            if (body.includes('video-player') || body.includes('drive-viewer-video-player')) {
                return {
                    message: 'Valid video',
                    fileId: fileId,
                    url: `https://drive.google.com/uc?export=download&id=${fileId}`
                };
            }

            if (response.headers.location) {
                const redirectUrl = new URL(response.headers.location);
                const finalResponse = await this.makeRequest(redirectUrl);
                return this.processResponse(finalResponse, fileId);
            }

            const regularUrl = `https://drive.google.com/uc?export=download&id=${fileId}`;
            const regularResponse = await this.makeRequest(regularUrl);

            if (regularResponse.headers.location) {
                const redirectUrl = new URL(regularResponse.headers.location);
                const finalResponse = await this.makeRequest(redirectUrl);
                
                return this.processResponse(finalResponse, fileId);
            }
           
            return this.processResponse({ response, body }, fileId);

        } catch (error) {
            return { message: 'Error checking link: ' + error.message };
        }
    }

    processResponse({ response, body }, fileId) {
        const contentType = response.headers['content-type'];
        
        if (response.statusCode === 403 || response.statusCode === 401) {
                console.log("PRIVATE")
                console.log(body)
            return { message: 'Image/video is private' };
        }
        if (contentType && contentType.includes('text/html') && body.includes('.mp4') ) {
            return {
                message: 'Valid video',
                isPublic:true,
                fileId: fileId,
                type:"video",
                url: `https://drive.google.com/uc?export=download&id=${fileId}`
             };
        }
        
        if (contentType) {
            if (contentType.startsWith('image/')) {
                return {
                    message: 'Valid image',
                    isPublic:true,
                    type:"image",
                    fileId: fileId,
                    url: `https://drive.google.com/uc?export=download&id=${fileId}`
                };
            }
            if (contentType.startsWith('video/')) {
                return {
                    message: 'Valid video',
                    isPublic:true,
                    type:"video",
                    fileId: fileId,
                    url: `https://drive.google.com/uc?export=download&id=${fileId}`
                };
            }
        }
        
        return { message: 'File is not in image/video format',isPublic:false };
    }
}

async function checkDrivelink(url) {

    const checker = new DriveFileTypeChecker();

    try {
        const result = await checker.getFileType(url);
        return result;
    } catch (error) {
        console.error('Error checking link:', error);
        return { message: 'Error checking accessibility: ' + error.message };
    }
}

module.exports = checkDrivelink;