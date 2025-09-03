# TV Show Tracker Backend

A minimal Python backend for tracking TV shows and user watch history. Built with FastAPI, SQLite, and JWT authentication.

## Features

- **Global TV Show Management**: Add, update, delete, and list TV shows
- **Global Watch Tracking**: Mark shows as watched/unwatched with ratings (1-5) for all users
- **JWT Authentication**: Secure API with bearer token authentication
- **SQLite Database**: File-based database with automatic table creation
- **CORS Support**: Ready for frontend integration

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Local Development

1. **Clone and setup virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**:
   ```bash
   cp env.example .env
   # Edit .env if needed
   ```

4. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Open API documentation**:
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

## API Usage Examples

### Authentication

**Login to get JWT token**:
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"ray","password":"password123"}'
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": "ray"
}
```

### Using the API

**Set your token**:
```bash
TOKEN="your_jwt_token_here"
```

**List all shows**:
```bash
curl http://127.0.0.1:8000/shows \
  -H "Authorization: Bearer $TOKEN"
```

**Create a new show**:
```bash
curl -X POST http://127.0.0.1:8000/shows \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Breaking Bad"}'
```

**Mark a show as watched**:
```bash
curl -X POST http://127.0.0.1:8000/shows/1/watch \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"rating":5}'
```

**Get user's watched shows**:
```bash
curl http://127.0.0.1:8000/users/ray/watched \
  -H "Authorization: Bearer $TOKEN"
```

## Complete API Contract

### Authentication
- `POST /auth/login`
  - **Body**: `{"username": "string", "password": "string"}`
  - **Response**: `{"access_token": "string", "token_type": "bearer", "user": "string"}`

### Shows (Authentication Required)
- `GET /shows?watched={true|false}`
  - **Query Params**: `watched` (optional) - filter by watched status
  - **Response**: Array of `ShowResponse` objects
- `POST /shows`
  - **Body**: `{"title": "string"}`
  - **Response**: `ShowResponse` object (201 Created)
- `PATCH /shows/{show_id}`
  - **Body**: `{"title": "string"}` (partial update)
  - **Response**: `ShowResponse` object
- `DELETE /shows/{show_id}`
  - **Response**: 204 No Content
- `POST /shows/{show_id}/watch`
  - **Body**: `{"rating": 1-5}`
  - **Response**: `{"message": "Show marked as watched"}` (201 Created)
- `DELETE /shows/{show_id}/watch`
  - **Response**: 204 No Content

### Users (Authentication Required)
- `GET /users/{username}/watched`
  - **Response**: Array of `ShowResponse` objects (globally watched shows)
- `GET /users/{username}/unwatched`
  - **Response**: Array of `ShowResponse` objects (globally unwatched shows)

### Response Models

**ShowResponse**:
```json
{
  "id": 1,
  "title": "Breaking Bad",
  "created_at": "2024-01-15T10:30:00",
  "watched": true,
  "rating": 5
}
```

**ShowResponse** (includes global watch status):
```json
{
  "id": 1,
  "title": "Breaking Bad",
  "created_at": "2024-01-15T10:30:00",
  "watched": true,
  "rating": 5,
  "watched_at": "2024-01-15T10:30:00"
}
```

## Frontend Development Guide

### Authentication Flow
1. **Login**: Send `POST /auth/login` with username/password
2. **Store Token**: Save the returned `access_token` (localStorage, sessionStorage, or secure cookie)
3. **Use Token**: Include `Authorization: Bearer {token}` header in all subsequent requests
4. **Token Expiry**: Tokens expire after 60 minutes - redirect to login when you get 401 responses

### Data Models

**Show Object**:
```json
{
  "id": 1,
  "title": "Breaking Bad",
  "created_at": "2024-01-15T10:30:00",
  "watched": true,
  "rating": 5
}
```

**Show Object** (now includes global watch status):
```json
{
  "id": 1,
  "title": "Breaking Bad",
  "created_at": "2024-01-15T10:30:00",
  "watched": true,
  "rating": 5,
  "watched_at": "2024-01-15T10:30:00"
}
```

### Key Frontend Patterns

1. **Protected Routes**: Check for valid JWT token before allowing access to main app
2. **Token Refresh**: Implement automatic logout on 401 responses
3. **Error Handling**:
   - 400: Validation errors (show user-friendly messages)
   - 401: Unauthorized (redirect to login)
   - 404: Not found (show appropriate message)
   - 422: Bad request data (highlight form errors)

### Common Frontend Operations

**Login Form**:
```javascript
const login = async (username, password) => {
  const response = await fetch('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });

  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', data.user);
    return data;
  } else {
    throw new Error('Login failed');
  }
};
```

**Authenticated Request Helper**:
```javascript
const authenticatedFetch = async (url, options = {}) => {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('No token');

  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
};
```

**List Shows with Filter**:
```javascript
const getShows = async (watched = null) => {
  let url = '/shows';
  if (watched !== null) {
    url += `?watched=${watched}`;
  }

  const response = await authenticatedFetch(url);
  return response.json();
};
```

**Mark Show as Watched**:
```javascript
const watchShow = async (showId, rating) => {
  const response = await authenticatedFetch(`/shows/${showId}/watch`, {
    method: 'POST',
    body: JSON.stringify({ rating })
  });

  if (!response.ok) {
    throw new Error('Failed to mark show as watched');
  }
};
```

### State Management Considerations

- **User State**: Store current user info and authentication status
- **Shows List**: Cache shows data with refresh on mutations
- **Watch Status**: Track global watch status for all shows
- **Loading States**: Handle async operations with loading indicators
- **Error States**: Display user-friendly error messages

### UI/UX Recommendations

- **Login Screen**: Simple username/password form
- **Shows List**: Display all shows with global watched/unwatched indicators
- **Show Details**: Allow editing titles and managing global watch status
- **Rating System**: 1-5 star rating when marking as watched (applies to all users)
- **Filtering**: Toggle between "All Shows", "Watched", "Unwatched"
- **Responsive Design**: Mobile-friendly interface
- **Real-time Updates**: Refresh data after mutations

## Default Users

The system comes with two hardcoded users for testing:
- **Username**: `ray`, **Password**: `password123`
- **Username**: `dana`, **Password**: `secret`

## Database Schema

- **Show**: `id`, `title`, `created_at`
- **Watch**: `id`, `user`, `show_id`, `rating`, `watched_at`

## Testing

Run the test suite:
```bash
pytest tests/
```

## Deployment on Render

1. **Push your code to GitHub**

2. **Create a new Web Service on Render**:
   - Connect your GitHub repository
   - Use the free plan
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables**:
   - `SECRET_KEY`: Will be auto-generated by Render

4. **Deploy**: Render will automatically build and deploy your service

## Project Structure

```
tvtracker/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app and auth endpoints
│   ├── auth.py          # JWT authentication
│   ├── models.py        # SQLModel database models
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── db.py           # Database configuration
│   ├── utils.py        # Utility functions and demo data
│   └── routers/
│       ├── __init__.py
│       ├── shows.py     # Show management endpoints
│       └── users.py     # User watch history endpoints
├── tests/
│   ├── test_auth.py
│   └── test_shows.py
├── requirements.txt
├── render.yaml
├── Procfile
├── env.example
└── README.md
```

## Environment Variables

- `SECRET_KEY`: JWT signing secret (defaults to dev value)
- `SEED`: Set to "true" to seed demo data on startup

## Demo Data

When `SEED=true`, the system automatically creates 5 demo TV shows:
- Breaking Bad
- The Wire
- Mad Men
- The Sopranos
- Game of Thrones

## Error Handling

The API returns appropriate HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid/missing token)
- `404` - Not Found
- `422` - Validation Error (FastAPI automatic)

## CORS Configuration

CORS is configured to allow:
- `http://localhost:5173` (Vite default)
- `http://localhost:3000` (React default)
- `*` (all origins in development)

