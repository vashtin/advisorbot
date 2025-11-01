# **AdvisorBot - Penn State AI Academic Assistant**

A comprehensive web-based chatbot designed to assist students in exploring Penn State majors, courses, and tuition details.  
AdvisorBot combines **scraped PSU Bulletin data** with **AI-powered responses** to simulate an academic advising experience that’s factual, concise, and interactive.

---

**📁 Project Structure**

advisorbot/
├── backend/ # FastAPI backend and GPT integration
│ ├── main.py # Core API handling chat requests
│ ├── programs.json # Scraped list of majors/programs
│ ├── courses.json # Course details and prerequisites
│ ├── scrape/ # Web scraping utilities
│ │ ├── linkscrape.py
│ │ ├── psutextscrape.py
│ │ ├── courselinksgenerate.py
│ │ └── coursetextscrape.py
│ ├── data/ # Processed JSON datasets
│ ├── .env # OpenAI API key
│ └── requirements.txt # Python dependencies
│
├── frontend/ # User interface
│ ├── index.html # Chat UI layout
│ ├── style.css # Styling (navy background, white chat box)
│ └── script.js # Frontend logic for chat flow
│
├── docs/ # Documentation and diagrams
│ ├── data-flow.md # How scraped data moves through the system
│ └── setup-guide.md # Local setup and environment guide
│
└── README.md # Main documentation file

yaml
Copy code

---

**🚀 Quick Start**

**Run Full Application (Recommended)**

```bash
# Start the backend server
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
Open a new terminal tab:

bash
Copy code
# Start the frontend
cd frontend
python3 -m http.server 5500
Visit http://localhost:5500 in your browser.

🧩 Individual Development

Backend Only

bash
Copy code
cd backend
uvicorn main:app --reload
Frontend Only

bash
Copy code
cd frontend
python3 -m http.server 5500
📚 Documentation

Backend Setup Guide

Data Flow Overview

Scraper Descriptions

🛠️ Development Notes

This project follows a clear separation of concerns:

Frontend: Interactive chat interface styled in HTML/CSS/JS.

Backend: FastAPI app integrating OpenAI GPT with structured JSON data.

Data: Scraped from PSU’s official Bulletin using BeautifulSoup.

Docs: Includes setup guides and architecture diagrams for reproducibility.

🔧 Configuration

To connect to the OpenAI API:

Create a .env file inside /backend

Add:

ini
Copy code
OPENAI_API_KEY= your_api_key_here
Ensure python-dotenv is installed (included in requirements.txt)
