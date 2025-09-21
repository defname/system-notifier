#!/bin/bash

# Uninstallation script for system-notifier

# --- Configuration ---
SERVICE_NAME="system-notifier.service"
SERVICE_FILE_PATH="$HOME/.config/systemd/user/$SERVICE_NAME"
ICON_CACHE_DIR=".icon_cache"

# --- Functions ---
log() {
    echo "[*] $1"
}

error() {
    echo "[!] $1" >&2
    exit 1
}

# --- Main Script ---
log "Starting uninstallation of system-notifier..."

# Stop and disable the systemd service
log "Stopping and disabling the systemd service..."
systemctl --user stop "$SERVICE_NAME"
systemctl --user disable "$SERVICE_NAME"

# Remove the systemd service file
if [ -f "$SERVICE_FILE_PATH" ]; then
    log "Removing systemd service file..."
    rm "$SERVICE_FILE_PATH"
else
    log "Systemd service file not found. Skipping."
fi

# Reload systemd user daemon
log "Reloading systemd user daemon..."
systemctl --user daemon-reload

# Remove the icon cache directory
if [ -d "$ICON_CACHE_DIR" ]; then
    log "Removing icon cache directory..."
    rm -rf "$ICON_CACHE_DIR"
else
    log "Icon cache directory not found. Skipping."
fi

log "Uninstallation complete."
