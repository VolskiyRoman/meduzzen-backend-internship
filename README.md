# FastAPI Application

## Getting Started

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/VolskiyRoman/meduzzen-backend-internship
   
2. Navigate into the project directory:
    ```bash
   cd meduzzen-backend-internship
   
3. Create and activate a virtual environment
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    .\venv\Scripts\activate  # On Windows

4. Install the dependencies:
    ```bash
   pip install -r requirements.txt
   
5. Running the Application
   ```bash
   uvicorn main:app --reload

### Launching Your Application within Docker

#### Build Docker Image

   ```bash
   docker build -t backend_internship .
   docker run -d -p 5000:5000 --name my-fastapi-container backend_internship

#The application will now be accessible at http://localhost:5000.