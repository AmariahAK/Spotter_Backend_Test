# Route & Log Planner

## Overview
The **Route & Log Planner** is a full-stack web application designed to help drivers plan their routes and generate ELD (Electronic Logging Device) logs based on trip details. Built with **Django** for the backend and **React** (TypeScript, Vite) for the frontend, the app ensures compliance with driving regulations by automatically generating logs for driving, on-duty, off-duty, and sleeper berth hours.

## Features
- **Route Calculation:** Automatically generates a route between locations using OpenRouteService.
- **ELD Log Generation:** Computes daily events (driving, rest periods, etc.) based on regulatory constraints.
- **Interactive Map:** Displays the planned route dynamically.
- **Driver Input Form:** Users enter their trip details, including locations and hours used.
- **State Management:** React manages trip data and updates the UI accordingly.

## Tech Stack
### Frontend
- **React (Vite + TypeScript)** – For a fast and optimized user experience.
- **Axios** – Handles API calls to the backend.
- **Leaflet.js / OpenRouteService** – Provides dynamic mapping and route visualization.

### Backend
- **Django (Django REST Framework)** – Handles API requests and processes trip planning.
- **OpenRouteService API** – Used for geocoding and route calculation.
- **PostgreSQL** – Stores trip and log data.

## Setup Instructions
### Prerequisites
Ensure you have the following installed:
- **Node.js** (for frontend dependencies)
- **Python 3.x** (for Django backend)
- **PostgreSQL** (or update settings for another database)

### Installation
#### Clone the Repository
```sh
git clone https://github.com/AmariahAK/Spotter_Frontend_Test.git frontend
cd frontend
```

```sh
git clone https://github.com/AmariahAK/Spotter_Backend_Test.git backend
cd backend
```

#### Backend Setup
1. Navigate to the backend directory:
   ```sh
   cd backend
   ```
2. Create a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Apply migrations:
   ```sh
   python manage.py migrate
   ```
5. Start the backend server:
   ```sh
   python manage.py runserver
   ```

#### Frontend Setup
1. Navigate to the frontend directory:
   ```sh
   cd ../frontend
   ```
2. Install dependencies:
   ```sh
   npm install
   ```
3. Start the frontend server:
   ```sh
   npm run dev
   ```

The frontend should now be running at `http://localhost:5173`.

## Usage
1. Open the app in your browser.
2. Enter the **current location**, **pickup location**, **drop-off location**, and **hours used**.
3. Click "Calculate Route."
4. View the **updated map and generated log sheet**.

## Challenges & Solutions
- **Map Defaulted to London:** Fixed by ensuring the backend correctly formatted route geometry and dynamically centering the map.
- **Plain UI:** Improved by adding a light gray background, card shadows, and spacing adjustments.

## Future Improvements
- **Enhanced UI:** More polished styling with better colors and layout.
- **Deployment:** Plan to deploy the frontend on **Vercel** and the backend on **Railway or Heroku**.
- **Additional Features:** Implement fuel stop recommendations and advanced ELD rules.

## Contributing
Pull requests are welcome! If you’d like to contribute, please open an issue first to discuss any major changes.

## License
MIT License

## Contact
- GitHub: [AmariahAK](https://github.com/AmariahAK)
- Email: amariah.abish@gmail.com

