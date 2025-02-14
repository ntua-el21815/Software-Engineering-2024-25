# TOLLIS (Toll Interoperability System)

This project (TOLLIS) provides a unified system for handling toll transactions across multiple stations and operators. Below is an overview of key points inferred from the accompanying project specification (SRS-softeng24-27.docx) and refined build instructions.

## Overview

- Implements a toll interoperability solution where different toll stations can communicate with a central system to register and track transactions.
- Provides a back-end REST API, a CLI interface, and a web-based Portal for comprehensive access and management.
- Incorporates a database layer (MySQL >= 8.0) to store user, transaction, and payment data.

## Main Components

1. **REST API (back-end)**  
   - Handles requests for toll operations, user account management, and system admin tasks.  
   - Built with Python (>= 3.10) using a framework compatible with the project’s needs (e.g., Flask).

2. **CLI Client**  
   - Offers command-line interaction (commands defined in “se2427.py”).  
   - Supports querying and managing transaction data, user information, and more.

3. **Web Portal**  
   - Runs on various web browsers with JavaScript enabled.  
   - Provides a graphical interface to the same functionality exposed by the API and CLI.

## Prerequisites

- Python 3.10 or higher (installed and available in PATH).
- MySQL 8.0 or higher, running locally or accessible from the environment where you deploy.
- A modern web browser (Chrome, Firefox, Microsoft Edge, etc.) with JavaScript enabled.

## Project Structure

- `back-end/rest_api/`  
  Contains the REST API source code and database-related scripts (e.g., `db_create.sql`).

- `cli-client/`  
  Contains the CLI program (`se2427.py`) and any related libraries.

- `scripts/`  
  May include extra scripts for environment setup (Makefiles for different platforms).

- `documentation/`  
  Includes project documentation such as the SRS (Software Requirements Specification).

## Building and Deployment

Below are refined instructions for building, deploying, and running TOLLIS:

1. Clone or download the repository.  
   Example:  
   ```console
   git clone https://github.com/ntua-el21815/Software-Engineering-2024-25.git
   ```

2. Navigate to the project’s root directory (where the Makefile is located).  
   ```console
   cd Software-Engineering-2024-25
   ```

3. Choose the appropriate Makefile:

   - **Windows**: Use the default Makefile.  
   - **macOS / Linux**: Rename “MakefileForMac” to “Makefile” (and remove or rename the default one).  

4. Use one of the following build targets:

   - **Complete Setup and Build** (installs all dependencies, creates the database, generates certificates, etc.):  
     ```console
     make scratch
     ```
     or  
     ```console
     foo@bar: softeng24-27 $ make scratch
     ```
     This command is comprehensive but can be time-consuming. It also automatically creates the database.

   - **Build Without Auto-Creating the Database**:  
     ```console
     make
     ```
     or  
     ```console
     foo@bar: softeng24-27 $ make
     ```
     If you prefer to manage the MySQL database setup yourself, run `db_create.sql` manually (found in `back-end/rest_api/database`) before or after this step.

5. **Running the REST API**:  
   ```console
   make run_api
   ```
   or  
   ```console
   foo@bar: softeng24-27 $ make run_api
   ```
   The API’s address (e.g., https://127.0.0.1:5000) will be displayed in the console.

6. **Running the Web Portal**:  
   ```console
   make run_portal
   ```
   or  
   ```console
   foo@bar: softeng24-27 $ make run_portal
   ```
   The web address for the portal (e.g., https://127.0.0.1:8080) will also be displayed in the console.

## CLI Usage

The CLI client (located in `cli-client/`) can run after you have installed all Python dependencies or after a successful `make`/`make scratch`:

```console
cd cli-client
python ./se2427.py {commands}
```

Typical commands might include initiating transactions, listing user data, or various administrative tasks. Consult the CLI help (`python ./se2427.py --help`) for more details.

## Notes

- If you want to build the project without any automated steps (like database creation), simply avoid `make scratch`. Manage the MySQL setup and certificate generation manually.
- The system’s logging and configuration details can be found in the back-end folder. Adjust them as necessary for your environment.

## Further Information

Refer to the accompanying SRS (SRS-softeng24-27.docx) in the “documentation” directory for a detailed functional and technical breakdown:
- Requirements
- Use cases
- Sequence diagrams
- Data models
- Non-functional requirements

This README is the starting point. The SRS document provides a deeper, comprehensive view of the system’s design and behavior.
