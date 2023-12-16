# Credit Approval Project

This project aims to demonstrate credit approval workflows using Django and Docker.

## Prerequisites

- Python (3.9.12 recommended)
- Docker

## Setup Instructions

### 1. Clone the Repository

bash

git clone https://github.com/Ad-30/Credit-Approval.git
cd Credit-Approval

# Navigate to the project directory
cd Credit-Approval

# Create a virtual environment (optional but recommended)
python -m venv myenv

# Activate the virtual environment (for MacOS/Linux)
source myenv/bin/activate

# Activate the virtual environment (for Windows)
myenv\Scripts\activate

# Ensure you're in the project directory and virtual environment is activated
pip install -r requirements.txt


# Make migrations
python manage.py makemigrations
python manage.py migrate

# Run the Django development server
python manage.py runserver


Running with Docker
1. Build Docker Image
bash
Copy code
# Ensure you're in the project directory
docker build -t credit-approval .
2. Run Docker Container
bash
Copy code
docker run -p 8000:8000 credit-approval
