import os
import streamlit as st
from openai import OpenAI
import requests
import json
from langchain.agents import create_agent

# location can be a city, a zip code, an airport code ('SYR'),
# or a landmark ('Eiffel+Tower')
# note: hard codes units to degrees Fahrenheit
def get_weather_data(location: str = "Syracuse, NY") -> dict:
    """This tool retrieves weather information based on a city name and provides
    clothing suggestions and advice for weather-appropriate outdoor activities."""
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

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

agent = create_agent(
    model="openai:gpt-5-mini", 
    tools=[get_weather_data], 
    system_prompt="You are a helpful assistant that gives clothing suggestions and outdoor activity advice based on the weather. Use the weather tool to get current conditions.", 
)

if st.button("Get Advice"):
    result = agent.invoke(
        {"messages": [{"role": "user", "content": f"What should I wear in {location}?"}]}
    )

    with st.chat_message("assistant"):
        st.write(result["messages"][-1].content)

    # Part D
    with st.expander("Behind the scenes"):
        for message in result["messages"]:
            st.write(f"**{message.type}**")
            st.write(message.content)
            if message.type == "ai" and getattr(message, "tool_calls", None):
                st.write(message.tool_calls)
    # a) There are 4 messages total: 'human' (the user's initial prompt),
    # 'ai' (the model deciding to call the tool), 'tool' (the JSON results returned from get_weather_data),
    # and 'ai' (the model's final response based on the tool's data).

    # b) The second message (type: 'ai') asks for the tool. 
    # The request is stored in its `tool_calls` attribute rather than the `content` attribute.

    # c) In Lab 5, the user message was created manually when we appended {"role": "user", "content": ...} 
    # to the messages list. The AI tool call was created by the first `client.chat.completions.create` 
    # API call and manually appended to the history.The tool message was created by manually parsing the tool call, 
    # executing the function, and appending {"role": "tool", "content": result}.
    # The AI's final response was created by the second `client.chat.completions.create` API call.