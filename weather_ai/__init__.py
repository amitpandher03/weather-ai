from openai import OpenAI
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_weather(location: str, unit: str = "fahrenheit", format: str = "text", forecast_days: int = 0) -> str:
    """Get weather data for a location
    Args:
        forecast_days: 0 = current weather, 1-16 = forecast days
    """
    try:
        # First get coordinates from location name
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {
            "name": location,
            "count": 1,
            "language": "en",
            "format": "json"
        }
        
        geo_response = requests.get(geo_url, params=geo_params)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        
        if not geo_data.get("results"):
            return f"Error: Location '{location}' not found"
            
        coordinates = geo_data["results"][0]
        lat = coordinates["latitude"]
        lon = coordinates["longitude"]
        
        # Modified weather params
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,weather_code,precipitation",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
            "temperature_unit": "fahrenheit" if unit == "fahrenheit" else "celsius",
            "forecast_days": 1 if forecast_days > 0 else 0,  # 1 day = current
            "timezone": "auto"
        }

        if forecast_days > 0:
            weather_params.update({
                "forecast_days": forecast_days,
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_mean,precipitation_sum"
            })

        # Then get weather for coordinates
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_response = requests.get(weather_url, params=weather_params)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        if "current" not in weather_data:
            return f"Error: No weather data available for {location}"
            
        if format == "json":
            return json.dumps(weather_data)

        # Modified text response
        if forecast_days > 0:
            forecast = []
            for i in range(forecast_days):
                day = weather_data['daily']
                forecast.append(
                    f"Day {i+1}: {day['temperature_2m_max'][i]}°{unit[0].upper()}/"
                    f"{day['temperature_2m_min'][i]}°{unit[0].upper()}, "
                    f"Precipitation: {day['precipitation_sum'][i]}mm"
                )
            return f"Weather forecast for {location}:\n" + "\n".join(forecast)
            
        current = weather_data['current']
        return (
            f"Current weather in {location}:\n"
            f"- Temperature: {current['temperature_2m']}°{unit[0].upper()}\n"
            f"- Conditions: {weather_code_to_text(current['weather_code'])}\n"
            f"- Precipitation: {current['precipitation']}mm"
        )
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {str(e)}"
    except (KeyError, IndexError) as e:
        return f"Error processing data: {str(e)}"

def chat(query: str, history: list = None) -> str:
    """Handle chat conversation with weather tool integration"""
    messages = history or []
    messages = messages.copy()
    
    # Add system message at start
    if not any(msg['role'] == 'system' for msg in messages):
        messages.insert(0, {
            "role": "developer",
            "content": """STrictly follow these location rules:
                        1. If unsure of spelling, verify with user before using
                        2. Never translate or anglicize location names
                        3. most importantly, always give the temperature in celsius and detect the language of the user and give the temperature in the language of the user
                        4. strictly follow the last prompts from the user for the location
                        """


        })
    


    messages.append({"role": "user", "content": query})
    
    tools = [{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather or forecast for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City and country"},
                    "unit": {"type": "string", "enum": ["fahrenheit", "celsius"], "default": "fahrenheit"},
                    "format": {"type": "string", "enum": ["text", "json"], "default": "text"},
                    "forecast_days": {"type": "integer", "description": "Number of forecast days (0=current)", "default": 0}
                },
                "required": ["location"]
            }
        }
    }]
    
    # First API call to determine if tool should be used
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    
    print("\n=== First API Response ===")  # Debug log
    print(response.choices[0].message)  # Debug log
    
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    if tool_calls:
        messages.append(response_message)
        
        for tool_call in tool_calls:
            if tool_call.function.name == "get_weather":
                args = json.loads(tool_call.function.arguments)
                print(f"\n=== Calling get_weather with args: {args} ===")  # Debug log
                
                weather_result = get_weather(**args)
                print(f"=== Weather result: {weather_result} ===")  # Debug log
                
                messages.append({
                    "role": "tool",
                    "content": weather_result,
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name
                })

        # Second API call to generate final response
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        print("\n=== Final API Response ===")  # Debug log
        print(final_response.choices[0].message.content)  # Debug log
        
        return final_response.choices[0].message.content
    
    return response_message.content

# Add weather code mapping
def weather_code_to_text(code: int) -> str:
    WMO_CODES = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        56: "Freezing drizzle",
        61: "Light rain",
        66: "Freezing rain",
        80: "Light rain showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail"
    }
    return WMO_CODES.get(code, "Unknown weather conditions")

