import streamlit as st
import csv
from datetime import datetime
from typing_extensions import override
from openai import OpenAI, AssistantEventHandler
import requests
# Your OpenAI API key and Assistant details
api_key = "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"
assistant_id = "asst_bfVqscYIEFVOMr7WPDvR2xAp"

client = OpenAI(api_key=api_key)
st.set_page_config(layout="wide", page_title="Your App Title", page_icon="🌱")


custom_css = """
    <style>
        /* Targeting the sidebar for a black background color */
        .css-1d391kg, .stSidebar {
            background-color: #c8f584 !important;
            color: #ffffff;
        }

        /* Targeting the sidebar text color */
        .stSidebar .sidebar-content {
            color: #ffffff;
        }

        /* Styling sidebar headers */
        .stSidebar h1 {
            color: #ffffff;
        }

        /* Styling sidebar links */
        .stSidebar a {
            color: #ffffff;
        }

        /* Targeting the main content area background color */
        .stApp {
            background-color: #c9d7ff;
        }

        /* General card styling for navigation */
        .card {
            margin: 16px 0;
            padding: 16px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: box-shadow 0.3s ease-in-out;
            background-color: #ffffff;
        }

        .card:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        /* Styling buttons with a professional look */
        button {
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            background-color: #03c1ff;
            color: #83dffc;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }

        button:hover {
            background-color: #83dffc;
        }

        /* Styling text inputs */
        .stTextInput > div > div > input {
            border-radius: 5px;
            border: 1px solid #ced4da;
            padding: 10px;
        }

        /* Adjusting layout spacings and alignments */
        .stButton > button {
            width: 100%;
            padding: 12px;
            margin-top: 10px;
        }

        /* Custom styling for selectboxes */
        .stSelectbox > div > div {
            border-radius: 5px;
            border: 1px solid #ced4da;
        }

        /* Additional global font styling */
        body {
            font-family: 'Arial', sans-serif;
        }
    </style>
"""

def create_navigation_card(option_name, icon_code, description):
    """Utility function to create a card for the navigation options."""
    st.markdown(f"""
        <div class="card">
            <h2><i class="{icon_code}"></i> {option_name}</h2>
            <p>{description}</p>
        </div>
        """, unsafe_allow_html=True)

class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)
        return "hi"

    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)
