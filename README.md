# Lenscape API (Flask + MongoDB + Clerk)

This is the Python-based backend service for the **Lenscape Immersive Digital Art Gallery**. It handles database operations on MongoDB, verifies user tokens from Clerk, manages artwork curation & voting, and uploads images/videos directly to Cloudinary.

## Features
*   **Flask API** with standard JSON payloads matching the frontend React models.
*   **MongoDB Curation**: Handles users, artworks, comments, categories, and moderation statuses.
*   **Clerk Authentication**: JWT signature validation against Clerk's JSON Web Key Sets (JWKS).
*   **Cloudinary Integration**: Direct binary image/video uploads with dynamic media URL creation.
*   **Unlocked Achievements**: Auto-evaluates requirements to award badges to students on interactions.
*   **Local Developer Bypass**: Pass `X-Mock-User` and `X-Mock-Email` headers to bypass Clerk authentication in testing.

---

## Getting Started

### 1. Requirements
Ensure you have **Python 3.8+** and **MongoDB** installed (locally or via MongoDB Atlas).

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

# MongoDB URI (Atlas or local)
MONGO_URI=mongodb://localhost:27017/lenscape

# Clerk JWKS endpoint (used to verify tokens locally)
CLERK_JWKS_URL=https://<your-clerk-instance-id>.clerk.accounts.dev/.well-known/jwks.json

# Admin Emails
ADMIN_EMAILS=admin@jlug.club,admin@lenscape.com

# Cloudinary configurations
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret
```

### 4. Database Seeding (Optional)
To pre-populate MongoDB with initial mock users and artworks from the frontend, run:

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

### Authenticated Endpoints (Header: `Authorization: Bearer <Clerk_JWT>`)
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
When communicating with the backend, acquire the session token from Clerk on the frontend:
```javascript
const token = await window.Clerk.session.getToken();
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
