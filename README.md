# Backend AI Agent Service

This backend provides an AI-powered chat endpoint that returns a text response and two charts (as images) for integration with the frontend.

## Tech Stack
- Python 3.9+
- FastAPI
- Plotly
- (Optional) OpenAI or HuggingFace for AI

## Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API
- **POST /chat/**
  - Request: `{ "message": "user input" }`
  - Response: `{ "text": "...", "chart1": "<base64>", "chart2": "<base64>" }`

## Deployment
- Ready for Railway deployment (see Railway docs) 

---

## 1. **Start the Backend Server**

From your project root, run:
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
# source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```
You should see output indicating the server is running at `http://127.0.0.1:8000`.

---

## 2. **Test the /chat/ Endpoint in Postman**

- **Method:** POST
- **URL:** `http://127.0.0.1:8000/chat/`
- **Headers:**  
  - `Content-Type: application/json`
- **Body (raw, JSON):**
  ```json
  {
    "message": "Show me a negotiation analysis"
  }
  ```

- **Expected Response:**
  ```json
  {
    "text": "AI response to: Show me a negotiation analysis",
    "chart1": "<base64 string>",
    "chart2": "<base64 string>"
  }
  ```

The `chart1` and `chart2` fields will be long base64-encoded PNG images.

---

## 3. **Troubleshooting**
- If you get an error about Plotly image export, make sure `kaleido` is installed (`pip install kaleido`).
- If you get a 422 error, check that your JSON body is valid and matches the model.

---

Let me know if you get a successful response or if you encounter any errors! If you want, you can paste the response here and I’ll help you interpret it. 