### Frontend Integration Notes

- **Base URL**: Use `http://127.0.0.1:8000` for local development
- **CORS**: Pre-configured for common frontend dev servers
- **Content-Type**: Always send `application/json` for POST/PATCH requests
- **Authentication**: Include `Authorization: Bearer {token}` header for protected endpoints
- **Error Responses**: All errors return JSON with `detail` field containing error message

## Security Notes

- **Production**: Change the default `SECRET_KEY` and use proper password hashing
- **Current**: Uses hardcoded users for simplicity
- **JWT**: Tokens expire after 60 minutes
- **Validation**: All inputs are validated with Pydantic schemas

## Dependencies

- **FastAPI**: Modern web framework
- **SQLModel**: SQL database with Pydantic integration
- **Uvicorn**: ASGI server
- **python-jose**: JWT handling
- **python-dotenv**: Environment variable management

## Troubleshooting

### Common Frontend Issues

1. **CORS Errors**: Ensure your frontend is running on `localhost:5173`, `localhost:3000`, or update CORS in `app/main.py`
2. **401 Unauthorized**: Check that your JWT token is valid and not expired (60 minutes)
3. **400 Bad Request**: Validate your request payload matches the expected schema
4. **Network Errors**: Verify the backend is running on `http://127.0.0.1:8000`

### Backend Issues

1. **Database Errors**: Delete `tvtracker.db` file to reset database
2. **Port Conflicts**: Change port in `uvicorn` command if 8000 is busy
3. **Import Errors**: Ensure virtual environment is activated and dependencies installed
