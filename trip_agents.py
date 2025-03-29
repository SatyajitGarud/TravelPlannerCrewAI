from crewai import Agent
from trip_tools import search_web_tool
from dotenv import load_dotenv
import streamlit as st
import os
load_dotenv()


from langchain_community.chat_models import ChatOpenAI

llm = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# Agents
guide_expert = Agent(
    role="Local Expert at this city",
    goal="Provide the BEST insights about the selected city",
    backstory="""A knowledgeable local guide with extensive information
        about the city, it's attractions and customs""",
    tools=[search_web_tool],
    verbose=True,
    max_iter=5,
    llm=llm,
    allow_delegation=False,
)

location_expert = Agent(
    role="Travel Trip Expert",
    goal="Provides travel logistics and essential information.",
    backstory="A seasoned traveler who knows everything about different cities.",
    tools=[search_web_tool],  
    verbose=True,
    max_iter=5,
    llm= llm,   # ChatOpenAI(temperature=0, model="gpt-4o-mini"),
    allow_delegation=False,
)

planner_expert = Agent(
    role="Amazing Travel Concierge",
    goal="""Create the most amazing travel itineraries with budget and 
        packing suggestions for the city""",
    backstory="""Specialist in travel planning and logistics with 
        decades of experience""",
    tools=[search_web_tool],
    verbose=True,
    max_iter=5,
    llm=llm,
    allow_delegation=False,
)
