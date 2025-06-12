FastAPI Application Deployment Guide
This README.md outlines the steps to deploy a FastAPI application on an Alma server, running it efficiently in the background using Gunicorn with Uvicorn workers and managing it as a daemon process via systemd.

📝 Description
This guide is tailored for deploying a FastAPI application onto an AlmaLinux (or similar RHEL-based) server. The deployment strategy focuses on using gunicorn as the process manager with uvicorn workers to serve the asynchronous FastAPI application, ensuring high performance and stability. The application will be managed as a background service (daemon) using systemd, which provides robust features for process control, automatic restarts, and system integration.

✨ Key Deployment Features
Robust Serving: Utilizes Gunicorn as a WSGI/ASGI HTTP server for process management.

Asynchronous Workers: Employs Uvicorn workers for optimal performance with FastAPI's asynchronous nature.

Background Operation: Configured as a systemd service to run reliably in the background upon server boot.

Worker Configuration: Set up with 4 workers to handle concurrent requests.

Specific Python Version: Targets Python 3.9.5 for environment consistency.

🚀 Prerequisites on Alma Server
Before you begin, ensure your Alma server has the following installed:

Python 3.9.5:

AlmaLinux typically comes with a Python version, but you might need to install python3.9 specifically or use pyenv for version management if it's not the default 3.9.5.

You can often install a specific Python version using dnf or yum if available in your repository:

sudo dnf install python3.9
# Or if using pyenv (recommended for precise version control):
# curl https://pyenv.run | bash
# exec "$SHELL"
# pyenv install 3.9.5
# pyenv global 3.9.5

pip (Python package installer)

venv (Python virtual environment module - usually comes with Python)

git (for cloning your repository)

sudo privileges (for installing packages and managing system services)

systemd (standard on AlmaLinux for service management - no extra installation needed)

📦 Project Setup and Installation
Follow these steps to get your FastAPI application ready on the Alma server:

Log in to your Alma server:

ssh your_user@your_alma_server_ip

Clone your FastAPI project:
Choose a suitable directory, for example, /opt/your-fastapi-app/.

sudo mkdir -p /opt/your-fastapi-app
sudo chown your_user:your_user /opt/your-fastapi-app # Grant ownership to your user
cd /opt/your-fastapi-app
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git . # Clones into current directory

(Replace YOUR_USERNAME and YOUR_REPOSITORY_NAME with your actual GitHub details.)

Create and activate a Python virtual environment:
It is crucial to use a virtual environment to manage project dependencies in isolation.

python3.9 -m venv venv
source venv/bin/activate

(If using pyenv and pyenv global 3.9.5 is set, python -m venv venv might suffice.)

Install project dependencies:
Ensure you have a requirements.txt file in your project's root with the specified versions:

fastapi==0.115.12
uvicorn[standard]==0.34.3
gunicorn==23.0.0
python-multipart==1.2.1

Then install:

pip install -r requirements.txt

Create the UPLOAD_FOLDER (if your app uses file uploads):

mkdir UPLOAD_FOLDER

Ensure this folder has appropriate write permissions for the user that Gunicorn/Uvicorn will run as. For a simple setup, if your Gunicorn worker is running as your_user, the current permissions are fine. For production, consider a dedicated service user.

⚙️ Deployment with Gunicorn and Systemd
We will create a systemd service file to manage your FastAPI application.

Create a Gunicorn start script (optional but recommended):
This script encapsulates the Gunicorn command, making the systemd service file cleaner.
Create a file named start_app.sh in your project root (/opt/your-fastapi-app/):

#!/bin/bash
# start_app.sh

# Navigate to the application directory
cd /opt/your-fastapi-app/

# Activate the virtual environment
source venv/bin/activate

# Run Gunicorn with Uvicorn workers
# Replace 'main:app' with your actual module:app if it's different
# E.g., 'my_api_folder.main:app' if your app is in 'my_api_folder/main.py'
exec gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --log-level info \
    --log-file - # Log to stdout, which systemd will capture

Make the script executable:

chmod +x start_app.sh

Create a systemd service file:
This file defines how your application will run as a daemon.
Create /etc/systemd/system/your-fastapi-app.service using sudo:

sudo vim /etc/systemd/system/your-fastapi-app.service

Paste the following content, adjusting User and Group to your deployment user/group (e.g., your_user):

[Unit]
Description=FastAPI application served by Gunicorn
After=network.target

[Service]
User=your_user # Replace with your deployment user (e.g., 'your_user')
Group=your_user # Replace with your deployment group (e.g., 'your_user')
WorkingDirectory=/opt/your-fastapi-app
ExecStart=/opt/your-fastapi-app/start_app.sh
Restart=always
RestartSec=5s
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=your-fastapi-app

[Install]
WantedBy=multi-user.target

Description: A human-readable description of your service.

After=network.target: Ensures the network is up before starting the service.

User and Group: The user and group under which the Gunicorn process will run. Crucial for security and permissions.

WorkingDirectory: The directory where your start_app.sh script and FastAPI application reside.

ExecStart: The command to execute to start your application. This points to the start_app.sh script.

Restart=always: Ensures the service automatically restarts if it crashes.

RestartSec=5s: Waits 5 seconds before attempting a restart.

StandardOutput/StandardError=syslog: Redirects logs to systemd journal. You can view them using journalctl.

SyslogIdentifier: A unique identifier for your logs in journalctl.

WantedBy=multi-user.target: Ensures the service starts automatically when the system boots into a multi-user environment.

Reload systemd to recognize the new service:

sudo systemctl daemon-reload

Start your FastAPI service:

sudo systemctl start your-fastapi-app

Enable your service to start on boot:

sudo systemctl enable your-fastapi-app

📊 Managing the Application
Once deployed as a systemd service, you can manage your FastAPI application using systemctl commands:

Check status:

sudo systemctl status your-fastapi-app

This will show if the service is active, running, and recent log messages.

Stop the application:

sudo systemctl stop your-fastapi-app

Restart the application:

sudo systemctl restart your-fastapi-app

View logs:

sudo journalctl -u your-fastapi-app.service -f

The -f flag "follows" the logs in real-time.

⚠️ Troubleshooting
Service fails to start:

Check sudo systemctl status your-fastapi-app for immediate errors.

Use sudo journalctl -u your-fastapi-app.service --since "1 hour ago" (or a shorter time frame) to view detailed logs and pinpoint the issue.

Ensure all Python dependencies are correctly installed in the virtual environment.

Double-check the ExecStart path and the main:app entry in start_app.sh.

Ensure your start_app.sh script is executable (chmod +x start_app.sh).

"Permission denied" errors:

Verify the User and Group in your .service file match the actual user and group that owns the /opt/your-fastapi-app directory and its contents (especially the UPLOAD_FOLDER if used).

Check directory and file permissions (ls -l /opt/your-fastapi-app).

Application not accessible (e.g., in browser):

Verify your FastAPI app is binding to 0.0.0.0:8000 (or your chosen IP/port).

Check your server's firewall (e.g., firewalld on AlmaLinux). You might need to open port 8000:

sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

If using a reverse proxy like Nginx or Apache, ensure it's configured correctly to forward requests to Gunicorn (typically http://127.0.0.1:8000).

This README.md provides a robust foundation for deploying your FastAPI application on an Alma server using systemd. Remember to adapt paths, filenames, and user/group details to your specific environment.
