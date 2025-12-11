# Link Qualification System

A comprehensive system for qualifying websites based on SEO metrics, traffic data, and keyword relevance.

## Features

- CSV import for website lists with emails and pricing
- Automatic Ahrefs DR and traffic data retrieval
- DataForSEO integration for keyword extraction (up to 1000 pages per site)
- Vector embedding of keywords using Pinecone
- Admin dashboard with authentication
- Guest search interface with filtering
- Automatic deployment to Render.com

## Tech Stack

### Backend
- Python FastAPI
- PostgreSQL database
- Pinecone vector database
- Celery for background tasks
- Redis for caching

### Frontend
- React with TypeScript
- Tailwind CSS
- Recharts for data visualization

## Setup Instructions

### Local Development

1. Clone the repository
2. Set up Python backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up frontend:
   ```bash
   cd frontend
   npm install
   ```

4. Configure environment variables in `.env` files

5. Run the services:
   - Backend: `uvicorn app.main:app --reload`
   - Frontend: `npm start`

## Deployment

Pushes to the main branch automatically deploy to Render.com.