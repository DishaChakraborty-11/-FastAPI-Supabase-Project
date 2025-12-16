# 🚀 FastAPI + Supabase + WebSockets

A **production-ready starter template** for building interactive, real-time AI or chat-based applications using **FastAPI**, **Supabase**, and **WebSockets**.

---

## ✨ Features

* ⚡ **FastAPI** for high-performance REST APIs
* 🗄️ **Supabase (PostgreSQL)** for persistent session & event storage
* 🔄 **WebSockets** for real-time, bi-directional communication
* 📦 **Async architecture** using `supabase-py` AsyncClient
* 🌐 **ngrok support** for public testing (Colab / local)
* 🧩 Modular & scalable project structure

---

## 🧠 Use Case

This project manages:

* **Conversation Sessions** (user, start/end time, summary)
* **Conversation Events** (messages, actions, metadata)
* **Live WebSocket communication** between multiple clients

Perfect as a foundation for:

* AI chatbots 🤖
* Multi-user conversation systems
* Real-time dashboards
* Event-driven AI pipelines

---

## 🏗️ Architecture Overview

```
Client (Browser / App)
        │
        │ REST APIs (JSON)
        ▼
   FastAPI Server
        │
        │ Async DB Calls
        ▼
   Supabase (PostgreSQL)
        ▲
        │
        │ WebSockets (Real-time)
        │
   Multiple Clients
```

---

## 🛠️ Prerequisites

* Python **3.9+**
* Supabase Project (URL + anon key)
* ngrok Account (for public URL testing)

---

## ⚙️ Environment Setup

### 1️⃣ Create & Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

---

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🗄️ Supabase Configuration

### 🔑 a. Get Supabase Credentials

1. Open **Supabase Dashboard**
2. Go to **Project Settings → API**
3. Copy:

   * **Project URL**
   * **anon public API key**

---

### 📄 b. Create `.env` File

Create a `.env` file in the project root:

```env
SUPABASE_URL="YOUR_SUPABASE_PROJECT_URL"
SUPABASE_KEY="YOUR_SUPABASE_ANON_KEY"
```

⚠️ **Never commit this file to GitHub**

---

### 🧠 c. Create `execute_sql` Function (Mandatory)

Supabase does **not allow DDL via client by default**. Create this function manually:

1. Open **SQL Editor** in Supabase
2. Click **+ New query**
3. Paste & run:

```sql
CREATE OR REPLACE FUNCTION execute_sql(sql_query TEXT)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    EXECUTE sql_query;
END;
$$;
```

✅ Verify under **Database → Functions**

---

### 📊 d. Create Database Tables

Run the following Python code once:

```python
import os
from supabase import AsyncClient, create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: AsyncClient = create_client(SUPABASE_URL, SUPABASE_KEY)

session_metadata_table_sql = """
CREATE TABLE IF NOT EXISTS session_metadata (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    summary TEXT
);
"""

event_log_table_sql = """
CREATE TABLE IF NOT EXISTS event_log (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES session_metadata(session_id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    event_type TEXT NOT NULL,
    event_data JSONB
);
"""

await supabase.rpc('execute_sql', {'sql_query': session_metadata_table_sql}).execute()
await supabase.rpc('execute_sql', {'sql_query': event_log_table_sql}).execute()
```

---

## ▶️ Running the Application

### 🔐 1️⃣ Authenticate ngrok

```python
import os
os.environ["NGROK_AUTH_TOKEN"] = "YOUR_NGROK_AUTH_TOKEN"
```

---

### 🚦 2️⃣ Start FastAPI + ngrok

```python
from pyngrok import ngrok
import threading, time, os

ngrok.kill()
ngrok.set_auth_token(os.environ["NGROK_AUTH_TOKEN"])

def run_fastapi():
    os.system('uvicorn app:app --host 0.0.0.0 --port 8000')

threading.Thread(target=run_fastapi).start()
time.sleep(5)

public_url = ngrok.connect(8000)
print("FastAPI running at:", public_url)
```

🌍 Use the printed URL to access APIs & WebSockets

---

## 📡 API Endpoints

### 🧩 Sessions

#### ➕ Create Session

`POST /sessions/`

```json
{
  "user_id": "user_123",
  "summary": "Initial conversation"
}
```

---

#### 📄 Get Session

`GET /sessions/{session_id}`

---

### 🧾 Events

#### ➕ Create Event

`POST /events/`

```json
{
  "session_id": "<SESSION_UUID>",
  "event_type": "user_message",
  "event_data": {
    "text": "Hello AI",
    "language": "en"
  }
}
```

---

#### 📚 Get All Events for a Session

`GET /sessions/{session_id}/events`

---

## 🔌 WebSocket Usage

### 🌐 WebSocket Test UI

Open:

```
{PUBLIC_NGROK_URL}/websocket_test
```

### 🧪 How It Works

1. Enter a **Client ID**
2. Click **Connect**
3. Send messages
4. Messages are:

   * echoed back
   * broadcast to all connected clients

---

## 🧱 Key Design Choices

| Technology | Why It’s Used                      |
| ---------- | ---------------------------------- |
| FastAPI    | High performance, async, auto docs |
| Pydantic   | Strong validation & typing         |
| Supabase   | Managed PostgreSQL + scalability   |
| WebSockets | Real-time communication            |
| APIRouter  | Clean & modular architecture       |

---

## 🚀 Next Improvements

* 🔐 Supabase Auth integration
* 🤖 AI response generation
* 📈 Analytics dashboard
* 🧪 Unit & integration tests
* 🐳 Docker support

---

## ⭐ Final Notes

This README is **copy‑paste ready** and GitHub‑friendly. You now have a clean, scalable backend foundation for real‑time AI systems.

Happy building! 🎉
