# SmartBook AI 🤖

SmartBook AI is an AI-powered appointment booking platform built with **Streamlit, LangChain, Groq, and Supabase**. It connects clients with service providers in healthcare, tutoring, and consulting through service discovery, appointment management, and a conversational AI assistant.

## Features

- **Authentication:** Signup, login, session restoration, and logout using Supabase Auth.
- **Client Dashboard:** Search services, check availability, book appointments, view booking history, and cancel bookings.
- **Worker Dashboard:** Create services, manage availability, and view assigned bookings.
- **Worker Applications:** Apply to become a service provider and track application status. Healthcare services require independent credential verification before approval.
- **AI Booking Assistant:** Uses LangChain tools to find services, check real availability, and retrieve the user's bookings.
- **Database Security:** Supabase PostgreSQL, Row Level Security (RLS), and database-backed booking validation.

## Tech Stack

- **Frontend:** Streamlit
- **Language:** Python
- **AI Agent:** LangChain
- **LLM:** Groq
- **Authentication and Database:** Supabase Auth and PostgreSQL
- **Configuration:** python-dotenv

## Architecture

```text
                 Client / Worker
                       |
                       v
               Streamlit Application
                       |
          +------------+------------+
          |            |            |
          v            v            v
    Client          Worker       AI Booking
    Dashboard       Dashboard    Assistant
          |            |            |
          |            |       LangChain Tools
          |            |            |
          +------------+------------+
                       |
                       v
             Authenticated Supabase
                       |
                       v
              PostgreSQL Database
               + RLS + Constraints
```

The Streamlit interface handles user interactions, LangChain connects the AI model to controlled application tools, and Supabase manages authentication and persistent data. Database policies and functions enforce access permissions and booking rules.

## Project Structure

```text
SmartAppointmentAgent/
├── app.py
├── auth.py
├── database.py
├── profiles.py
├── qualifications.py
├── worker_applications.py
├── worker_dashboard.py
├── client_dashboard.py
├── services.py
├── availability.py
├── bookings.py
├── tools.py
├── agent.py
├── chat_ui.py
├── requirements.txt
└── README.md
```

## Setup and Installation

**1. Install dependencies**

```bash
pip install -r requirements.txt
```

**2. Configure environment variables**

Create a `.env` file in the project root:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
GROQ_API_KEY=your_groq_api_key
COOKIES_PASSWORD=your_random_secret
```

Use your own credentials. Never upload the actual `.env` file or API keys to GitHub.

**3. Run the application**

```bash
streamlit run app.py
```

Ensure your Supabase database tables, RLS policies, and required booking functions are configured before using the application.

## Future Improvements

- Automated appointment reminders
- Calendar integration
- Persistent AI conversation history
- Automated testing and cloud deployment
