# Quantum Synth - Project Structure

```
quantum-synth/
│
├── README.md                    # Project overview
├── DEVELOPMENT.md              # Complete development guide
├── setup.sh                    # Quick setup script
├── docker-compose.yml          # Docker orchestration
├── .gitignore                  # Git ignore rules
│
├── backend/                    # Django Backend
│   ├── config/                 # Django project settings
│   │   ├── __init__.py        # Celery integration
│   │   ├── settings.py        # Django settings
│   │   ├── urls.py            # URL routing
│   │   ├── celery.py          # Celery configuration
│   │   ├── wsgi.py            # WSGI application
│   │   └── asgi.py            # ASGI application
│   │
│   ├── quantumsynth/          # Main Django app
│   │   ├── models.py          # Database models (QuantumPatch, ProcessedSample)
│   │   ├── views.py           # API views
│   │   ├── serializers.py     # DRF serializers
│   │   ├── tasks.py           # Celery tasks (quantum processing)
│   │   ├── urls.py            # App URL routing
│   │   ├── admin.py           # Django admin config
│   │   └── apps.py            # App configuration
│   │
│   ├── manage.py              # Django management script
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Docker image for backend
│   └── .env.example           # Environment variables template
│
└── frontend/                   # React Frontend
    ├── src/
    │   ├── components/
    │   │   ├── QuantumSynth.tsx      # Main synth component
    │   │   └── QuantumSynth.css      # Component styles
    │   │
    │   ├── services/
    │   │   └── api.ts                # Backend API client
    │   │
    │   ├── App.tsx                   # Main App component
    │   ├── App.css                   # App styles
    │   ├── main.tsx                  # Entry point
    │   └── index.css                 # Base styles
    │
    ├── index.html                    # HTML template
    ├── package.json                  # Node dependencies
    ├── tsconfig.json                 # TypeScript config
    ├── tsconfig.node.json            # TypeScript config for Vite
    ├── vite.config.ts                # Vite configuration
    └── Dockerfile                    # Docker image for frontend
```

## Key Files Explained

### Backend Core Files

**`backend/config/settings.py`**
- Django settings: database, CORS, REST framework, Celery
- Update ALLOWED_HOSTS and SECRET_KEY for production

**`backend/quantumsynth/models.py`**
- `QuantumPatch`: Stores quantum processing presets
- `ProcessedSample`: Caches processed audio

**`backend/quantumsynth/tasks.py`**
- `process_quantum_audio`: Main Celery task for quantum processing
- Uses quantumaudio library to encode/decode audio

**`backend/quantumsynth/views.py`**
- `process_audio`: Upload audio, start async processing
- `task_status`: Check Celery task progress
- `quick_process`: Synchronous processing for short clips

### Frontend Core Files

**`frontend/src/components/QuantumSynth.tsx`**
- Main UI component with keyboard and controls
- Generates audio with Tone.js
- Sends to backend, polls for results, plays output

**`frontend/src/services/api.ts`**
- Axios client for backend communication
- Functions: processAudio, checkTaskStatus, getPatches

**`frontend/vite.config.ts`**
- Vite dev server configuration
- Proxy /api requests to Django backend

## Tech Stack Summary

### Backend
- **Django 5.0**: Web framework
- **Django REST Framework**: API endpoints
- **Celery**: Async task processing
- **Redis**: Message broker
- **quantumaudio**: Quantum audio encoding/decoding
- **Qiskit**: Quantum circuit execution
- **librosa/soundfile**: Audio processing

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server
- **Tone.js**: Web audio synthesis
- **Axios**: HTTP client

### Infrastructure
- **Docker Compose**: Local development orchestration
- **SQLite**: Default database (PostgreSQL for production)
- **Redis**: Celery broker and result backend

## Quick Commands Reference

### Setup
```bash
./setup.sh                    # Run automated setup
```

### Development
```bash
# Backend
cd backend
python manage.py runserver

# Celery
celery -A config worker -l info

# Frontend
cd frontend
npm run dev
```

### Docker
```bash
docker-compose up            # Start all services
docker-compose down          # Stop all services
docker-compose logs -f       # View logs
```

### Database
```bash
python manage.py migrate                # Run migrations
python manage.py makemigrations         # Create migrations
python manage.py createsuperuser        # Create admin user
```

### Testing
```bash
# Backend tests
python manage.py test

# Frontend tests
npm run test
```

## Environment Variables

Create `backend/.env` from `.env.example`:
```bash
DEBUG=True
SECRET_KEY=your-secret-key-here
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Ports

- Frontend Dev Server: 5173
- Django Backend: 8000
- Redis: 6379

## What You Have

✅ Complete Django backend with REST API
✅ Celery async task processing
✅ React + TypeScript frontend
✅ Quantum audio processing integration
✅ Docker support for easy deployment
✅ Development documentation
✅ Ready-to-use quantum synth interface

## Next: Start Building!

1. Run `./setup.sh` or follow manual setup in DEVELOPMENT.md
2. Start all three services (Django, Celery, Frontend)
3. Open http://localhost:5173
4. Click notes and hear quantum-processed audio!

Then customize it to your vision. This is YOUR quantum instrument now! 🎵⚛️
