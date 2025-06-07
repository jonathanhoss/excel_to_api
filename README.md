## Documentation

### Overview
This project provides a web application to turn Excel files into dynamic RESTful APIs. Users can upload Excel files, define input/output mappings, and expose calculations as API endpoints.

### Features

- **User Authentication:** Register and log in to manage your files and calculations.
- **Excel File Management:** Upload, list, and delete Excel files.
- **Calculation Mapping:** Define which cells are inputs and outputs for each calculation.
- **Run Calculations:** Provide input values via web forms or API, and receive calculated outputs.
- **Dynamic API Endpoints:** Each calculation is accessible via a unique RESTful endpoint.

### Usage

#### 1. Register & Login

- Visit `/register` to create an account.
- Login at `/login`.

#### 2. Upload Excel Files

- Go to the Home page after login.
- Use the upload form to add `.xlsx` files.

#### 3. Create Calculations

- Click "Create New Calculation".
- Select an Excel file, name the calculation, and specify input/output cells (e.g., `DATA!B1, DATA!B2`).

#### 4. Run Calculations

- From the Home page, click "Run" next to a calculation.
- Enter input values and submit to see results.

#### 5. Use the API

- Visit `/api` to see all calculation endpoints.
- Example API call:
  ```
  curl -X GET "http://localhost:5000/calculation/api/<calculation_id>?INPUT1=val1&INPUT2=val2"
  ```

### Project Structure

- `app/` – Main application code (models, routes, services, repositories)
- `uploads/` – Uploaded Excel files
- `instance/` – SQLite database
- `tests/` – Unit tests


### Install
Install dependencies:
```
pip install -r requirements.txt
```

Run the app:
```
python run.py
```

### Docker Deployment

You can run the application using Docker:

1. **Build the Docker image:**
   ```
   docker build -t excel-to-api .
   ```

2. **Run the container:**
   ```
   docker run -p 5000:5000 excel-to-api
   ```

This will start the app on [http://localhost:5000](http://localhost:5000).


## TODOS
- Optimize recalculations → cache results (don’t always recalculate Excel, store results in JSON).
- Add some tests
- Support custom names for calculations in the API.