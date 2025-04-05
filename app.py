import streamlit as st
import os
from openai import OpenAI

# Streamlit Page Configuration
st.set_page_config(page_title="AI Executive Coaching MVP", layout="wide")

# Set OpenAI API key from Streamlit secrets
api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

# Sidebar Filters and Scenario Selection
st.sidebar.header("Manager Profile")
industry = st.sidebar.selectbox(
    "Industry",
    ["Technology", "Finance", "Healthcare", "Professional Services", "Other"]
)

company_size = st.sidebar.selectbox(
    "Company Size",
    ["Small (1-50)", "Medium (51-500)", "Large (501-5000)", "Enterprise (5000+)"]
)

manager_level = st.sidebar.selectbox(
    "Manager Level",
    ["New Manager", "Experienced Middle Manager", "Senior Manager"]
)

st.sidebar.markdown("---")
scenario_tab = st.sidebar.radio("Choose Interaction Type", ["Coaching Chat", "Role-Play Scenarios"])
st.sidebar.markdown("---")
st.sidebar.info("Customize your profile to receive personalized coaching advice.")

# Predefined role-play scenarios
scenarios = {
    "Giving Tough Feedback": "Employee is coming in for a performance review. Manager is giving feedback to a talented employee whose recent performance has declined.",
    "Motivating a Disengaged Team Member": "High-performing team member feeling disengaged comes to talk to their manager.",
    "Resolving Conflict": "Two key team members have ongoing conflicts affecting team morale.",
    "Preparing for a Difficult Meeting": "Manager talking to their colleague in preparation for a challenging update in an upcoming meeting with the leadership team."
}

# Main Interface
st.title("AI Coaching Chat")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if scenario_tab == "Role-Play Scenarios":
    st.header("Interactive Role-Play Scenarios")
    selected_scenario = st.selectbox("Select a scenario to practice:", list(scenarios.keys()))
    scenario_description = scenarios[selected_scenario]
    st.write(f"**Scenario:** {scenario_description}")

    if st.button("Start New Role-Play"):
        st.session_state["messages"] = []
        initial_prompt = (
            f"Simulate a realistic dialogue as an employee or colleague named Rishabh, talking to their manager names Warren based on the following scenario:\n\n"
            f"{scenario_description}\n\nBegin the conversation with just the first line you would say to the manager."
        )
        with st.spinner("Initiating scenario..."):
            response = client.responses.create(
                model="gpt-4o",
                instructions="Role-play with a manager as an employee or colleague realistically and naturally",
                input=initial_prompt,
            )
            st.session_state.messages.append({"role": "assistant", "content": response.output_text})

    # Display chat history and enable reply
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if user_reply := st.chat_input("Your response:"):
        st.session_state.messages.append({"role": "user", "content": user_reply})
        with st.chat_message("user"):
            st.write(user_reply)

        conversation_history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])

        with st.chat_message("assistant"):
            with st.spinner("Generating response..."):
                try:
                    follow_up_response = client.responses.create(
                        model="gpt-4o",
                        instructions="Continue the realistic role-play as an employee initiating a conversation with their manager based on the dialogue provided.",
                        input=conversation_history,
                    )
                    st.write(follow_up_response.output_text)
                    st.session_state.messages.append({"role": "assistant", "content": follow_up_response.output_text})
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

else:
    # Standard coaching chat interface
    st.markdown("**Example Prompts:**")
    st.markdown("*How do I provide constructive feedback to a high-performing employee whose behavior is negatively affecting team morale?*")
    st.markdown("*What are some strategies to boost motivation and productivity in my fully remote team?*")   
    st.markdown("*I have an upcoming one-on-one to discuss performance concerns. What's the best way to approach this conversation sensitively and effectively?*")
    st.markdown("*I’m overwhelmed by my current workload and competing priorities. How can I prioritize tasks more effectively as a manager?*")
    
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("Describe your managerial challenge:"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Generating tailored coaching advice..."):
                full_prompt = (
                    f"You are an executive coach helping Warren, a {manager_level.lower()} in a "
                    f"{company_size.lower()} company within the {industry.lower()} industry. "
                    f"First provide an empathetic 1 line summary of their ask and their industry, company size, and manager level. Then, ask them 1 clarifying question on their challenge.\n\n"
                    f"Before proceeding to provide practical, clear, and actionable advice to address the following challenge:\n\n"
                    f"{prompt}"
                )
                try:
                    response = client.responses.create(
                        model="gpt-4o",
                        instructions="Provide empathetic, actionable, and concise executive coaching advice.",
                        input=full_prompt,
                    )
                    advice = response.output_text
                    st.write(advice)
                    st.session_state.messages.append({"role": "assistant", "content": advice})
                except Exception as e:
                    error_message = f"An error occurred: {str(e)}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
