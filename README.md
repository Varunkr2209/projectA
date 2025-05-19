# Job Title Categorization API

A robust and extensible Flask-based REST API that categorizes job titles by extracting:
- **Function**: Broad job domains like Marketing, Sales, Engineering
- **Sub-function**: Specialized areas such as Growth, Backend Development
- **Seniority**: Job level like Entry, Senior, Director, etc.

This API uses alias normalization, regular expressions, and fuzzy matching (via RapidFuzz) for intelligent, high-confidence categorization. It is designed with performance, observability, and extensibility in mind.

---

## 📌 Use Cases

- Structuring HR databases with standardized job taxonomy
- Enhancing analytics on job titles for recruitment platforms
- Cleaning and enriching user-submitted job title data

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

### 2. Run the Server
```bash
python task3.py
```

### 3. Or use Docker
```bash
docker build -t job-title-api .
docker run -p 8000:8000 job-title-api
```

The API will be live at `http://localhost:8000/`

---

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
```json
{
  "title": "Senior Growth Manager"
}
```

#### Example Request (Batch)
```json
{
  "titles": ["Junior Backend Dev", "VP of Sales", "Lead Digital Marketing"]
}
```
#### How to Use:
***Single Title:***

```bash
curl -X POST http://localhost:8000/v1/categorise \
  -H "Content-Type: application/json" \
  -d '{"title": "Senior Software Engineer"}'
```
  
***Multiple Titles:***

```bash
curl -X POST http://localhost:8000/v1/categorise \
  -H "Content-Type: application/json" \
  -d '{"titles": ["Junior Developer", "Marketing Director"]}'
```

***Health Checks:***

bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
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
  "status": "success",
  "version": "v1"
}
```

---

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
