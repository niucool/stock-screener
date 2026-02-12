# Stock Screener

![Stock Screener](./img/sp500-stock-screener.png)

## Table of Contents

- [Stock Screener](#stock-screener)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Features](#features)
  - [Technologies Used](#technologies-used)
    - [Frontend](#frontend)
    - [Backend](#backend)
  - [Project Structure](#project-structure)
  - [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Backend Setup](#backend-setup)
    - [Frontend Setup](#frontend-setup)
  - [Usage](#usage)
    - [Running the Application](#running-the-application)
    - [API Endpoints](#api-endpoints)
      - [1. Get All Stock Data with Interval Filters](#1-get-all-stock-data-with-interval-filters)
      - [2. Get Stock Data for a Specific Symbol](#2-get-stock-data-for-a-specific-symbol)
  - [Filtering Data](#filtering-data)
    - [Applying Filters](#applying-filters)
    - [Preset Filters (Optional)](#preset-filters-optional)
  - [Screenshots](#screenshots)
  - [Contributing](#contributing)
    - [Code of Conduct](#code-of-conduct)
  - [License](#license)
  - [Contact](#contact)

## Overview

**Stock Screener** is a powerful web application designed to help users analyze and filter stock data based on various technical indicators. Leveraging interval-based filters, users can customize their search criteria to identify stocks that meet specific conditions. The application features a responsive and intuitive user interface built with React and Material-UI, coupled with a robust Flask backend that handles data processing and API requests.

## Features

- **Interval-Based Filtering:** Apply `From` and `To` ranges for multiple technical indicators such as Williams %R, EMA of Williams %R, RSI 14, and RSI 21.
- **Real-Time Data Display:** View filtered stock data in an interactive DataGrid with sorting and export capabilities.
- **Detailed Stock Information:** Click on a stock entry to view detailed information in a modal dialog.
- **Preset Filters:** Utilize predefined filter presets for common analysis scenarios like Overbought and Oversold conditions.
- **Responsive Design:** Seamlessly works across various devices and screen sizes.
- **Performance Optimizations:** Implements debouncing to prevent excessive API calls and ensures efficient data loading.

## Technologies Used

### Frontend

- **React:** JavaScript library for building user interfaces.
- **Material-UI (MUI):** React components for faster and easier web development.
- **Axios:** Promise-based HTTP client for making API requests.
- **React Router:** Declarative routing for React applications.
- **Lodash.debounce:** Utility for debouncing functions to optimize performance.

### Backend

- **Flask:** Lightweight WSGI web application framework for Python.
- **Flask-CORS:** Extension for handling Cross-Origin Resource Sharing (CORS).
- **Python:** Programming language for backend development.
- **JSON:** Data format for storing and exchanging stock data.

## Project Structure

```
stock-screener/
├── backend/
│   ├── api/
│   │   ├── app.py
│   │   └── requirements.txt
│   └── data/
│       └── stocks/
│           └── processed/
│               ├── AAPL.json
│               ├── GOOGL.json
│               └── ... other stock data files
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.js
│   │   │   ├── Filters.js
│   │   │   ├── StockTable.js
│   │   │   └── StockDetailDialog.js
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.js
│   │   ├── index.js
│   │   └── ... other React files
│   ├── package.json
│   └── ... other frontend files
├── README.md
└── ... other project files
```

## Installation

### Prerequisites

- **Node.js & npm:** [Download and install](https://nodejs.org/) Node.js (which includes npm).
- **Python 3.7+:** [Download and install](https://www.python.org/downloads/) Python.
- **Virtual Environment (optional but recommended):** To manage Python dependencies.

### Backend Setup

1. **Navigate to the Backend Directory:**

   ```bash
   cd stock-screener/backend/api
   ```

2. **Create and Activate a Virtual Environment (Optional):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**

   Ensure you have a `requirements.txt` file with the following (add more if needed):

   ```text
   Flask
   Flask-CORS
   ```

   Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare Stock Data:**

   Ensure that your stock data JSON files are placed in the `backend/data/stocks/processed/` directory. Each file should be named as `<SYMBOL>.json` (e.g., `AAPL.json`) and contain the necessary fields:

   ```json
   {
       "Symbol": "AAPL",
       "Date": "2025-01-10",
       "Close": 150.25,
       "Williams_R_21": -85.32,
       "EMA_13_Williams_R": -80.15,
       "RSI_14": 45.67,
       "RSI_21": 50.89
   }
   ```

5. **Run the Backend Server:**

   ```bash
   python app.py
   ```

   The server should start on `http://0.0.0.0:5001` with debug mode enabled.

### Frontend Setup

1. **Navigate to the Frontend Directory:**

   ```bash
   cd stock-screener/frontend
   ```

2. **Install Dependencies:**

   Ensure you have a `package.json` with necessary dependencies. If not, initialize and install:

   ```bash
   npm install
   ```

   **Common Dependencies:**

   ```bash
   npm install @mui/material @mui/icons-material @mui/x-data-grid axios lodash.debounce
   ```

3. **Configure Environment Variables (If Needed):**

   If your API base URL differs, you can set it in a `.env` file.

   ```env
   REACT_APP_API_BASE_URL=http://localhost:5001/api
   ```

4. **Run the Frontend Server:**

   ```bash
   npm start
   ```

   The application should open in your default browser at `http://localhost:3000`.

## Usage

### Running the Application

1. **Start the Backend Server:**

   Ensure the Flask backend is running on `http://localhost:5001`.

2. **Start the Frontend Server:**

   Run the React frontend on `http://localhost:3000`.

3. **Access the Application:**

   Open your browser and navigate to `http://localhost:3000`.

### API Endpoints

#### 1. Get All Stock Data with Interval Filters

- **Endpoint:** `/api/stock-all-data`
- **Method:** `GET`
- **Description:** Retrieves all stock data entries that match the specified interval filters.
- **Query Parameters:**
  
  - `williamsR_from` (float): Lower bound for Williams %R.
  - `williamsR_to` (float): Upper bound for Williams %R.
  - `emaWilliamsR_from` (float): Lower bound for EMA(13) of Williams %R.
  - `emaWilliamsR_to` (float): Upper bound for EMA(13) of Williams %R.
  - `rsi14_from` (float): Lower bound for RSI 14.
  - `rsi14_to` (float): Upper bound for RSI 14.
  - `rsi21_from` (float): Lower bound for RSI 21.
  - `rsi21_to` (float): Upper bound for RSI 21.

- **Example Request:**

  ```
  GET http://localhost:5001/api/stock-all-data?williamsR_from=-100&williamsR_to=-80&rsi14_from=30&rsi14_to=70
  ```

- **Success Response:**

  - **Code:** `200 OK`
  - **Content:** JSON array of filtered stock data.

- **Error Responses:**

  - **Code:** `404 Not Found`
    - **Content:** `{"error": "No stock data available"}`
  - **Code:** `500 Internal Server Error`
    - **Content:** `{"error": "Internal Server Error"}`

#### 2. Get Stock Data for a Specific Symbol

- **Endpoint:** `/api/stock-data/<symbol>`
- **Method:** `GET`
- **Description:** Retrieves stock data for the specified symbol.
- **URL Parameters:**
  
  - `<symbol>` (string): Stock symbol (e.g., `AAPL`).

- **Example Request:**

  ```
  GET http://localhost:5001/api/stock-data/AAPL
  ```

- **Success Response:**

  - **Code:** `200 OK`
  - **Content:** JSON object of the stock data for the specified symbol.

- **Error Responses:**

  - **Code:** `404 Not Found`
    - **Content:** `{"error": "Symbol not found"}`
  - **Code:** `500 Internal Server Error`
    - **Content:** `{"error": "Internal Server Error"}`

## Filtering Data

The application allows users to filter stock data based on the following technical indicators using interval-based (`From` and `To`) inputs:

1. **Williams %R (`williamsR`):**
   - **Range:** -100 to 0
   - **Description:** Measures overbought and oversold levels.

2. **EMA(13) of Williams %R (`emaWilliamsR`):**
   - **Range:** Adjust based on your analysis needs (e.g., -100 to 100)
   - **Description:** Exponential Moving Average of Williams %R.

3. **RSI 14 (`rsi14`):**
   - **Range:** 0 to 100
   - **Description:** Relative Strength Index over 14 periods.

4. **RSI 21 (`rsi21`):**
   - **Range:** 0 to 100
   - **Description:** Relative Strength Index over 21 periods.

### Applying Filters

1. **Navigate to the Filters Section:**

   At the top of the application, you'll find input fields labeled with each technical indicator and their corresponding `From` and `To` values.

2. **Set the Desired Ranges:**

   - Enter the lower bound in the `From` field.
   - Enter the upper bound in the `To` field.
   - Ensure that `From` is less than or equal to `To` for each filter.

3. **Apply the Filters:**

   The application uses debouncing to optimize performance, updating the stock data displayed in the table after a short delay once you stop typing.

4. **Reset Filters:**

   Click the **Reset Filters** button to clear all inputs and view the unfiltered stock data.

### Preset Filters (Optional)

If implemented, you can use preset buttons like **Overbought** or **Oversold** to quickly apply common filter configurations.

## Screenshots

*Replace the placeholder descriptions with actual screenshots.*

1. **Home Page:**

   ![Home Page](path_to_home_page_screenshot)

2. **Filter Section:**

   ![Filter Section](path_to_filter_section_screenshot)

3. **Stock Data Table:**

   ![Stock Data Table](path_to_stock_table_screenshot)

4. **Stock Detail Dialog:**

   ![Stock Detail Dialog](path_to_detail_dialog_screenshot)

## Contributing

Contributions are welcome! Please follow these steps to contribute to the project:

1. **Fork the Repository:**

   Click the "Fork" button at the top right corner of the repository page.

2. **Clone Your Fork:**

   ```bash
   git clone https://github.com/florinel-chis/stock-screener.git
   ```

3. **Create a New Branch:**

   ```bash
   git checkout -b feature/YourFeatureName
   ```

4. **Make Changes:**

   Implement your feature or bug fix.

5. **Commit Your Changes:**

   ```bash
   git commit -m "Add feature: YourFeatureName"
   ```

6. **Push to Your Fork:**

   ```bash
   git push origin feature/YourFeatureName
   ```

7. **Create a Pull Request:**

   Navigate to the original repository and create a pull request from your forked branch.

### Code of Conduct

Please adhere to the [Code of Conduct](CODE_OF_CONDUCT.md) in all interactions.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For any inquiries or support, please contact:

- **Name:** Florinel Chis
- **Email:** florinel.chis@gmail.com
- **GitHub:** [florinel-chis](https://github.com/florinel-chis)
- **LinkedIn:** [Florinel Chis](https://www.linkedin.com/in/chisflorinel/)