def task_manager():
    csv_file = 'tasks.csv'

    def load_tasks_from_csv():
        tasks = []
        try:
            with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    tasks.append(row)
        except FileNotFoundError:
            pass  # File will be created when the first task is added.
        return tasks

    def save_task_to_csv(task):
        tasks = load_tasks_from_csv()
        max_id = 0 if not tasks else max(int(task[0]) for task in tasks)
        task_id = max_id + 1
        with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([task_id] + task)

    def delete_task(task_id):
        tasks = load_tasks_from_csv()
        tasks = [task for task in tasks if task[0] != task_id]
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(tasks)

    col1, spacer, col2 = st.columns([7, 3, 4])

    with col1:
        st.title('🌱 Task Manager')

        task_description = st.text_input('Task Description', placeholder="Enter the task description (e.g., Water plants)")
        days_of_week = st.multiselect('Select Days of the Week', ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        reminder_time = st.time_input('Reminder Time')
        reminder_type = st.selectbox('Reminder Type', ['Email', 'SMS'])
        contact_info = st.text_input(f'Enter your {reminder_type} address', placeholder=f"Your {reminder_type} here")

        if st.button('Add Task'):
            days_selected = ','.join(days_of_week)
            task = [task_description, days_selected, reminder_time.strftime("%H:%M"), reminder_type, contact_info]
            save_task_to_csv(task)
            st.success('Task added successfully!')
            st.experimental_rerun()

    with col2:
        st.title('Scheduled Tasks')
        tasks = load_tasks_from_csv()
        st.markdown('<div class="tasks-container">', unsafe_allow_html=True)
        for task in tasks:
            with st.container():
                col1, col_del = st.columns([5, 1])
                with col1:
                    days_list = task[2].split(',')
                    st.markdown(f"""
                    <div class="task-card">
                        <h4>{task[1]}</h4>
                        <p><b>Days:</b> {', '.join(days_list)}</p>
                        <p><b>Time:</b> {task[3]}</p>
                        <p><b>Type:</b> {task[4]}</p>
                        <p><b>Contact:</b> {task[5]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col_del:
                    if st.button('Delete', key="delete" + task[0]):
                        delete_task(task[0])
                        st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)






def app_run():
    st.title("AgroAI")
    st.caption("Get help to grow green plants from me")

    if 'chat_count' not in st.session_state:
        st.session_state.chat_count = 0
    if 'thread_id' not in st.session_state:
        st.session_state.thread_id = client.beta.threads.create().id

    prompt = st.text_input("Enter your message")
    if prompt:
        res_box = st.empty()
        st.session_state.chat_count += 1
        report = []

        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=str(prompt)
        )

        # Assuming OpenAI's Threads API is used here, with an EventHandler to manage events
        # Note: Implement `EventHandler` class based on your needs.
        event_handler = AssistantEventHandler()

        with client.beta.threads.runs.create_and_stream(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
            event_handler=event_handler,
        ) as stream:
            store = None
            for event in stream:
                if event.data.object == "thread.message.delta":
                    for content in event.data.delta.content:
                        if content.type == 'text':
                            report.append(content.text.value)
                            store = content.text.value

                    if store is not None:
                        result = "".join(report).strip()
                        res_box.markdown(f"`{result}`")

def get_weather_data(city, api_key="4156a452c7d52e7f8837ac90d97aa49d"):
    current_weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"

    current_weather_response = requests.get(current_weather_url)
    current_weather_data = current_weather_response.json()

    forecast_response = requests.get(forecast_url)
    forecast_data = forecast_response.json()

    forecast_processed = []
    for entry in forecast_data.get("list", []):
        date = datetime.utcfromtimestamp(entry["dt"]).strftime('%Y-%m-%d')
        if not any(d['date'] == date for d in forecast_processed):
            forecast_processed.append({
                "date": date,
                "temp_max": entry["main"]["temp_max"],
                "temp_min": entry["main"]["temp_min"],
                "humidity": entry["main"]["humidity"],
                "precipitation": entry.get("rain", {}).get("3h", 0)  # Assume 0 mm if no data
            })

    return {
        "current": {
            "temp_c": current_weather_data.get("main", {}).get("temp"),
            "humidity": current_weather_data.get("main", {}).get("humidity"),
            "wind_kph": current_weather_data.get("wind", {}).get("speed") * 3.6,  # Convert m/s to km/h
            "precipitation": current_weather_data.get("rain", {}).get("1h", 0)  # Assume 0 mm if no data
        },
        "forecast": forecast_processed[:6]  # Only include the next six days
    }

def apply_custom_styles():
    st.markdown(
        """
        <style>
        .main { background-color: #FFFFFF; }
        .stTextInput, .stButton>button { border: 1px solid #4f4f4f; border-radius: 20px; }
        .stTextInput>div>div>input { background-color: #292929; color: black; }
        .stButton>button { background-color: #1db954; color: black; }
        .dashboard-header { color: black; padding-bottom: 0.75em; text-align: center; }
        .dashboard-box { background-color: #333333; padding: 1em; border-radius: 10px; margin-bottom: 1em; }
        .dashboard-text { color: black; margin: 0; font-size: 1em; padding: 0.25em 0; }
        .forecast-row { display: flex; justify-content: space-around; }
        .forecast-card { width: 30%; }
        </style>
        """, unsafe_allow_html=True
    )
def get_city_by_ip(api_key="8cfff43ec029ac"):
    try:
        response = requests.get(f'http://ipinfo.io/json?token={api_key}')
        city = response.json()['city']
    except Exception as e:
        st.error("Failed to get location. Please enter the city manually.")
        return None
    return city
def home_main():
    apply_custom_styles()
    st.markdown('<h1 class="dashboard-header">Agricultural Weather Dashboard</h1>', unsafe_allow_html=True)
    city = get_city_by_ip()
    city = "Chittagong"
    print(city)
    if city == "Chattogram":
        # city = st.text_input("Enter your city", key='city_input')
        city ="Chittagong"
    weather_data = get_weather_data(city)

    # Current weather centered at the top
    st.markdown('<div class="dashboard-box">', unsafe_allow_html=True)
    st.markdown('<h2 class="dashboard-header">Current Weather in ' + city + '</h2>', unsafe_allow_html=True)
    st.markdown(f'<p class="dashboard-text">Temperature: {weather_data["current"]["temp_c"]}°C</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="dashboard-text">Humidity: {weather_data["current"]["humidity"]}%</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="dashboard-text">Wind Speed: {weather_data["current"]["wind_kph"]} km/h</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="dashboard-text">Precipitation (last 1 hr): {weather_data["current"]["precipitation"]} mm</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    cols = [st.columns(3), st.columns(3)]
    for i, day in enumerate(weather_data['forecast']):
        with cols[i // 3][i % 3]:
            st.markdown('<div class="dashboard-box forecast-card">', unsafe_allow_html=True)
            st.markdown(f'<h3 class="dashboard-header">{day["date"]}</h3>', unsafe_allow_html=True)
            st.markdown(f'<p class="dashboard-text">Max Temp: {day["temp_max"]}°C</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="dashboard-text">Min Temp: {day["temp_min"]}°C</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="dashboard-text">Humidity: {day["humidity"]}%</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="dashboard-text">Expected Precipitation: {day["precipitation"]} mm</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
def main():
    st.markdown(custom_css, unsafe_allow_html=True)


    st.sidebar.markdown("<h1 style='color: white; text-align: center;'>Navigation</h1>", unsafe_allow_html=True)

    if st.sidebar.button("Home"):
        st.session_state['current_page'] = 'Home'
    if st.sidebar.button("AI Assist"):
        st.session_state['current_page'] = 'AI Assist'
    if st.sidebar.button("Task Reminder"):
        st.session_state['current_page'] = 'Task Reminder'
    if st.sidebar.button("Closest Nursery Institute"):
        st.session_state['current_page'] = 'Closest Nursery Institute'
    if st.sidebar.button("Plant Disease Predictor"):
        st.session_state['current_page'] = 'Plant Disease Predictor'

    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'Home'  # Default page

    if st.session_state['current_page'] == 'Home':

        home_main()
    elif st.session_state['current_page'] == 'AI Assist':
        app_run()  # Call your AI Assist functionality

    elif st.session_state['current_page'] == 'Task Reminder':
        task_manager()  # Call your Task Manager functionality



if __name__ == "__main__":
    main()
