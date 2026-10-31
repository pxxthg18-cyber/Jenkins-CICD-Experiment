#!/usr/bin/env python3
"""
verify_deployment.py - Post-deployment health verification script.
Invoked by Stage 5 of the Jenkins CI/CD pipeline.
"""
import sys
import json
import urllib.request

def verify(port):
    urls = [
        f"http://host.docker.internal:{port}/health",
        f"http://localhost:{port}/health"
    ]
    for url in urls:
        try:
            print(f"Checking deployment health at {url}...")
            res = urllib.request.urlopen(url, timeout=5)
            if res.status == 200:
                body = json.loads(res.read().decode("utf-8"))
                if body.get("status") == "healthy":
                    print(f"SUCCESS: Health check verified on {url}!")
                    print(f"Payload: {body}")
                    return True
        except Exception as err:
            print(f"Notice: {url} check not ready ({err})")
    return False

if __name__ == "__main__":
    port_to_check = sys.argv[1] if len(sys.argv) > 1 else "5000"
    if not verify(port_to_check):
        print(f"ERROR: Deployment health verification failed on port {port_to_check}")
        sys.exit(1)
    sys.exit(0)
