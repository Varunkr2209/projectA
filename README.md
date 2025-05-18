# Job Title Categorization API

A Flask-based API that categorizes job titles into:
- **Function** (e.g., Marketing, Engineering, Sales)
- **Sub-function** (e.g., Growth, Backend, Account Management)
- **Seniority** (e.g., Entry, Manager, Director)

---

## Features

- Accepts job titles via a JSON POST request
- Classifies function, sub-function, and seniority with confidence score
- Provides warnings for uncertain or unmatched values
- Returns structured JSON output
- Loads mapping data from a YAML file or defaults
- CORS enabled for browser-based clients

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
pyyaml
```

---

## Running the Server

```bash
python task3.py
```

The API will be accessible at:

```
http://localhost:8000/
```

---

#### API Usage
##### Endpoint
```
POST /categorise
```

##### Request Header
```
Content-Type: application/json
```

##### Request Body
```json
{
  "title": "Senior Growth Manager"
}
```

##### Example `curl`
```bash
curl -X POST http://localhost:8000/categorise \
  -H "Content-Type: application/json" \
  -d '{"title": "Senior Growth Manager"}'
```

##### Response
```json
{
  "function": "Marketing",
  "sub_function": "Growth",
  "seniority": "Senior",
  "confidence": 1.0,
  "matched": true,
  "warnings": [],
  "original_title": "Senior Growth Manager"
}
```

---

## Common Errors I faced

| Error | Description |
|-------|-------------|
| `405 Method Not Allowed` | You sent a GET instead of POST |
| `400 Bad Request` | You didn’t send a valid JSON payload or title is missing |

---

## Tools I used
- VS Code
- Postman

## Author
-- Varun Kumar
