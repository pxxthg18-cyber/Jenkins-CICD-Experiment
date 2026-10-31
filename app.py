from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# Simple HTML template for the beginner-friendly web interface
HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CI/CD Flask Application</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: linear-gradient(135deg, #1f2937, #111827);
            color: #f3f4f6;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background-color: #1f2937;
            border: 1px solid #374151;
            border-radius: 12px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
            max-width: 600px;
            width: 100%;
            padding: 32px;
            text-align: center;
        }
        .badge {
            display: inline-block;
            background-color: #10b981;
            color: #064e3b;
            font-weight: 600;
            font-size: 0.85rem;
            padding: 4px 12px;
            border-radius: 9999px;
            margin-bottom: 16px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        h1 {
            font-size: 1.85rem;
            margin-bottom: 12px;
            color: #ffffff;
        }
        p.subtitle {
            color: #9ca3af;
            font-size: 1rem;
            margin-bottom: 24px;
            line-height: 1.5;
        }
        .info-card {
            background-color: #111827;
            border-radius: 8px;
            padding: 16px;
            margin: 20px 0;
            text-align: left;
            border-left: 4px solid #3b82f6;
        }
        .info-card h2 {
            font-size: 1rem;
            color: #93c5fd;
            margin-bottom: 8px;
        }
        .info-card ul {
            list-style-type: none;
            font-size: 0.9rem;
            color: #d1d5db;
        }
        .info-card li {
            padding: 4px 0;
        }
        .info-card li strong {
            color: #f3f4f6;
        }
        .btn-group {
            display: flex;
            gap: 12px;
            justify-content: center;
            margin-top: 24px;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            font-size: 0.95rem;
            transition: all 0.2s ease;
        }
        .btn-primary {
            background-color: #2563eb;
            color: #ffffff;
        }
        .btn-primary:hover {
            background-color: #1d4ed8;
        }
        .btn-secondary {
            background-color: #374151;
            color: #e5e7eb;
        }
        .btn-secondary:hover {
            background-color: #4b5563;
        }
        footer {
            margin-top: 24px;
            font-size: 0.8rem;
            color: #6b7280;
        }
    </style>
</head>
<body>
    <div class="container">
        <span class="badge">Pipeline Status: Operational</span>
        <h1>Jenkins CI/CD Lab Experiment</h1>
        <p class="subtitle">Automated Building, Testing, and Deployment of a Containerized Flask Web App</p>

        <div class="info-card">
            <h2>Application Details</h2>
            <ul>
                <li><strong>Image Name:</strong> jenkins-cicd-flask-app</li>
                <li><strong>Framework:</strong> Flask (Python 3)</li>
                <li><strong>Pipeline Engine:</strong> Jenkins Declarative Pipeline</li>
                <li><strong>Container Engine:</strong> Docker</li>
            </ul>
        </div>

        <div class="btn-group">
            <a href="/health" class="btn btn-primary" target="_blank">Check Health API (/health)</a>
            <a href="https://jenkins.io" class="btn btn-secondary" target="_blank" rel="noopener">Jenkins Docs</a>
        </div>

        <footer>
            College Lab Experiment &bull; Containerized DevOps Demo
        </footer>
    </div>
</body>
</html>
"""


@app.route("/")
def home():
    """Home endpoint rendering user-friendly UI for demo and verification."""
    return render_template_string(HOME_TEMPLATE)


@app.route("/health")
def health():
    """
    Health check endpoint utilized by Docker HEALTHCHECK,
    automated pipeline test suites, and load balancers.
    """
    return jsonify(
        status="healthy",
        app="jenkins-cicd-flask-app",
        version="1.0.1"
    ), 200


if __name__ == "__main__":
    # Host 0.0.0.0 allows incoming traffic inside Docker containers
    app.run(host="0.0.0.0", port=5000, debug=False)
