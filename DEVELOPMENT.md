# Quantum Synth - Development Guide

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- Redis (for Celery)

### Option 1: Manual Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

#### Start Celery Worker (in new terminal)
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
celery -A config worker -l info
```

#### Frontend Setup (in new terminal)
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Option 2: Quick Setup Script
```bash
chmod +x setup.sh
./setup.sh
```

### Option 3: Docker Compose
```bash
docker-compose up
```

## Architecture

```
┌─────────────┐
│   Browser   │
│  (React +   │
│   Tone.js)  │
└──────┬──────┘
       │ HTTP/REST
       ▼
┌─────────────┐      ┌─────────┐
│   Django    │◄─────┤  Redis  │
│   Backend   │      └─────────┘
└──────┬──────┘           ▲
       │                  │
       │              ┌───┴────┐
       └──────────────┤ Celery │
                      └────────┘
                      Quantum Processing
```

## API Endpoints

### Process Audio
```http
POST /api/quantum/process/
Content-Type: multipart/form-data

{
  "audio": <file>,
  "scheme": "qpam",
  "shots": 4000,
  "buffer_size": 256
}

Response:
{
  "task_id": "abc-123",
  "status": "processing"
}
```

### Check Task Status
```http
GET /api/quantum/task/{task_id}/

Response:
{
  "task_id": "abc-123",
  "status": "SUCCESS",
  "result": {
    "audio": [...],
    "metadata": {
      "scheme": "qpam",
      "shots": 4000,
      "sample_rate": 22050
    }
  }
}
```

### Quantum Patches (CRUD)
```http
GET    /api/quantum/patches/
POST   /api/quantum/patches/
GET    /api/quantum/patches/{id}/
PUT    /api/quantum/patches/{id}/
DELETE /api/quantum/patches/{id}/
```

## Development Workflow

### 1. Run All Services
```bash
# Terminal 1: Backend
cd backend && source venv/bin/activate
python manage.py runserver

# Terminal 2: Celery
cd backend && source venv/bin/activate
celery -A config worker -l info

# Terminal 3: Frontend
cd frontend
npm run dev
```

### 2. Access Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/quantum/
- Django Admin: http://localhost:8000/admin/

### 3. Test the Flow
1. Open http://localhost:5173
2. Click a note (e.g., C4)
3. Watch the status update as it:
   - Generates audio with Tone.js
   - Sends to Django backend
   - Processes through quantum circuit (Celery)
   - Returns processed audio
   - Plays the result

## Quantum Schemes

### QPAM (Quantum Probability Amplitude Modulation)
- Best for: Mono audio
- Characteristics: Cleanest reconstruction
- Use when: You want minimal quantum artifacts

### SQPAM (Single-Qubit PAM)
- Best for: Efficient mono encoding
- Characteristics: Balanced quality/efficiency
- Use when: Processing longer clips

### QSM (Quantum State Modulation)
- Best for: Mono audio with phase information
- Characteristics: More quantum noise
- Use when: You want creative quantum effects

### MQSM (Multi-channel QSM)
- Best for: Stereo audio
- Characteristics: Preserves channel separation
- Use when: Processing stereo content

## Customization Ideas

### Add New Quantum Effects
Edit `backend/quantumsynth/tasks.py`:
```python
def apply_quantum_effect(circuit):
    # Add custom gates here
    circuit.h(0)  # Hadamard gate
    circuit.rx(np.pi/4, 1)  # Rotation
    return circuit
```

### Add Presets
Create patches via Django admin or API:
```python
QuantumPatch.objects.create(
    name="Lo-Fi Quantum",
    scheme="qsm",
    shots=2000,  # Lower = more noise
    buffer_size=128
)
```

### Add More Waveforms
Edit `frontend/src/components/QuantumSynth.tsx`:
```typescript
const synth = new Tone.Synth({
  oscillator: { 
    type: 'triangle'  // Try: sine, square, sawtooth, triangle
  }
});
```

## Performance Tuning

### Buffer Size
- Smaller (128): Faster processing, more chunks
- Larger (512): Slower processing, fewer chunks
- Default (256): Good balance

### Quantum Shots
- 1000-2000: Fast, lo-fi, noisy
- 4000-6000: Balanced
- 7000-8000: High quality, slow

### Caching
The `ProcessedSample` model caches results. Clear old samples:
```bash
python manage.py shell
>>> from quantumsynth.models import ProcessedSample
>>> ProcessedSample.objects.filter(created_at__lt='2025-01-01').delete()
```

## Troubleshooting

### "Cannot connect to Redis"
```bash
# Start Redis
redis-server

# Or with Docker
docker run -p 6379:6379 redis:7-alpine
```

### "Module not found: quantumaudio"
```bash
cd backend
source venv/bin/activate
pip install quantumaudio
```

### "CORS errors"
Check `backend/config/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite
]
```

### "Task takes forever"
- Reduce buffer_size (try 128)
- Reduce shots (try 2000)
- Check Celery worker is running

## Next Steps

### Enhancements to Build
1. **File upload**: Let users upload their own audio
2. **WebSocket**: Real-time processing updates
3. **Visualizer**: Show quantum circuit or waveform
4. **Presets library**: Save/share quantum patches
5. **Authentication**: User accounts and saved projects
6. **Advanced controls**: More quantum parameters
7. **MIDI support**: Connect MIDI keyboard
8. **Effects chain**: Multiple quantum processors

### Production Deployment
1. Set DEBUG=False in settings
2. Configure production database (PostgreSQL)
3. Set up proper SECRET_KEY
4. Configure static files (collectstatic)
5. Use gunicorn for Django
6. Use nginx as reverse proxy
7. Set up proper Redis instance
8. Monitor Celery with Flower

## Resources

- quantumaudio docs: https://quantumaudio.readthedocs.io
- Qiskit docs: https://qiskit.org/documentation/
- Tone.js docs: https://tonejs.github.io/
- Django docs: https://docs.djangoproject.com/
- Celery docs: https://docs.celeryq.dev/

## Contributing

This is your project now! Some ideas:
- Add support for other quantum backends (IBM Quantum, AWS Braket)
- Implement quantum machine learning for generative music
- Create a library of quantum audio effects
- Build a collaborative online DAW with quantum processing

Happy quantum music making! 🎵⚛️
