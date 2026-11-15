# 🌟 ANSH-M Essentials (Finished Product Features)

This document lists the "Proper Working Features" that have been transitioned from mock-up to production-ready status.

## 🚀 1. Real-Time SMS Automation
- **Unified Dispatch**: Centralized SMS service that uses live Twilio API credentials.
- **Auto-Formatting**: Built-in regex engine that sanitizes and converts 10-digit Indian mobile numbers into the global E.164 standard (+91...).
- **Background Engine**: Powered by `APScheduler`, running independently of the web server for 24/7 reliability.

## 📈 2. Price Spike Intelligence (15% Surge Monitor)
- **Hourly Scans**: The system analyzes predicted price changes every 60 minutes.
- **Surge Warning**: If a >15% increase is detected for tomorrow, an **Emergency Spike Alert** is triggered and sent to all subscribers in that market.
- **Smart Logic**: Prevents duplicate alerts for the same spike event.

## 🔐 3. Security & Infrastructure
- **Private Data Vault**: All sensitive keys and IDs are moved to `D:\antigravity\secret` during migration.
- **Master .gitignore**: Prevents accidental exposure of your Twilio and Agmarknet keys on GitHub.
- **One-Click Deployment**: `RUN_PROJECT.bat` handles all environment setups on new laptops automatically.

## ⚡ 4. Essential Mode Toggle
You can control the alert intensity by setting the `ESSENTIALS_ONLY` flag in the `backend/.env` file.
- `ESSENTIALS_ONLY=True`: Sends only high-priority Spike Alerts.
- `ESSENTIALS_ONLY=False`: Sends both morning summaries and spike alerts.
