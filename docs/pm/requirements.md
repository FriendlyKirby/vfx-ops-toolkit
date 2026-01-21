# Requirements

## Problem
In production, render outputs and storage usage must be monitored to prevent delays and failures.
Teams also need lightweight ways to record publish events and retrieve history.

## Goals (Must-have)
- Validate render outputs and detect missing frames
- Report disk usage by show/shot
- Record a publish event without modifying render outputs
- List publish history with filtering
- Support human-readable output and machine-readable JSON
- Log actions to a file

## Non-goals
- Render farm scheduling
- DCC plugins or GUIs (Maya/Nuke/Houdini UI)
- Real integration with external tracking systems (simulated adapter only)