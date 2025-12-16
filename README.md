# -FastAPI-Supabase-Project
Project Overview
This project demonstrates a basic FastAPI application integrated with Supabase for data persistence and WebSockets for real-time communication. It allows for the management of conversation sessions and their associated events, providing a foundation for building interactive AI applications.

Setup
To get this project running locally or in a Colab environment, follow these steps.

Prerequisites
Python 3.9+
A Supabase project (you will need its URL and anon key)
An ngrok account (for local testing with a public URL)
1. Environment Setup
First, ensure you have Python installed. It's recommended to use a virtual environment:

python -m venv venv
source venv/bin/activate # On Windows use `venv\Scripts\activate`
2. Installation
Install the required Python dependencies:

pip install -r requirements.txt
3. Supabase Configuration
This application uses Supabase for its database. You need to configure your Supabase project:

a. Obtain Supabase Credentials
Go to your Supabase project dashboard.
Navigate to 'Project Settings' -> 'API'.
Note down your Project URL and the anon (public) API key.
b. Create .env File
Create a file named .env in the root directory of your project (e.g., /content/ in Colab) and add your credentials:

SUPABASE_URL="YOUR_SUPABASE_PROJECT_URL"
SUPABASE_KEY="YOUR_SUPABASE_ANON_KEY"
IMPORTANT: Replace "YOUR_SUPABASE_PROJECT_URL" and "YOUR_SUPABASE_ANON_KEY" with your actual credentials.

c. Create execute_sql Function in Supabase
The Python client uses a custom PostgreSQL function to execute DDL statements. You MUST create this function manually in your Supabase project:

Go to your Supabase project dashboard.

Navigate to 'SQL Editor'.

Click '+ New query'.

Paste and execute the following SQL code:

CREATE OR REPLACE FUNCTION execute_sql(sql_query TEXT)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    EXECUTE sql_query;
END;
$$;
Verify its creation under 'Database' -> 'Functions'.

d. Create Tables
Run the following Python code (if not already done) to create the session_metadata and event_log tables in your Supabase project:

import asyncio
import os
from supabase import AsyncClient, create_client

# Ensure these are your actual credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
try:
    supabase: AsyncClient = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Supabase client initialized successfully.")
except Exception as e:
    print(f"Error initializing Supabase client: {e}")
    supabase = None

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

async def create_supabase_tables_combined():
    if supabase is None:
        print("Supabase client is not initialized. Cannot create tables.")
        return

    try:
        print("Attempting to create 'session_metadata' table...")
        await supabase.rpc('execute_sql', {'sql_query': session_metadata_table_sql}).execute()

        print("Attempting to create 'event_log' table...")
        await supabase.rpc('execute_sql', {'sql_query': event_log_table_sql}).execute()

        print("Tables 'session_metadata' and 'event_log' creation process completed. Check your Supabase dashboard to verify.")

    except Exception as e:
        print(f"Error creating Supabase tables: {e}")

await create_supabase_tables_combined()
Running the Application
To run the FastAPI application and make it publicly accessible (e.g., in Colab), you'll use uvicorn and ngrok.

1. Authenticate ngrok
Obtain your ngrok auth token from ngrok.com/signup and set it in your environment or directly in the Colab cell:

# In your environment (e.g., in a Colab cell before running the app)
os.environ["NGROK_AUTH_TOKEN"] = "YOUR_NGROK_AUTH_TOKEN"
2. Start FastAPI with Uvicorn and ngrok
Execute the following Python code:

from pyngrok import ngrok
import os
import threading
import time

# Terminate any existing ngrok tunnels
ngrok.kill()

# Authenticate ngrok (replace 'YOUR_NGROK_AUTH_TOKEN' with your actual token)
NGROK_AUTH_TOKEN = os.environ.get("NGROK_AUTH_TOKEN", "YOUR_NGROK_AUTH_TOKEN") # Fallback for direct execution
ngrok.set_auth_token(NGROK_AUTH_TOKEN)

# Start FastAPI app with Uvicorn in a separate thread
def run_fastapi():
    os.system('uvicorn app:app --host 0.0.0.0 --port 8000')

fastapi_thread = threading.Thread(target=run_fastapi)
fastapi_thread.start()

time.sleep(5) # Give FastAPI app some time to start

# Open an ngrok tunnel to the FastAPI app's port (8000)
public_url = ngrok.connect(8000)
print(f"FastAPI app is running at: {public_url}")
This will print a public URL (e.g., https://xxxx.ngrok-free.dev) that you can use to access your FastAPI application.

API Endpoints
The application provides the following RESTful API endpoints for managing sessions and events:

Sessions
POST /sessions/

Description: Creates a new conversation session.
Request Body (SessionMetadata Pydantic model):
{
    "user_id": "some_user_id",
    "summary": "Initial summary of the conversation"
}
(session_id, start_time, end_time are automatically handled or optional).
Response: 201 Created with the created SessionMetadata object.
GET /sessions/{session_id}

Description: Retrieves a specific session's metadata.
Path Parameter: session_id (UUID of the session).
Response: 200 OK with the SessionMetadata object, or 404 Not Found if the session does not exist.
Events
POST /events/

Description: Creates a new event entry associated with a session.
Request Body (EventLog Pydantic model):
{
    "session_id": "<UUID_OF_EXISTING_SESSION>",
    "event_type": "user_message",
    "event_data": {
        "text": "Hello, AI!",
        "language": "en"
    }
}
(event_id, timestamp are automatically handled).
Response: 201 Created with the created EventLog object.
GET /sessions/{session_id}/events

Description: Retrieves all events for a given session, ordered by timestamp.
Path Parameter: session_id (UUID of the session).
Response: 200 OK with a list of EventLog objects, or an empty list if no events are found.
WebSocket Usage
The application includes a WebSocket endpoint for real-time communication.

1. Access the WebSocket Test Page
Open your browser and navigate to the /websocket_test endpoint of your public ngrok URL (e.g., https://xxxx.ngrok-free.dev/websocket_test).

2. Interact with the WebSocket
Enter a Client ID (e.g., user1).
Click 'Connect'.
Type messages into the Message input field and click 'Send'. Messages will be echoed back to you and broadcast to all connected clients.
Key Design Choices
FastAPI: Chosen for its high performance, modern Python type hints, and automatic OpenAPI documentation, making API development efficient and robust.
Pydantic: Integrated with FastAPI for data validation, serialization, and deserialization, ensuring data integrity and clear API contracts.
Supabase: Used as the backend-as-a-service for its PostgreSQL database, authentication, and real-time capabilities. The supabase-py AsyncClient facilitates asynchronous database interactions.
WebSockets: Implemented for real-time, bi-directional communication, enabling instant updates and interactive features for AI applications.
Modularity: The application structure uses an APIRouter to organize API endpoints, promoting maintainability and scalability.
