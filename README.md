Here’s a detailed **README.md** file for your GitHub repository based on all the information you’ve provided:

---

# Gitleaks Detection Tool

This repository contains a Python script and Docker image for running [Gitleaks](https://github.com/gitleaks/gitleaks), a tool for detecting secrets and sensitive information in codebases. The project includes unit tests using `pytest` and offers flexibility to run via the terminal, PyCharm, or Docker.

---

## **Features**
- **Python script** for running Gitleaks with customizable arguments.
- **Dockerized version** of the tool for easy containerized execution.
- Structured output handling with Pydantic models.
- Comprehensive error handling and logging.
- Unit tests for validating various scenarios.

---

## **Setup Instructions**

### **Prerequisites**
1. Python 3.10+ installed on your system.
2. Docker installed on your system.
3. Libraries required: `pytest`, `pydantic`.

---

### **Installation**
1. Clone this repository:
    ```bash
    git clone https://github.com/OmarAboRabea1/jit_task.git
    cd jit_task
    git checkout master
    ```

2. Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Install Docker if not already installed. Follow the [official instructions](https://docs.docker.com/get-docker/).

---

## **Usage**

### **Python Script**
The main script for running Gitleaks is `gitleaks_detection.py`.

#### **Run the Script**
```bash
python3 gitleaks_detection.py -s "/path/to/source" -rp "output.json" gitleaks detect --no-git --verbose
```

#### **View Help Command**
```bash
python3 gitleaks_detection.py -h
```
Expected Output:
```plaintext
usage: gitleaks_detection.py [-s SOURCE] [-rp REPORT_PATH] [command] [subcommand] [additional arguments]

Run Gitleaks and process its output. (args order is important)

positional arguments:
  {gitleaks}            Command to execute (e.g., gitleaks)
  subcommand            Subcommand for Gitleaks (e.g., detect, protect, etc.)
  additional            Additional arguments for Gitleaks

optional arguments:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
                        Source directory or file to scan
  -rp REPORT_PATH, --report-path REPORT_PATH
                        Path to save the Gitleaks report
```

---

### **Docker**

#### **Build the Docker Image**
```bash
docker build --no-cache -t detectleaks .
```

#### **Run the Docker Image**
```bash
docker run -it -v $(pwd):/code detectleaks --report-path /code/output.json --source /code/ gitleaks detect --no-git -v
```

#### **View Help Command for Docker**
```bash
docker run -it -v $(pwd):/code detectleaks -h
```

---

### **Running Tests**
The tests are written using the `pytest` framework and are located in `gitleaks_detection_tests.py`.

#### **Run Tests**
```bash
pytest gitleaks_detection_tests.py
```

---

## **File Structure**
```plaintext
├── gitleaks_detection.py       # Main script to run Gitleaks with Python
├── gitleaks_detection_tests.py # Test cases for the script
├── Dockerfile                  # Docker configuration for running Gitleaks
├── requirements.txt            # Python dependencies
├── output.json               # Example output file (optional)
└── README.md                   # Documentation
```

---

## **Scenarios Handled**

### **Valid Runs**
- Arguments:
    ```bash
    -s "/path/to/source" -rp "output.json" gitleaks detect --no-git -v
    ```
    - **Result:** Successfully runs Gitleaks and outputs findings (if any) to `output.json`.

### **Unknown Argument**
- Arguments:
    ```bash
    -s "/path/to/source" -rp "output.json" gitleaks detect --jit
    ```
    - **Result:** 
      ```json
      {
          "exit_code": 2,
          "error_message": "Gitleaks scan failed: unknown argument '--jit'."
      }
      ```

### **Missing Source**
- Arguments:
    ```bash
    -rp "output.json" gitleaks detect
    ```
    - **Result:**
      ```json
      {
          "exit_code": 2,
          "error_message": "Gitleaks scan failed: please provide a source folder"
      }
      ```

### **Invalid Source**
- Arguments:
    ```bash
    -s "/path/to/invalid" -rp "output.json" gitleaks detect
    ```
    - **Result:**
      ```json
      {
          "exit_code": 2,
          "error_message": "Gitleaks scan failed: please provide a valid source folder"
      }
      ```

### **Missing Command or Subcommand**
- Arguments:
    ```bash
    -s "/path/to/source" -rp "output.json" --no-git
    ```
    - **Result:**
      ```json
      {
          "exit_code": 2,
          "error_message": "Gitleaks scan failed: unrecognized arguments: --no-git --verbose \n\n Please provide the arguments like this: --source \"the source path\" --report-path \"the report path\" {gitleaks command} gitleaks subcommand (e.g., detect, protect, etc.) additional args (e.g --no-git)"
      }
      ```
