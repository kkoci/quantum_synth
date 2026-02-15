# Quantum Synth

A web-based synthesizer that processes audio through quantum circuits using the quantumaudio library.

## Architecture

- **Backend**: Django + Django REST Framework + Celery
- **Frontend**: React + TypeScript + Tone.js
- **Quantum**: quantumaudio + Qiskit

## Project Structure

```
quantum-synth/
├── backend/
│   ├── config/              # Django settings
│   ├── quantumsynth/        # Main Django app
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── package.json
│   └── tsconfig.json
├── docker-compose.yml
└── README.md
```

## Quick Start

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Start Celery Worker

```bash
celery -A config worker -l info
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

Create `backend/.env`:
```
DEBUG=True
SECRET_KEY=your-secret-key-here
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
```

## API Endpoints

- `POST /api/quantum/process/` - Process audio through quantum circuit
- `GET /api/quantum/task/{task_id}/` - Get task status
- `GET /api/quantum/patches/` - List available quantum patches
- `POST /api/quantum/patches/` - Create new quantum patch

## Development

This is a basic scaffold. You'll want to add:
- Authentication
- File upload size limits
- Audio format validation
- More quantum circuit transformations
- Preset management
- WebSocket support for real-time updates


Each scheme has its own "sonic fingerprint":

| Scheme | Speed | Noise Level | Character |
|--------|-------|-------------|-----------|
| QPAM | Fast (~10s) | High | Clean quantum noise, simple artifacts |
| SQPAM | Slow (~10min) | Very High | More complex quantum degradation |
| QSM | Medium-Slow | Medium-High | Different noise texture |
| MQSM | Slow (~1min) | Lower | Pitch distortion + stereo effects |

