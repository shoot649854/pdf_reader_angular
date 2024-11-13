#!/bin/bash

# Define the ports used by backend and frontend
BACKEND_PORT=5001
FRONTEND_PORT=4200

# Function to check if a port is in use
check_port() {
  if lsof -i:$1 > /dev/null; then
    echo "Port $1 is already in use. Terminating the script."
    exit 1
  fi
}

# Trap function to kill processes on exit
cleanup() {
  echo "Stopping frontend and backend..."
  lsof -ti :$FRONTEND_PORT | xargs kill -9
  lsof -ti :$BACKEND_PORT | xargs kill -9
}

trap cleanup EXIT
check_port $BACKEND_PORT
check_port $FRONTEND_PORT

# Start backend if port is available
(
  cd backend || exit
  echo "Starting backend with Poetry on port $BACKEND_PORT..."
  poetry run python app.py &
)

# Start frontend if port is available
(
  cd frontend || exit
  echo "Starting frontend with pnpm on port $FRONTEND_PORT..."
  pnpm run start &
)

wait
