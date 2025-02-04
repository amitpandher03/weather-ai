# WeatherGPT 🌦️🤖

[![Python Version](https://img.shields.io/badge/python-3.13+-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

An AI-powered weather assistant combining OpenAI's GPT-4 with real-time weather data from Open-Meteo.

## Features ✨
- Natural language weather queries
- Real-time weather data integration
- Multilingual support
- 3-day weather forecasting
- Interactive chat interface
- Code syntax highlighting in responses
- Animated UI with Tailwind CSS

## Tech Stack 🛠️
- **Backend**: Python 3.13, Flask
- **Frontend**: Tailwind CSS, JavaScript
- **AI**: OpenAI GPT-4
- **Weather API**: Open-Meteo
- **Tools**: Poetry, Markdown parsing

## Installation 📦

```bash

#Clone repository

git clone https://github.com/amitpandher03/weather-ai.git

cd weather-ai


#Install dependencies with Poetry

poetry install

#Set up environment variables

cp .env.example .env


## Configuration ⚙️
Create `.env` file:

```bash
OPENAI_API_KEY=your_openai_key_here
FLASK_SECRET_KEY=your_flask_secret_key
```

## Usage 🚀

```bash
#Start Flask development server

poetry run flask run
```


Example queries:
- "What's the weather like in Tokyo tomorrow?"
- "Show me 3-day forecast for Paris in Celsius"
- "Will it rain in Mumbai this weekend?"

## API Endpoints 🌐
| Endpoint | Method | Description              |
|----------|--------|--------------------------|
| `/chat`  | POST   | Process weather queries  |

## Screenshots 🖼️
![Chat Interface](/screenshots/image.png)

## License 📄
MIT License - See [LICENSE](LICENSE) for details.

> **Note**: This application may occasionally generate inaccurate weather predictions. Always verify critical information with official sources.