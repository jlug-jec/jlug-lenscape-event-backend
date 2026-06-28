# Lenscape API (Flask + Firestore + Firebase Auth)

This is the Python-based backend service for the **Lenscape Immersive Digital Art Gallery**. It handles Firestore data operations, verifies Firebase user tokens, manages artwork curation and voting, and uploads images/videos directly to Cloudinary.

## Features
*   **Flask API** with standard JSON payloads matching the frontend React models.
*   **Firestore Curation**: Handles users, artworks, comments, categories, admins, and moderation statuses.
*   **Firebase Authentication**: Verifies Firebase ID tokens for Google/email sign-in flows.
*   **Cloudinary Integration**: Direct binary image/video uploads with dynamic media URL creation.
*   **Unlocked Achievements**: Auto-evaluates requirements to award badges to students on interactions.
*   **Local Developer Bypass**: Pass `X-Mock-User` and `X-Mock-Email` headers to bypass Clerk authentication in testing.

---

## Getting Started

### 1. Requirements
Ensure you have **Python 3.8+** installed and a Firebase project with Firestore enabled.

### 2. Setup Virtual Environment & Install Dependencies
Navigate to this directory and create a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (CMD):
.\venv\Scripts\activate.bat
# On macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Environment Configurations
Rename `.env.example` to `.env` and configure your credentials:

```ini
# Flask configuration
FLASK_PORT=5000
FLASK_ENV=development

# Firebase Admin credentials (use one)
FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
FIREBASE_SERVICE_ACCOUNT=/absolute/path/to/firebase-service-account.json

# Admin and JWT secrets
ADMIN_SECRET_KEY=change-this-master-key
ADMIN_JWT_SECRET=change-this-admin-secret
USER_JWT_SECRET=change-this-user-secret
OTP_SECRET=change-this-otp-secret

# SMTP2GO email
SMTP2GO_API_KEY=your-smtp2go-api-key
SENDER_EMAIL=lenscape@jlug.club

# Cloudinary configurations
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret
```

### 4. Database Seeding (Optional)
To pre-populate Firestore with initial mock users and artworks from the frontend, run:

```bash
python seed.py
```

### 5. Running the Server
Start the development server using:

```bash
python app.py
```
The server will boot on `http://localhost:5000`.

---

## API Documentation

### Public Endpoints
*   `GET /api/health`: Health status.
*   `GET /api/categories`: Fetch names of all art categories.
*   `GET /api/artworks`: Fetch all approved artworks (ordered by creation date).

### Authenticated Endpoints (Header: `Authorization: Bearer <Firebase_ID_Token>`)
*   `GET /api/cloudinary/signature`: Retrieve a cryptographic signed configuration to upload files directly from the frontend to Cloudinary.
*   `GET /api/users/profile`: Retrieve user profile, their submissions, and unlocked achievements.
*   `POST /api/users/profile` (JSON): Create/update user signature profile.
*   `POST /api/artworks` (JSON): Submit a new artwork. Requires `imageUrl`, `title`, `description`, and `category`.
*   `POST /api/artworks/<id>/vote`: Upvote an artwork. (Restricted to one vote per category per user).
*   `POST /api/artworks/<id>/comment`: Add a comment to an artwork. (Restricted to one comment per user).

### Admin-Only Endpoints
*   `POST /api/artworks/<id>/approve`: Moderate artwork to "approved".
*   `POST /api/artworks/<id>/reject`: Moderate artwork to "rejected".
*   `GET /api/admin/users`: List all registered users.
*   `POST /api/admin/users/<id>/ban`: Ban a user.
*   `POST /api/admin/users/<id>/unban`: Unban a user.
*   `POST /api/categories`: Add a new category.
*   `DELETE /api/categories/<name>`: Remove a category.

---

## Frontend Integration Tips

### Authentication Integration
When communicating with the backend, acquire a Firebase ID token on the frontend:
```javascript
const token = await firebase.auth().currentUser.getIdToken();
const response = await fetch('http://localhost:5000/api/users/profile', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### Dev Testing (Bypass JWT)
For local testing when Clerk is not fully configured, send dev header overrides:
```javascript
const response = await fetch('http://localhost:5000/api/users/profile', {
  headers: {
    'X-Mock-User': 'user_alex',
    'X-Mock-Email': 'alex@college.edu'
  }
});
```
