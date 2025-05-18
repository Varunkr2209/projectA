# Job Title Categorization API

A simple Flask-based API that classifies job titles into:
- **Function** (e.g., Marketing, Sales)
- **Sub-function** (e.g., Growth, Account Management)
- **Seniority** (e.g., Entry, Manager, Director)

---

## Features

- Accepts job titles via a JSON POST request
- Extracts function, sub-function, and seniority level
- Returns structured JSON output
- Easy to test with Postman, Hoppscotch, or curl
- Optional: CORS enabled for browser testing

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
```

---

## Running the Server

```bash
python app.py
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
  "matched": true
}
```

---

## Common Errors I faced

| Error | Description |
|-------|-------------|
| `405 Method Not Allowed` | You sent a GET instead of POST |
| `400 Bad Request` | You didn’t send a valid JSON payload |

---

## Tools I used
- VS Code
- Postman

## Auther
-- Varun Kumar