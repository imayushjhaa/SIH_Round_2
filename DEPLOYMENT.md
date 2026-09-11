# Deployment Guide

## Prerequisites
- Python 3.10+
- Node.js 18+
- Git

## Backend Deployment

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Generate Data & Train Model
```bash
python generate_data.py
python train_model.py
```

### 3. Set Environment Variables
```bash
export FRONTEND_URL=https://your-frontend-domain.com
```

### 4. Run Backend Server
```bash
# Development
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production (using gunicorn)
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Frontend Deployment

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Update Production Environment
Edit `frontend/.env.production`:
```env
VITE_BACKEND_URL=https://your-backend-domain.com
```

### 3. Build for Production
```bash
npm run build
```

### 4. Deploy
The `dist/` folder contains the production build. Deploy to:
- Vercel: `vercel deploy`
- Netlify: `netlify deploy --prod`
- Static hosting: Upload `dist/` contents

## Environment Variables

### Backend
- `FRONTEND_URL`: Frontend domain for CORS (optional, defaults to localhost)

### Frontend
- `VITE_BACKEND_URL`: Backend API URL (required for production)

## Health Check
- Backend: `curl http://localhost:8000/api/dashboard/summary`
- Frontend: Open browser to `http://localhost:5173`

## Production Checklist
- [ ] Update `frontend/.env.production` with actual backend URL
- [ ] Set `FRONTEND_URL` environment variable on backend server
- [ ] Run `generate_data.py` and `train_model.py` on production server
- [ ] Verify `backend/parcels.geojson` exists (30 parcels)
- [ ] Test CORS by accessing frontend from production domain
- [ ] Verify all API endpoints return data
- [ ] Check map renders all 30 parcels correctly
