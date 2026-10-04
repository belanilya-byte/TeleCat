# 🐱 TeleCat

@TeleKoshkaBot

**TeleCat** is a persistent virtual pet that lives inside Telegram.

The project started as a simple Tamagotchi-style bot and is being developed toward a personalized virtual creature with autonomous behavior, memory and personality.

## Current version — Mk.0.2

### Features

- Persistent virtual pet state
- Hunger, thirst, litter and affection mechanics
- State decay over real time
- Custom cat names
- Owner profiles
- Russian, English and Hebrew localization
- Autonomous background behavior
- Random unsolicited interactions
- Persistent SQLite storage
- Admin user information tools
- Production deployment with persistent storage

## Tech stack

- Python
- aiogram
- SQLite
- Git / GitHub
- Railway
- Jira

## Architecture

The original Mk.0.1 prototype was refactored into separate modules for:

- Telegram handlers
- pet logic
- database operations
- background behavior
- localization
- UI
- configuration

This architecture is intended to support future personality, memory and LLM integration.

## Development

TeleCat is developed iteratively using a Jira-based workflow.

Development includes feature planning, implementation, production deployment, bug reporting, debugging and production verification.

## Roadmap

**Mk.0.3 — Personality & Behavior**

Planned development includes persistent personality traits, mood, behavioral decisions and interaction history.

Later versions are intended to explore memory, AI-assisted communication and evolutionary mechanics.

## Copyright

Copyright © 2026 Ilia Belan. All rights reserved.

This repository is publicly available for portfolio and educational review.

No permission is granted to copy, modify, distribute, sublicense or use this software commercially without explicit permission from the author.
