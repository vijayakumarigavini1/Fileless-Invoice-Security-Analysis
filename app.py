from flask import Flask, request, jsonify
import subprocess
import sys
import os
import html
import csv
import io

import database

app = Flask(__name__)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

SCRIPTS = {
    "main": "main.py",
    "diagnose": "diagnose.py",
    "evaluate": "evaluate.py",
    "calibrate": "calibrate.py",
    "inspect_cases": "inspect_cases.py"
}

database.initialize_database()


def run_script(module):
    """Run a project module and return its output and status."""

    if module not in SCRIPTS:
        return None, "error", "Unknown module"

    try:
        result = subprocess.run(
            [sys.executable, SCRIPTS[module]],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout or ""

        if result.stderr:
            output += "\n\nMessages or errors:\n" + result.stderr

        if not output.strip():
            output = "The script finished without producing output."

        status = "success" if result.returncode == 0 else "error"

        return output, status, None

    except subprocess.TimeoutExpired:
        return "The script exceeded the 60-second time limit.", "error", None

    except Exception as error:
        return str(error), "error", None


def make_page(output="Welcome! Select a button to run your project."):
    safe_output = html.escape(output)

    buttons = ""

    for key, filename in SCRIPTS.items():
        label = filename.replace(".py", "").replace("_", " ").title()

        buttons += f"""
        <form method="post" action="/run/{key}">
            <button type="submit">{label}</button>
        </form>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fileless Invoice Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <style>
            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background: #eef2f7;
                color: #1e293b;
            }}

            header {{
                background: #101827;
                color: white;
                text-align: center;
                padding: 30px 15px;
            }}

            .container {{
                max-width: 1000px;
                margin: 30px auto;
                padding: 0 20px;
            }}

            .cards {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
            }}

            .card {{
                background: white;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 3px 10px #0001;
            }}

            label {{
                display: inline-block;
                font-weight: 600;
                margin-bottom: 5px;
            }}

            input[type="text"], select, input[type="file"] {{
                box-sizing: border-box;
                width: 100%;
                max-width: 100%;
                min-height: 44px;
                padding: 10px 12px;
                margin: 4px 0 12px;
                border: 1px solid #cbd5e1;
                border-radius: 7px;
                background: #ffffff;
                color: #1e293b;
                font-size: 15px;
                display: block;
                visibility: visible;
                opacity: 1;
            }}

            input[type="file"] {{
                height: auto;
            }}

            .form-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 8px 16px;
            }}

            .help {{
                color: #64748b;
                font-size: 13px;
                line-height: 1.5;
            }}

            .buttons {{
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
                margin: 20px 0;
            }}

            button {{
                background: #2563eb;
                color: white;
                border: 0;
                border-radius: 7px;
                padding: 13px 18px;
                cursor: pointer;
                font-size: 14px;
            }}

            button:hover {{
                background: #1d4ed8;
            }}

            .output {{
                background: #0b1220;
                color: #a7f3d0;
                padding: 20px;
                border-radius: 10px;
                white-space: pre-wrap;
                overflow-wrap: anywhere;
                overflow-x: auto;
                min-height: 150px;
                line-height: 1.5;
            }}

            .api-links {{
                background: white;
                padding: 18px;
                border-radius: 10px;
                margin-top: 20px;
            }}

            .api-links a {{
                color: #2563eb;
                margin-right: 15px;
            }}

            footer {{
                text-align: center;
                padding: 25px;
                color: #64748b;
            }}
        </style>
    </head>

    <body>
        <header>
            <h1>Fileless Invoice</h1>
            <p>Security Event Analysis and Attack Detection</p>
        </header>

        <div class="container">
            <h2>Project Dashboard</h2>

            <div class="cards">
                <div class="card">
                    <h3>Event Analysis</h3>
                    <p>Investigate security events and attack evidence.</p>
                </div>

                <div class="card">
                    <h3>Diagnostics</h3>
                    <p>Examine detection accuracy and missing evidence.</p>
                </div>

                <div class="card">
                    <h3>Evaluation</h3>
                    <p>Review the model's test results.</p>
                </div>

                <div class="card">
                    <h3>Calibration</h3>
                    <p>Compare probability calibration metrics.</p>
                </div>
            </div>
<h2>Input Security Events</h2>

<div class="card">
    <h3>Manual Event Analysis</h3>
    <form method="post" action="/manual-analysis">
        <div class="form-grid">
            <div>
                <label for="source_host">Source Host</label>
                <input type="text" id="source_host" name="source_host"
                       value="CLERK-PC" required>
            </div>
            <div>
                <label for="destination_host">Destination Host</label>
                <input type="text" id="destination_host" name="destination_host"
                       value="JUMPHOST1" required>
            </div>
            <div>
                <label for="event_type">Event Type</label>
                <select id="event_type" name="event_type" required>
                    <option value="login">login</option>
                    <option value="ldap_burst">ldap_burst</option>
                    <option value="access">access</option>
                    <option value="connect">connect</option>
                    <option value="script_host_spawn">script_host_spawn</option>
                </select>
            </div>
            <div>
                <label for="user_account">User Account</label>
                <input type="text" id="user_account" name="user_account"
                       value="admin1" required>
            </div>
        </div>
        <button type="submit">Analyze Event</button>
    </form>
</div>

<div class="card" style="margin-top: 18px;">
    <h3>CSV File Upload</h3>
    <p class="help">Upload a CSV containing these column names:
       <code>source_host,destination_host,event_type,user_account</code>.
       Maximum file size: 2 MB; maximum 5,000 event rows.</p>
    <form method="post" action="/csv-analysis" enctype="multipart/form-data">
        <label for="events_csv">Choose CSV File</label>
        <input type="file" id="events_csv" name="events_csv"
               accept=".csv,text/csv" required>
        <button type="submit">Upload and Analyze CSV</button>
    </form>
</div>

            <h2>Run Project Modules</h2>

            <div class="buttons">
                {buttons}
            </div>

            <h2>Execution Results</h2>
            <div class="output">{safe_output}</div>

            <div class="api-links">
                <h3>Backend Services</h3>
                <p>
                    <a href="/api/health">Backend Status</a>
                    <a href="/api/history">Analysis History</a>
                </p>
            </div>

            <p>
                Note: Attack probabilities are estimates,
                not proof of an attack.
            </p>
        </div>

        <footer>Fileless Invoice Security Analysis Project</footer>
    </body>
    </html>
    """


@app.route("/")
def home():
    return make_page()


@app.route("/run/<module>", methods=["POST"])
def run_module(module):
    if module not in SCRIPTS:
        return "Unknown module", 404

    output, status, error = run_script(module)

    if error:
        output = error
        status = "error"

    try:
        database.save_result(module, status, output)
    except Exception:
        app.logger.exception("Failed to save analysis result")

    return make_page(output)


# API: Check whether the backend and database are available.
@app.route("/api/health", methods=["GET"])
def health():
    try:
        history_count = len(database.get_history(limit=200))

        return jsonify({
            "status": "ok",
            "application": "Fileless Invoice",
            "database": "connected",
            "recent_history_records": history_count
        }), 200

    except Exception:
        app.logger.exception("Health check failed")

        return jsonify({
            "status": "error",
            "database": "unavailable"
        }), 500


# API: Run a module and return structured JSON.
@app.route("/api/run/<module>", methods=["POST"])
def api_run_module(module):
    if module not in SCRIPTS:
        return jsonify({
            "error": "Unknown module",
            "available_modules": list(SCRIPTS.keys())
        }), 404

    output, status, error = run_script(module)

    if error:
        output = error
        status = "error"

    try:
        result_id = database.save_result(module, status, output)
    except Exception:
        app.logger.exception("Failed to save analysis result")

        return jsonify({
            "module": module,
            "status": status,
            "output": output,
            "database_saved": False
        }), 500

    return jsonify({
        "id": result_id,
        "module": module,
        "status": status,
        "output": output,
        "database_saved": True
    }), 200 if status == "success" else 500


# API: Retrieve recent analysis history.
@app.route("/api/history", methods=["GET"])
def api_history():
    try:
        limit = request.args.get("limit", default=50, type=int)

        if limit is None or limit < 1:
            return jsonify({
                "error": "limit must be a positive integer"
            }), 400

        records = database.get_history(limit=limit)

        return jsonify({
            "count": len(records),
            "history": records
        }), 200

    except Exception:
        app.logger.exception("Could not retrieve history")

        return jsonify({
            "error": "Could not retrieve analysis history"
        }), 500


# API: Retrieve one result by its database ID.
@app.route("/api/history/<int:result_id>", methods=["GET"])
def api_single_result(result_id):
    try:
        result = database.get_result(result_id)

        if result is None:
            return jsonify({
                "error": "Result not found"
            }), 404

        return jsonify(result), 200

    except Exception:
        app.logger.exception("Could not retrieve result")

        return jsonify({
            "error": "Could not retrieve result"
        }), 500
@app.route("/manual-analysis", methods=["POST"])
def manual_analysis():
    source_host = request.form.get("source_host", "").strip()
    destination_host = request.form.get("destination_host", "").strip()
    event_type = request.form.get("event_type", "").strip().lower()
    user_account = request.form.get("user_account", "").strip()

    if not all([source_host, destination_host, event_type, user_account]):
        return make_page("Error: Please fill in all Manual Event Analysis fields.")

    event_rules = {
        "script_host_spawn": ("Execution", "A scripting host was launched."),
        "ldap_burst": ("Discovery", "Directory enumeration activity was reported."),
        "login": ("Lateral Movement", "A login to another host was reported."),
        "connect": ("Lateral Movement", "A connection to another host was reported."),
        "access": ("Access", "Access activity was reported; additional context is required."),
    }

    if event_type in event_rules:
        capability, reason = event_rules[event_type]
        assessment = "Recognized event; additional correlated evidence is required for attack attribution."
        status = "success"
    else:
        capability = "Unknown"
        reason = "This event type is not present in the current capability mapping."
        assessment = "Needs further investigation. Verify the event type and supporting logs."
        status = "needs_review"

    output = (
        "MANUAL EVENT ANALYSIS\n"
        "=====================\n\n"
        f"Source Host: {source_host}\n"
        f"Destination Host: {destination_host}\n"
        f"Event Type: {event_type}\n"
        f"User Account: {user_account}\n\n"
        f"Recognized Capability: {capability}\n"
        f"Evidence Note: {reason}\n"
        f"Assessment: {assessment}\n\n"
        "Attack Probability: Not calculated\n"
        "Explanation: A single manual event does not provide "
        "the correlated event chain and trained baseline required "
        "by the existing attribution engine.\n"
    )

    try:
        result_id = database.save_result("manual_analysis", status, output)
        output += f"\nHistory Record ID: {result_id}"
    except Exception:
        app.logger.exception("Failed to save manual analysis")
        output += "\nWarning: The result could not be saved to database history."

    return make_page(output)

@app.route("/csv-analysis", methods=["POST"])
def csv_analysis():
    uploaded = request.files.get("events_csv")
    if uploaded is None or not uploaded.filename:
        return make_page("CSV upload failed: Please choose a CSV file.")

    if not uploaded.filename.lower().endswith(".csv"):
        return make_page("CSV upload failed: Please select a .csv file.")

    raw = uploaded.stream.read(2 * 1024 * 1024 + 1)
    if len(raw) > 2 * 1024 * 1024:
        return make_page("CSV upload failed: File must be 2 MB or smaller.")

    try:
        text = raw.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        required = ["source_host", "destination_host", "event_type", "user_account"]
        if not reader.fieldnames:
            return make_page("CSV upload failed: The file is empty or has no header.")

        headers = [name.strip().lower() if name else "" for name in reader.fieldnames]
        missing = [name for name in required if name not in headers]
        if missing:
            return make_page(
                "CSV upload failed: Missing required column(s): " + ", ".join(missing)
            )

        rows = []
        for line_number, original_row in enumerate(reader, start=2):
            if line_number > 5001:
                return make_page("CSV upload failed: Maximum allowed rows is 5,000.")
            # Normalize header names and trim values.
            row = {
                (key.strip().lower() if key else ""): (value or "").strip()
                for key, value in original_row.items()
            }
            values = {key: row.get(key, "") for key in required}
            if not any(values.values()):
                continue
            if not all(values.values()):
                return make_page(
                    f"CSV upload failed: One or more required fields are empty at row {line_number}."
                )
            rows.append(values)

        if not rows:
            return make_page("CSV upload failed: No event rows were found.")

        event_rules = {
            "script_host_spawn": ("Execution", "Scripting-host launch event; review context."),
            "ldap_burst": ("Discovery", "LDAP burst event; review for directory enumeration."),
            "login": ("Lateral Movement", "Login event; correlate with other evidence."),
            "connect": ("Lateral Movement", "Connection event; correlate with other evidence."),
            "access": ("Unknown", "Access event; additional context is required."),
        }

        suspicious = []
        unknown = []
        counts = {}
        for index, row in enumerate(rows, start=1):
            event_type = row["event_type"].lower()
            counts[event_type] = counts.get(event_type, 0) + 1
            if event_type in ("script_host_spawn", "ldap_burst"):
                suspicious.append((index, row, event_rules[event_type]))
            elif event_type not in event_rules:
                unknown.append((index, row))

        lines = [
            "CSV SECURITY EVENT ANALYSIS",
            "============================",
            f"File: {os.path.basename(uploaded.filename)}",
            f"Total event rows analyzed: {len(rows)}",
            f"Rule-flagged events (script_host_spawn / ldap_burst): {len(suspicious)}",
            f"Unknown event types needing review: {len(unknown)}",
            "",
            "Event type counts:"
        ]
        for event_name, count in sorted(counts.items()):
            lines.append(f"  {event_name}: {count}")

        lines.extend(["", "Flagged events for review:"])
        if suspicious:
            for index, row, (capability, reason) in suspicious[:100]:
                lines.append(
                    f"  Row {index}: {row['source_host']} -> {row['destination_host']} | "
                    f"{row['event_type']} | user={row['user_account']} | "
                    f"{capability}: {reason}"
                )
        else:
            lines.append("  No events matched the simple review rules.")

        if unknown:
            lines.extend(["", "Unknown event types (review required):"])
            for index, row in unknown[:100]:
                lines.append(
                    f"  Row {index}: {row['event_type']} | "
                    f"{row['source_host']} -> {row['destination_host']}"
                )

        lines.extend([
            "",
            "Important: These are rule-based review flags, not confirmed attacks.",
            "Attack probability is not calculated by this CSV upload feature."
        ])
        output = "\n".join(lines)

        try:
            result_id = database.save_result("csv_analysis", "success", output)
            output += f"\\n\\nHistory Record ID: {result_id}"
        except Exception:
            app.logger.exception("Failed to save CSV analysis")
            output += "\\nWarning: Result could not be saved to database history."

        return make_page(output)

    except UnicodeDecodeError:
        return make_page("CSV upload failed: Please save the CSV as UTF-8 and try again.")
    except csv.Error:
        return make_page("CSV upload failed: The file could not be parsed as valid CSV.")
    except Exception:
        app.logger.exception("CSV analysis failed")
        return make_page("CSV analysis failed due to an internal error. Check the server console.")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)