# Job Title Categorization API

<<<<<<< HEAD
An enhanced Flask-based API that classifies job titles into:
- **Function** (e.g., Marketing, Engineering, Sales)
- **Sub-function** (e.g., Growth, Backend, Account Management)
- **Seniority** (e.g., Entry, Manager, Director)
=======
A robust and extensible Flask-based REST API that categorizes job titles by extracting:
- **Function**: Broad job domains like Marketing, Sales, Engineering
- **Sub-function**: Specialized areas such as Growth, Backend Development
- **Seniority**: Job level like Entry, Senior, Director, etc.

This API uses alias normalization, regular expressions, and fuzzy matching (via RapidFuzz) for intelligent, high-confidence categorization. It is designed with performance, observability, and extensibility in mind.
>>>>>>> 0b6ac3e (Readme)

---

## 📌 Use Cases

<<<<<<< HEAD
- Accepts job titles via a JSON POST request
- Classifies function, sub-function, and seniority using exact and fuzzy logic
- Returns structured JSON output with confidence scoring
- Configuration via YAML and `.env`
- Rate limiting using `flask-limiter`
- Logging and error handling
- Health check and versioned endpoints
- CORS enabled
- Docker-ready
=======
- Structuring HR databases with standardized job taxonomy
- Enhancing analytics on job titles for recruitment platforms
- Cleaning and enriching user-submitted job title data
>>>>>>> 0b6ac3e (Readme)

---

## ⚙️ Features

-  Accepts both single and batch job title inputs via JSON
-  Intelligent fuzzy and regex-based matching
-  Confidence scoring and warning reporting
-  Fast with in-memory caching and thread pool processing
-  Health and readiness endpoints for observability
-  Deploy-ready with Docker and Gunicorn
-  Includes CORS, rate-limiting, and secure response headers

---

## 🧪 Quick Start

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

<<<<<<< HEAD
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
=======
### 2. Run the Server
>>>>>>> 0b6ac3e (Readme)
```bash
python task3.py
```

<<<<<<< HEAD
### Docker
=======
### 3. Or use Docker
>>>>>>> 0b6ac3e (Readme)
```bash
docker build -t job-title-api .
docker run -p 8000:8000 job-title-api
```
<<<<<<< HEAD

API will be accessible at:
=======
>>>>>>> 0b6ac3e (Readme)

The API will be live at `http://localhost:8000/`

---

<<<<<<< HEAD
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
=======
## API Endpoints

### Categorization
```
POST /v1/categorise
```

#### Request Headers
```http
Content-Type: application/json
```

#### Example Request (Single)
>>>>>>> 0b6ac3e (Readme)
```json
{
  "title": "Senior Growth Manager"
}
```

<<<<<<< HEAD
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
=======
#### Example Request (Batch)
```json
{
  "titles": ["Junior Backend Dev", "VP of Sales", "Lead Digital Marketing"]
}
```

#### Sample Response
```json
{
  "results": [
    {
      "function": "Engineering",
      "sub_function": "Backend Development",
      "seniority": "Entry",
      "confidence": 0.85,
      "matched": true,
      "warnings": [],
      "original_title": "Junior Backend Dev",
      "processing_time_ms": 14.2
    }
  ],
  "count": 1,
>>>>>>> 0b6ac3e (Readme)
  "status": "success",
  "version": "v1"
}
```

---

<<<<<<< HEAD
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
=======
### Health & Maintenance
- `GET /health` – Basic service uptime check
- `GET /ready` – Readiness probe for config & service health
- `POST /reload-config` – Reloads YAML config mappings dynamically

---

##  Configuration

Environment variables can control:
- `CONFIG_PATH`: Path to YAML file for function, seniority, and alias mappings
- `MIN_CONFIDENCE`: Minimum match confidence (default: 0.7)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Enables Flask debug mode

Default mappings are used if the config file is missing.

---

## YAML Mapping Format

Example `mappings.yaml`:

```yaml
functions:
  Marketing:
    digital: "Digital Marketing"
    content: "Content Marketing"
  Sales:
    account: "Account Management"

seniority:
  junior: "Entry"
  lead: "Manager"

aliases:
  mgr: "manager"
  eng: "engineer"
```

---

##  Tech Stack

- **Flask** – Web server
- **RapidFuzz** – High-performance fuzzy matching
- **Pydantic** – Settings and validation
- **Flask-Caching** – Response caching
- **Flask-Limiter** – API rate limiting
- **Gunicorn** – WSGI server for deployment
- **Docker** – Containerization

---

## Author

Varun Kumar

---

## 📄 License

This project is open-source and free to use under the MIT License.
>>>>>>> 0b6ac3e (Readme)
