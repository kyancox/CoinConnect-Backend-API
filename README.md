# api.coinmerge.co

## Overview
The CoinMerge Backend API powers the core functionality of the CoinMerge web-app, a unified cryptocurrency portfolio tracker. This API integrates with Coinbase, Gemini, and Ledger Live, enabling users to view their entire cryptocurrency portfolio in one centralized location. It leverages Python and Flask to create a robust RESTful API architecture, adhering to best practices in Object-Oriented Programming (OOP), specifically utilizing inheritance and composition principles.

## Features
Exchange Integration: Utilizes REST APIs from Coinbase and Gemini to fetch user asset data. For Ledger Live, it parses the Operations History CSV to account for assets stored on Ledger devices.
Real-time Pricing: Fetches real-time cryptocurrency prices through the CoinMarketCap API, ensuring accurate portfolio valuation.
Security: Implements secure authentication mechanisms for API key and secret management, allowing safe user interactions with their exchange accounts.

## Technologies
Backend: Python, Flask
Frontend Integration: Designed to work seamlessly with a frontend built using HTML, CSS, and JavaScript.
Data Handling: Employs OOP principles for efficient data management and API response handling.
