from openai import OpenAI
import streamlit as st
from trip_agents import guide_expert, location_expert, planner_expert
from trip_tasks import location_task, guide_task, planner_task
from crewai import Crew, Process





st.title("AI Travel Planner") 
st.write("Please use this app only once for testing as it uses Openai API and App link will be valid till 31st March 2025 ")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "details" not in st.session_state:
    st.session_state.details = []

content="""You are an AI travel assistant designed to help travelers plan their trips by refining their details and creating a personalized day-by-day itinerary based on their preferences, budget, and travel constraints. Your responses should be structured, clear, and engaging to ensure a seamless planning experience. Your first goal is to gather essential travel details such as budget (budget-friendly, mid-range, or luxury), trip duration or specific travel dates, destination and starting location, purpose of travel (leisure, adventure, business, honeymoon, cultural exploration, solo travel, family vacation, etc.), and personal preferences like interests in history, food, nightlife, nature, shopping, or adventure sports. If any details are unclear or missing, you should ask follow-up questions in a friendly, conversational manner to refine the input before proceeding. Once the core travel details are collected, further enhance the itinerary by gathering information on dietary preferences (vegetarian, vegan, halal, kosher, allergies, or specific cuisines), activity interests (hidden gems, must-see landmarks, cultural immersion, relaxation, adventure), walking tolerance or mobility concerns, accommodation preferences (luxury, mid-range, budget, boutique, central location, beachfront), and transportation preferences (public transport, private taxis, rental cars, or walking-friendly destinations). If any of these details are not provided, you should proactively engage the user to ensure the itinerary is fully customized to their needs.**inform the user that their travel plan is ready to be finalized and ask them to click the 'Generate Plan' button. Do not proceed further beyond this point."""
# Define the custom system prompt
system_prompt = {
    "role": "system",
    "content": content
    }

# Add system prompt only if the messages list is empty
if not st.session_state.messages:
    st.session_state.messages.append(system_prompt)

# Display previous chat messages
for message in st.session_state.messages:
    if message["role"] != "system":  # Hide system message from UI
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.details.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.details.append({"role": "assistant", "content": response})

   

# Add spacing below chat window
st.write("\n\n")


def extraction(convo):
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        extraction_prompt ="You are an AI travel assistant designed to extract and summarize key travel details from user conversations, focusing only on the most relevant information for trip planning. Your goal is to categorize the extracted details clearly and concisely under specific parameters: budget constraints, trip duration or travel dates, destination and starting location, purpose of travel, and user preferences. Preferences include dietary restrictions, specific interests (such as history, nature, or adventure sports), mobility considerations, and accommodation preferences. The extracted information should be structured in an easy-to-read format while omitting any irrelevant details. If any details are missing, do not infer or assume information—only present what has been explicitly stated by the user."
        extracted_info = client.chat.completions.create( model=st.session_state["openai_model"],messages=[{"role": "system","content": extraction_prompt}, {"role": "user", "content": convo} ] )
        ex_details=extracted_info.choices[0].message.content
        st.session_state.extracted_details=[]
        st.session_state.extracted_details.append(extracted_info.choices[0].message.content)
        message=st.session_state.extracted_details
        st.write(ex_details)
        return ex_details


if st.button("🚀 Generate Travel Plan"):
        
        message=extraction(str(st.session_state.details))
        # Initialize Tasks
        loc_task = location_task(location_expert, message)
        guid_task = guide_task(guide_expert, message)
        plan_task = planner_task([loc_task, guid_task], planner_expert, message)

        # Define Crew
        crew = Crew(
            agents=[location_expert, guide_expert, planner_expert],
            tasks=[loc_task, guid_task, plan_task],
            process=Process.sequential,
            full_output=True,
            verbose=True,
        )

        # Run Crew AI
        result = crew.kickoff()

        # Display Results
        st.subheader("✅ Your AI-Powered Travel Plan")
        st.markdown(result)


        # Ensure result is a string
        travel_plan_text = str(result)  # ✅ Convert CrewOutput to string

        st.download_button(
            label="📥 Download Travel Plan",
            data=travel_plan_text,  # ✅ Now passing a valid string
            file_name=f"Travel_Plan.txt",
            mime="text/plain"
        )
