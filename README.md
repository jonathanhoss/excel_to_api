

## Core Functionalities


1. **User Authentication (Optional)**:    
    - Users can register and log in (if you want to support multi-user systems).

2. **File Management**:
    - **Upload Excel Files**: Users can upload Excel files to the system.
    - **File Storage**: Save the files in a directory or cloud storage and store metadata in a database.

3. **Mapping Inputs/Outputs**:
    - Provide a UI to select cells in the Excel file and map them as **inputs** or **outputs**.
    - Save these mappings in the database.

4. **Perform Calculations**:
    - Accept a JSON payload with input values via an API.
    - Populate the mapped input cells in the Excel file.
    - Recalculate the file and return the mapped outputs.

5. **Dynamic API Generation**:
    - Automatically generate RESTful API endpoints for uploaded Excel files.
    - Use endpoints to perform calculations based on input/output mappings.