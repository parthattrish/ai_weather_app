from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# ✅ Your API keys
WEATHER_API_KEY = "edcc6078ab2e4cc8847100037250108"  # WeatherAPI key
GEMINI_API_KEY = "AIzaSyA3jXJFQ_yV_dgnhQBeVIpev-If6VPPYM4"  # Gemini key

@app.route("/")
def home():
    return render_template("index.html")

# ✅ Weather API Route
@app.route("/get_weather", methods=["POST"])
def get_weather():
    city = request.json.get("city")

    # ✅ Using WeatherAPI.com
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&aqi=yes"
    response = requests.get(url).json()
    print(response)  # Debug print
    return jsonify(response)

# ✅ Gemini API Route
@app.route("/ask_gemini", methods=["POST"])
def ask_gemini():
    user_query = request.json.get("query")
    city = request.json.get("city")
    category = request.json.get("category")  # ✅ check what type of query is coming

    # ✅ If the query is "other" → no weather data
    if category == "other":
        prompt = f"User's question: {user_query}\nAnswer in a detailed and simple way."
    else:
        # ✅ Fetch live weather for the given city
        weather_url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&aqi=yes"
        weather_response = requests.get(weather_url).json()

        if "error" in weather_response:
            weather_summary = f"Weather data for {city} could not be retrieved."
        else:
            weather_summary = (
                f"Current weather in {weather_response['location']['name']}, {weather_response['location']['country']}: "
                f"{weather_response['current']['condition']['text']}, {weather_response['current']['temp_c']}°C, "
                f"humidity {weather_response['current']['humidity']}%, wind speed {weather_response['current']['wind_kph']} kph."
            )

        prompt = f"{weather_summary}\nUser’s question: {user_query}\nAnswer based on the above weather information."

    # ✅ Send prompt to Gemini
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers).json()
    print(response)  # Debug print in console

    try:
        answer = response["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        answer = "❌ Sorry, I couldn’t get a response."

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
