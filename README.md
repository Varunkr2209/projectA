# Job Title Categorization API

An enhanced Flask-based API that classifies job titles into:
- **Function** (e.g., Marketing, Engineering, Sales)
- **Sub-function** (e.g., Growth, Backend, Account Management)
- **Seniority** (e.g., Entry, Manager, Director)

---

## Features

- Accepts job titles via a JSON POST request
- Classifies function, sub-function, and seniority using exact and fuzzy logic
- Returns structured JSON output with confidence scoring
- Configuration via YAML and `.env`
- Rate limiting using `flask-limiter`
- Logging and error handling
- Health check and versioned endpoints
- CORS enabled
- Docker-ready

---

## Requirements

Install dependencies using:

```bash
pip install -r requirements.txt
```

### `requirements.txt`
```txt
flask
flask-cors
flask-limiter
gunicorn
PyYAML
python-dotenv
rapidfuzz
```

---

## Running the Server

### Development
```bash
python task3.py
```

### Docker
```bash
docker build -t job-title-api .
docker run -p 8000:8000 job-title-api
```

API will be accessible at:

```
http://localhost:8000/
```

---

## Environment Variables

You can define the following in a `.env` file:

```env
PORT=8000
DEBUG=false
API_VERSION=v1
CONFIG_PATH=config/mappings.yaml
MIN_CONFIDENCE=0.7
```

---

## API Usage

### Health Check
```
GET /health
```

### Categorize Job Title
```
POST /v1/categorise
```

#### Request Header
```
Content-Type: application/json
```

#### Request Body
```json
{
  "title": "Senior Growth Manager"
}
```

#### Example `curl`
```bash
curl -X POST http://localhost:8000/v1/categorise   -H "Content-Type: application/json"   -d '{"title": "Senior Growth Manager"}'
```

#### Response
```json
{
  "function": "Marketing",
  "sub_function": "Growth",
  "seniority": "Senior",
  "confidence": 1.0,
  "matched": true,
  "warnings": [],
  "original_title": "Senior Growth Manager",
  "status": "success",
  "version": "v1"
}
```

---

## Common Errors

| Error | Description |
|-------|-------------|
| `405 Method Not Allowed` | You sent a GET instead of POST |
| `400 Bad Request` | Missing or invalid JSON or title field |

---

## Tools Used
- VS Code
- Postman
- Docker

## Author
-- Varun Kumar
