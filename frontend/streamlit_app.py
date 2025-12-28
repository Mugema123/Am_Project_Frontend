import streamlit as st
import requests

# ================================
# PAGE CONFIG
# ================================
st.set_page_config(
    page_title="Flight Delay Intelligence Assistant",
    layout="centered"
)

# ================================
# SESSION STATE INITIALIZATION
# ================================
if "prediction_result" not in st.session_state:
    st.session_state.prediction_result = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ================================
# TITLE
# ================================
st.title("✈️ Flight Delay Intelligence Assistant")
st.write("Enter flight details to predict delay risk and ask follow-up questions.")

# ================================
# FLIGHT INPUT FORM
# ================================
with st.form("flight_form"):
    UNIQUE_CARRIER = st.text_input("Carrier Code (e.g. DL)")
    ORIGIN = st.text_input("Origin Airport (e.g. CHA)")
    DEST = st.text_input("Destination Airport (e.g. ATL)")

    DEP_TIME_CATEGORY = st.selectbox(
        "Departure Time Category",
        ["Morning", "Afternoon", "Evening", "Night"]
    )

    DAY_OF_WEEK = st.number_input(
        "Day of Week (1 = Monday)", min_value=1, max_value=7
    )
    MONTH = st.number_input("Month", min_value=1, max_value=12)
    DAY_OF_MONTH = st.number_input("Day of Month", min_value=1, max_value=31)

    DISTANCE = st.number_input(
        "Distance (miles)", min_value=0.0
    )
    ROUTE_DELAY_RATE = st.number_input(
        "Route Delay Rate (0–1)", min_value=0.0, max_value=1.0
    )

    submitted = st.form_submit_button("Predict Delay Risk")

# ================================
# PREDICTION CALL
# ================================
if submitted:
    payload = {
        "UNIQUE_CARRIER": UNIQUE_CARRIER,
        "ORIGIN": ORIGIN,
        "DEST": DEST,
        "DEP_TIME_CATEGORY": DEP_TIME_CATEGORY,
        "DAY_OF_WEEK": DAY_OF_WEEK,
        "MONTH": MONTH,
        "DAY_OF_MONTH": DAY_OF_MONTH,
        "DISTANCE": DISTANCE,
        "ROUTE_DELAY_RATE": ROUTE_DELAY_RATE
    }

    try:
        response = requests.post(
            "https://flight-delay-api-4kxq.onrender.com/predict",
            json=payload,
            timeout=20
        )

        if response.status_code == 200:
            st.session_state.prediction_result = response.json()

            st.success(
                f"Delay Risk: **{st.session_state.prediction_result['delay_risk']}**"
            )
            st.metric(
                "Delay Probability",
                f"{st.session_state.prediction_result['delay_probability']:.2%}"
            )

            # Reset chat when new prediction is made
            st.session_state.chat_history = []

        else:
            st.error("Prediction API error occurred.")

    except Exception as e:
        st.error(f"Connection error: {e}")

# ================================
# CHAT SECTION
# ================================
st.divider()
st.subheader("💬 Ask the AI Assistant")

user_query = st.text_input(
    "Ask a question about this flight (e.g., 'Should I book this flight?')"
)

if user_query:
    if st.session_state.prediction_result is None:
        st.warning("Please predict delay risk first.")
    else:
        chat_payload = {
            "query": user_query,
            "context": st.session_state.prediction_result
        }

        try:
            chat_response = requests.post(
                "https://flight-delay-api-4kxq.onrender.com/chat",
                json=chat_payload,
                timeout=20
            )

            if chat_response.status_code == 200:
                reply = chat_response.json()["response"]

                st.session_state.chat_history.append(("You", user_query))
                st.session_state.chat_history.append(("Assistant", reply))
            else:
                st.error("Chat API error occurred.")

        except Exception as e:
            st.error(f"Chat connection error: {e}")

# ================================
# DISPLAY CHAT HISTORY
# ================================
for speaker, message in st.session_state.chat_history:
    if speaker == "You":
        st.markdown(f"**🧑 You:** {message}")
    else:
        st.markdown(f"**🤖 Assistant:** {message}")
