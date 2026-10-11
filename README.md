# Fileless Invoice — Security Event Analysis and Attack Detection

## 📌 Project Overview

Fileless Invoice is a cybersecurity project developed to analyze security events, identify suspicious activity, and estimate potential attack probabilities.

The project uses Python-based event generation, behavioral analysis, baseline comparison, and detection evaluation. A Flask web dashboard provides access to the available analysis modules.

## 🎯 Objectives

* Analyze security events and suspicious activity.
* Identify potential attack patterns.
* Estimate attack probabilities using behavioral analysis.
* Evaluate detection performance across multiple scenarios.
* Study the effects of missing or degraded security events.
* Store analysis results using SQLite.
* Provide a web-based interface for security analysis.

## ✨ Features

### 1. Security Event Analysis

Analyzes generated security events to identify potentially suspicious activity.

### 2. Attack Detection

Uses event characteristics and behavioral attribution to estimate potential attack activity.

### 3. Baseline Analysis

Builds a baseline of routine activity to help distinguish normal behavior from suspicious patterns.

### 4. Event Generation and Degradation

Generates security event scenarios and simulates event loss or degradation.

### 5. Evaluation Module

Evaluates detection performance across different scenarios using accuracy and Brier score.

### 6. Calibration Module

Evaluates the reliability of predicted attack probabilities.

### 7. Diagnostic Module

Examines event visibility and missing-event patterns.

### 8. Case Inspection

Supports inspection of selected security analysis cases.

### 9. Web Dashboard

Provides a browser-based interface using Flask, HTML, and CSS.

### 10. Analysis History

Stores analysis results in an SQLite database.

## 🛠️ Technologies Used

* Python
* Flask
* PyYAML
* SQLite
* HTML and CSS
* Git
* GitHub

## 📂 Project Structure

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
├── generator/
├── degrader/
└── README.md
```

## ⚙️ Installation

### Prerequisites

* Python 3.10 or later
* Git
* A modern web browser

### Step 1: Clone the Repository

```bash
git clone https://github.com/vijayakumarigavini1/Fileless-Invoice-Security-Analysis.git
```

### Step 2: Open the Project Folder

```bash
cd Fileless-Invoice-Security-Analysis
```

### Step 3: Install Dependencies

```bash
python -m pip install Flask PyYAML
```

## ▶️ Run the Project

Start the Flask application:

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

## 🧪 Available Modules

| Module           | Description                                  |
| ---------------- | -------------------------------------------- |
| Main Analysis    | Generates and analyzes security events       |
| Diagnose         | Examines event visibility and missing events |
| Evaluate         | Measures detection performance               |
| Calibrate        | Evaluates probability calibration            |
| Inspect Cases    | Examines selected analysis cases             |
| Analysis History | Stores and retrieves analysis results        |

## 📊 Evaluation Results

The following results were recorded during testing:

| Scenario      | Events Evaluated | Reported Accuracy |
| ------------- | ---------------: | ----------------: |
| Standard      |              118 |            100.0% |
| Mimic Admin   |              105 |            100.0% |
| Admin Account |              131 |             77.1% |
| Admin LDAP    |              145 |            100.0% |
| **Overall**   |          **499** |         **94.0%** |

### Calibration Results

| Metric                           | Before Calibration | After Calibration |
| -------------------------------- | -----------------: | ----------------: |
| Brier Score                      |              0.050 |             0.040 |
| Expected Calibration Error (ECE) |              0.061 |             0.027 |

These results reflect the project's tested scenarios. They do not guarantee equivalent performance against real-world attacks.

## 🔮 Future Enhancements

* Add CSV file upload for security event analysis.
* Improve manual event input functionality.
* Add visualizations for security events and evaluation results.
* Improve report export functionality.
* Test the system with additional datasets and attack scenarios.

## ⚠️ Limitations

* Attack probabilities are estimates, not proof of an attack.
* Performance on generated scenarios does not establish real-world detection performance.
* Missing or degraded events can affect detection reliability.
* Further testing with representative real-world data is necessary.

## 👩‍💻 Author

**Vijaya Kumari Gavini**

Cybersecurity Project

GitHub: [vijayakumarigavini1](https://github.com/vijayakumarigavini1)

## 📜 Disclaimer

This project is intended for educational and cybersecurity research purposes. Detection results should be treated as analytical estimates and verified using additional evidence.
## 🌐 Live Demo

Access the deployed application here:

**[Fileless Invoice - Live Dashboard](https://fileless-invoice-security.onrender.com)**

## 🚀 Project Modules

- Main — Security event analysis
- Diagnose — Detection diagnostics
- Evaluate — Model performance evaluation
- Calibrate — Probability calibration
- Inspect Cases — Security case inspection

## 🛠️ Technologies Used

- Python
- Flask
- SQLite
- HTML and CSS
- Git and GitHub
- Render