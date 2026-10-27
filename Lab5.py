import streamlit as st
from openai import OpenAI
import requests
import json

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# location can be a city, a zip code, an airport code ('SYR'),
# or a landmark ('Eiffel+Tower')
# note: hard codes units to degrees Fahrenheit
def get_current_weather(location):
    url = f'https://wttr.in/{location}?format=j1'
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        raise Exception(f'wttr.in error: status {response.status_code}')
    try:
        data = response.json()
    except ValueError:
        # unknown locations come back as plain text, not JSON
        raise Exception(f'Could not find a location named {location}')
        # j1 has three top-level sections:
        # current_condition -- one entry, conditions right now
        # weather -- three entries, one per day, each with
        # min/max, astronomy, and hourly forecasts
        # nearest_area -- the location wttr.in actually matched
    current = data['current_condition'][0]
    today = data['weather'][0]

    return {'location': location,
        'location': location,
        'temperature': float(current['temp_F']),
        'feels_like': float(current['FeelsLikeF']),
        'high_temp': float(today['maxtempF']),
        'low_temp': float(today['mintempF']),
        'description': current['weatherDesc'][0]['value']
    }

st.title("What to Wear Bot")
st.write("Enter a location to get clothing suggestions and outdoor activity advice based on today's weather.")

location_input = st.text_input("Enter a city, zip code, or landmark:", placeholder="i.e. Syracuse, NY")

if st.button("Get Advice"):
    with st.spinner("Checking the weather and gathering advice..."):
        # Define the tool for OpenAI
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "description": "Get the current weather and today's forecast for a given location. If no location is provided, default to 'Syracuse, NY'.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g., Syracuse, NY."
                            }
                        },
                        "required": ["location"],
                    },
                }
            }
        ]

        # Initial messages setup
        messages = [
            {"role": "system", "content": "You are a helpful assistant that gives clothing suggestions and outdoor activity advice based on the weather. Use the weather tool to get current conditions."},
            {"role": "user", "content": f"What should I wear and what outdoor activities should I do today in {location_input if location_input else 'Syracuse, NY'}?"}
        ]

        # First API call to trigger the tool
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        messages.append(response_message)

        # Check if the LLM decided to call the tool
        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                if tool_call.function.name == "get_current_weather":
                    # Extract the location argument
                    function_args = json.loads(tool_call.function.arguments)
                    loc = function_args.get("location", "Syracuse, NY")
                    
                    try:
                        # Execute the function
                        weather_info = get_current_weather(loc)
                        tool_content = json.dumps(weather_info)
                    except Exception as e:
                        tool_content = str(e)
                    
                    # Append the tool's response to the message history
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": "get_current_weather",
                        "content": tool_content,
                    })
            
            # Second call to the API to generate the final advice using the weather data
            second_response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=messages
            )
            
            # Output the final advice
            st.success("Here is your advice!")
            st.markdown(second_response.choices[0].message.content)
        else:
            # Fallback if no tool was called
            st.markdown(response_message.content)