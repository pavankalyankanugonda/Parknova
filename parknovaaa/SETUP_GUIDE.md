# ParkNova - Frontend & Backend Setup Guide

## Architecture Overview
- **Backend**: Spring Boot application running on `http://localhost:8080`
- **Frontend**: React (Vite) application running on `http://localhost:5173`
- **Database**: MySQL on `localhost:3306`

## Prerequisites
- Java 17+
- Node.js 16+ & npm
- MySQL server running with database `parknova`
- Maven 3.6+

## Option 1: Run Frontend & Backend Separately (Recommended for Development)

### Step 1: Start the Backend

1. Open a terminal in the project root (`c:\Users\pavan\OneDrive\Desktop\parknova`)
2. Verify MySQL is running and database `parknova` exists:
   ```sql
   CREATE DATABASE IF NOT EXISTS parknova;
   ```

3. Check `application.properties` contains your MySQL credentials:
   ```properties
   spring.datasource.url=jdbc:mysql://localhost:3306/parknova
   spring.datasource.username=root
   spring.datasource.password=8179@Pavan
   ```

4. Run the backend:
   ```bash
   mvn spring-boot:run
   ```
   
   **Expected output**: Application starts on `http://localhost:8080`

### Step 2: Start the Frontend

1. Open a NEW terminal in the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies (first time only):
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   
   **Expected output**: Application available at `http://localhost:5173`

### Step 3: Access the Application

- **Frontend App**: Open `http://localhost:5173` in your browser
- **Backend API**: Base URL is `http://localhost:8080/api`
- **Backend Admin**: `http://localhost:8080/admin`

---

## Option 2: Build Frontend & Serve with Backend (Production-like)

### Step 1: Build the Frontend

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Build the React app:
   ```bash
   npm install
   npm run build
   ```
   
   This will output files to `src/main/resources/static/app/`

### Step 2: Start the Backend

1. Return to project root:
   ```bash
   cd ..
   ```

2. Run the backend:
   ```bash
   mvn spring-boot:run
   ```

3. Access the bundled application:
   - **Bundled Frontend**: `http://localhost:8080/app`
   - **Backend API**: `http://localhost:8080/api`

---

## Connection Details

### API Base URL
The frontend uses the following base URL for API calls:
```javascript
const API_BASE = 'http://localhost:8080/api';
```

### CORS Configuration
CORS is configured to allow requests from:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Alternative frontend port)
- `http://localhost:8080` (Same origin)

### Available API Endpoints
```
GET    /api/slots              - Get all parking slots
GET    /api/stats              - Get parking statistics
GET    /api/active-booking     - Get current user's active booking
POST   /api/book/:slotId       - Book a parking slot
POST   /api/payment/confirm    - Confirm payment
GET    /admin/...              - Admin endpoints
GET    /user/...               - User endpoints
```

---

## Troubleshooting

### Frontend can't connect to backend
1. **Check backend is running**: Visit `http://localhost:8080` in browser
2. **Check CORS**: Ensure browser console shows no CORS errors
3. **Check firewall**: Make sure port 8080 is not blocked

### Database connection errors
```
Error: Connection refused to jdbc:mysql://localhost:3306/parknova
```
- Ensure MySQL is running
- Verify credentials in `application.properties`
- Create database if missing: `CREATE DATABASE parknova;`

### Port already in use
- **Backend (8080)**: Find and kill process on port 8080
- **Frontend (5173)**: Vite will automatically try next available port

**Windows commands**:
```bash
# Check what's using port 8080
netstat -ano | findstr :8080

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Dependencies installation fails
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

---

## Development Workflow

### Hot Reload
- **Backend**: Restart manually or use Spring Boot DevTools (optional)
- **Frontend**: Automatically hot-reloads on file changes

### Making API Calls from Frontend
The frontend already has axios configured:
```javascript
import axios from 'axios';

// In your component
const response = await axios.get('http://localhost:8080/api/slots');
```

### Common Development Tasks

1. **Format code**:
   ```bash
   cd frontend && npm run lint
   ```

2. **Build for production**:
   ```bash
   cd frontend && npm run build
   cd .. && mvn clean package
   ```

3. **Run tests** (if available):
   ```bash
   mvn test
   ```

---

## Quick Start Commands

### Terminal 1: Backend
```bash
cd c:\Users\pavan\OneDrive\Desktop\parknova
mvn spring-boot:run
```

### Terminal 2: Frontend
```bash
cd c:\Users\pavan\OneDrive\Desktop\parknova\frontend
npm run dev
```

Then open:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8080/api

---

## Ports Reference
| Service | Port | URL |
|---------|------|-----|
| Backend API | 8080 | http://localhost:8080 |
| Frontend (Vite) | 5173 | http://localhost:5173 |
| MySQL | 3306 | localhost:3306 |
| Frontend (Bundled) | 8080 | http://localhost:8080/app |

---

## Notes
- Frontend is configured to build to `src/main/resources/static/app/` with base path `/app/`
- Backend has CSRF disabled for API calls (ensure this is secure in production)
- Credentials are in `application.properties` - use environment variables in production
- Database auto-updates schema on startup (`spring.jpa.hibernate.ddl-auto=update`)
