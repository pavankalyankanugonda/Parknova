# ParkNova - Quick Start

## 🚀 START BOTH FRONTEND AND BACKEND IN 3 STEPS

### Prerequisites Check
- [ ] MySQL is running and database `parknova` exists
- [ ] Java 17+ installed
- [ ] Node.js 16+ installed
- [ ] Ports 8080 and 5173 are available

---

## 🔥 QUICK START (Recommended)

### Terminal 1 - Backend (Port 8080)
```bash
cd c:\Users\pavan\OneDrive\Desktop\parknova
mvn spring-boot:run
```
**Wait until you see**: `ParknovaApplication started in X.XXX seconds`

### Terminal 2 - Frontend (Port 5173)
```bash
cd c:\Users\pavan\OneDrive\Desktop\parknova\frontend
npm install
npm run dev
```
**Wait until you see**: `Local: http://localhost:5173/`

---

## 🌐 OPEN IN BROWSER

Visit: **http://localhost:5173**

---

## ✅ Testing the Connection

1. Open your browser's Developer Tools (F12)
2. Go to Console tab
3. You should NOT see any red CORS errors
4. Check Network tab - API calls to `http://localhost:8080/api/...` should show 200 status

---

## 🛑 STOP THE SERVERS

**Ctrl + C** in both terminals

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────┐
│           Browser (http://localhost:5173)        │
│                   React Frontend                 │
│                   (Vite Dev Server)              │
└────────────────────┬────────────────────────────┘
                     │ API Calls
                     ↓ (CORS Enabled)
┌─────────────────────────────────────────────────┐
│     Backend API Server (http://localhost:8080)   │
│            Spring Boot Application               │
│              (Port 8080 Open)                    │
└────────────────────┬────────────────────────────┘
                     │ Database Queries
                     ↓
┌─────────────────────────────────────────────────┐
│     MySQL Database (localhost:3306)              │
│         Database: parknova                       │
│    (Credentials in application.properties)       │
└─────────────────────────────────────────────────┘
```

---

## 🔧 API Base URL

Frontend uses: `http://localhost:8080/api`

Configured in: `frontend/src/App.jsx` (Line 27)

```javascript
const API_BASE = 'http://localhost:8080/api';
```

---

## 📝 CORS Configuration

Allowed Origins:
- ✅ http://localhost:5173 (Vite Dev)
- ✅ http://localhost:3000 (Alternative)
- ✅ http://localhost:8080 (Same Origin)

Configured in: `src/main/java/com/parknova/security/SecurityConfig.java`

---

## ❌ Common Issues

| Issue | Solution |
|-------|----------|
| `CORS error in browser console` | Backend not running or CORS not configured |
| `Port 8080 already in use` | Kill process on port 8080 or change backend port |
| `Cannot connect to database` | MySQL not running or wrong credentials |
| `Module not found errors` | Run `npm install` in frontend directory |
| `Frontend shows blank page` | Check browser console (F12) for errors |

---

## 📚 Full Setup Guide

See: [SETUP_GUIDE.md](SETUP_GUIDE.md)

For detailed instructions, troubleshooting, and alternate configurations.

---

## 🎯 Next Steps

1. **Start both servers** using commands above
2. **Open http://localhost:5173** in your browser
3. **Test the application** - click around, make bookings, etc.
4. **Check browser console** (F12) for any errors
5. **Check browser Network tab** to see API calls to backend

---

## 💡 Tips

- Frontend hot-reloads on file changes (no restart needed)
- Backend requires restart for Java code changes
- Use Chrome DevTools to inspect API requests
- API calls use axios (see frontend/src/App.jsx)

