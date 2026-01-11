# AccountBook

A simple web-based accounting book built with Python Flask and MongoDB. It supports conversion between Renminbi (CNY) and Singapore Dollar (SGD), records daily income and expenses, and keeps track of daily exchange rates.

## Directory Structure and File Descriptions

- **app.py**:
  - Core backend file built with the Flask framework.
  - Starts the web server (default port 3000).
  - Connects to the MongoDB database and handles all API requests (balance inquiries, deposits, expenses, history records, exchange rate statistics, etc.).
  - Contains logic to automatically access the Frankfurter API for exchange rate data.

- **templates/index.html**:
  - Frontend interface file.
  - Contains all UI components of the account book: current balance, deposit/expense forms, income/expense charts, exchange rate trend charts, etc.
  - Uses the Fetch API to interact with the backend `app.py`.
  - Uses Chart.js for chart rendering.

- **launcher.py**:
  - Startup script source code.
  - Used to generate the EXE executable file.
  - Includes logic for automatically clearing ports, starting the Flask server, and automatically opening the browser.

- **AccountBook.exe**:
  - The final generated executable program.
  - Windows users can double-click this file to launch the entire application with one click (no manual commands required).
  - Automatically opens the browser to access `http://localhost:3000` upon startup.
  - Closing the console window stops the service completely.

- **pic1.png, pic2.png, pic3.png**:
  - Screenshots demonstrating the frontend interface of the project.

## Environment Dependencies

### Python Version
- **Python 3.9.13**
- Key dependencies:
  - `Flask`: Web framework
  - `pymongo`: MongoDB driver
  - `flask-cors`: Handles cross-origin requests
  - `requests`: Sends HTTP requests (used for fetching exchange rates)

### Database Version
- **MongoDB**: Locally installed version (4.0+ recommended)
- Database Name: `accountBook`
- Collections:
  - `balance`: Stores the current account balance
  - `transactions`: Stores every deposit and expense record

## Usage Instructions
1. Ensure the local MongoDB service is started.
2. Double-click `AccountBook.exe` to start the program.
3. Use the account book in the automatically opened browser window.
