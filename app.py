import streamlit as st
import re
# Az OpenAI kliens tökéletesen kezeli a Groq-ot is, csak az alap URL-t kell átállítani!
from openai import OpenAI 

st.set_page_config(page_title="Green City MI Tutor", page_icon="🌱")
st.title("🌱 Green City - Szókratészi MI Mentor")

# A Groq ingyenes API kulcsát a Streamlit Secrets-be fogod bemásolni
# Az alap URL-t pedig átirányítjuk a Groq szuperszámítógépeire
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=st.secrets["GROQ_API_KEY"]
)

szerep = st.selectbox(
    "Válaszd ki a szerepköredet a projektben:",
    ["Várostervező mérnök", "Környezetvédelmi szakértő", "Digitális technológus", "Társadalmi koordinátor"]
)

CORE_SYSTEM_PROMPT = f"Te egy szigorúan a Szókratészi módszert alkalmazó MI Tutor vagy... (a fenti prompt jön ide)"

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "display_text": f"Üdvözöllek, mint a Green City projekt {szerep}e! Mi az első gondolatod a feladatoddal kapcsolatban?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["display_text"])

if user_input := st.chat_input("Írj ide a mentornak..."):
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "display_text": user_input})

    api_messages = [{"role": "system", "content": CORE_SYSTEM_PROMPT}]
    for msg in st.session_state.messages:
        content = msg.get("raw_text", msg["display_text"])
        api_messages.append({"role": msg["role"], "content": content})

    with st.chat_message("assistant"):
        with st.spinner("Gondolkodom a következő kérdésen..."):
            
            # Itt a Groq bivalyerős és ingyenes Llama 3.1 70B modelljét hívjuk meg!
            response = client.chat.completions.create(
                model="llama3-8b-8192", 
                messages=api_messages,
                temperature=0.5
            )
            raw_ai_response = response.choices[0].message.content
            
            # Regex szűrés ugyanaz...
            thought_match = re.search(r'\[THOUGHT\](.*?)\[/THOUGHT\]', raw_ai_response, re.DOTALL)
            response_match = re.search(r'\[RESPONSE\](.*?)\[/RESPONSE\]', raw_ai_response, re.DOTALL)
            
            clean_response = response_match.group(1).strip() if response_match else raw_ai_response.replace("[RESPONSE]", "").replace("[/RESPONSE]", "").strip()
            st.write(clean_response)
            
            st.session_state.messages.append({
                "role": "assistant",
                "display_text": clean_response,
                "raw_text": raw_ai_response
            })
