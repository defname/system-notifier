# Installation script for system-notifier

# --- Configuration ---
SERVICE_NAME="system-notifier.service"
SERVICE_FILE_PATH="$HOME/.config/systemd/user/$SERVICE_NAME"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
PYTHON_EXEC="$(which python3)"

# --- Functions ---
log() {
    echo "[*] $1"
}

error() {
    echo "[!] $1" >&2
    exit 1
}

# --- Main Script ---
log "Starting installation of system-notifier..."

# Check for python3
if [ -z "$PYTHON_EXEC" ]; then
    error "python3 not found. Please install python3 and make sure it's in your PATH."
fi

# Create systemd user directory if it doesn't exist
log "Checking for systemd user directory..."
mkdir -p "$HOME/.config/systemd/user"

# Create the systemd service file
log "Creating systemd service file at $SERVICE_FILE_PATH..."
cat > "$SERVICE_FILE_PATH" << EOL
[Unit]
Description=System Notifier
After=graphical-session.target

[Service]
ExecStart=$PYTHON_EXEC $PROJECT_DIR/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
EOL

log "Service file created successfully."

# Reload systemd user daemon
log "Reloading systemd user daemon..."
systemctl --user daemon-reload

# Enable and start the service
log "Enabling and starting the service..."
systemctl --user enable --now "$SERVICE_NAME"

log "Installation complete. The system-notifier service is now running."
log "You can check the status with: systemctl --user status $SERVICE_NAME"
