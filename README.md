# Fileless Invoice — Security Event Analysis and Attack Detection

## Project Overview

**Fileless Invoice** is a cybersecurity project designed to analyze security events, identify suspicious activity, and estimate the probability of potential attacks.

The project uses Python-based event generation, event degradation, baseline analysis, behavioral attribution, and attack detection techniques to study security event patterns through a web-based dashboard.

The dashboard provides access to different analysis modules and displays evaluation results to help users understand how suspicious events can be identified.

## Objectives

* Analyze security events and suspicious activity.
* Identify potential attack patterns from event sequences.
* Estimate attack probabilities using behavioral analysis.
* Evaluate detection performance across different scenarios.
* Examine the effects of missing or degraded security events.
* Store analysis results in an SQLite database.
* Provide a web interface for running analysis modules.

## Key Features

### 1. Security Event Analysis

Processes generated security events and analyzes activity patterns to identify potentially suspicious behavior.

### 2. Attack Detection

Uses event characteristics and behavioral attribution to estimate whether observed activity may be associated with an attack.

### 3. Baseline Analysis

Builds a baseline of routine activity to help distinguish normal behavior from potentially suspicious events.

### 4. Event Generation and Degradation

Generates security event scenarios and simulates the loss or degradation of events to study the impact on detection.

### 5. Evaluation Module

Evaluates detection performance across multiple scenarios and reports metrics such as accuracy and Brier score.

### 6. Calibration Module

Examines probability calibration to assess how closely predicted attack probabilities correspond to observed outcomes.

### 7. Diagnostic Analysis

Studies event visibility and missing-event patterns to understand how incomplete telemetry affects security analysis.

### 8. Case Inspection

Provides functionality for inspecting selected security analysis cases.

### 9. Web Dashboard

Uses Flask to provide a browser-based interface for running the project modules.

### 10. Analysis History

Uses SQLite to store analysis results for later reference.

## Technologies Used

* **Programming Language:** Python
* **Web Framework:** Flask
* **Configuration:** YAML
* **Database:** SQLite
* **Version Control:** Git
* **Repository Hosting:** GitHub
* **Interface:** HTML and CSS

## Project Structure

```text
fileless_invoice/
├── app.py
├── main.py
├── database.py
├── calibrate.py
├── diagnose.py
├── evaluate.py
├── inspect_cases.py
├── configs/
│   └── scenario.yaml
├── engine/
│   ├── attribution.py
│   ├── baseline.py
│   ├── capability.py
│   ├── chain.py
│   ├── labeller.py
│   └── regulatory.py
├── generator/
│   └── generate.py
├── degrader/
│   └── degrade.py
├── .gitignore
└── README.md
```

## Installation

### Prerequisites

* Python 3.10 or later
* Git
* A web browser

### Step 1: Clone the Repository

```bash
git clone https://github.com/vijayakumarigavini1/Fileless-Invoice-Security-Analysis.git
```

### Step 2: Navigate to the Project Folder

```bash
cd Fileless-Invoice-Security-Analysis
```

### Step 3: Install Dependencies

```bash
python -m pip install Flask PyYAML
```

Install any additional dependencies required by the project if prompted.

## Running the Project

Start the Flask application:

```bash
python app.py
```

Open the following address in your browser:

```text
http://127.0.0.1:5000
```

The dashboard provides access to the available project modules.

## Available Modules

| Module           | Purpose                                              |
| ---------------- | ---------------------------------------------------- |
| Main Analysis    | Generates and analyzes security events               |
| Diagnose         | Examines event visibility and missing-event patterns |
| Evaluate         | Evaluates detection performance                      |
| Calibrate        | Examines attack-probability calibration              |
| Inspect Cases    | Inspects selected analysis cases                     |
| Analysis History | Stores and retrieves saved analysis results          |

## Evaluation Results

The following results were obtained during project testing:

| Scenario      | Evaluated Events | Reported Accuracy |
| ------------- | ---------------: | ----------------: |
| Standard      |              118 |            100.0% |
| Mimic Admin   |              105 |            100.0% |
| Admin Account |              131 |             77.1% |
| Admin LDAP    |              145 |            100.0% |
| **Overall**   |          **499** |         **94.0%** |

Additional calibration results from testing:

* Brier score before calibration: 0.050
* Brier score after calibration: 0.040
* Expected Calibration Error (ECE) before calibration: 0.061
* Expected Calibration Error (ECE) after calibration: 0.027

These are results from the project's evaluation scenarios, not a guarantee of performance on real-world attacks. The results depend on the generated data, scenario design, and evaluation methodology.

## Limitations

* Attack probabilities are estimates, not proof of an attack.
* Performance on generated scenarios does not establish real-world detection performance.
* Missing or degraded security events can affect detection reliability.
* Additional testing with representative real-world data is needed before operational use.

## Future Enhancements

* Add CSV file upload for security event analysis.
* Support manual event input through the dashboard.
* Improve detection and reporting capabilities.
* Add visualizations for event patterns and evaluation metrics.
* Improve analysis history and report export functionality.
* Evaluate the system using additional datasets and attack scenarios.

## Author

**Vijaya Kumari Gavini**

Cybersecurity Project

GitHub: https://github.com/vijayakumarigavini1

## Disclaimer

This project is intended for educational and cybersecurity research purposes. Detection results should be interpreted as analytical estimates and verified using additional evidence.
