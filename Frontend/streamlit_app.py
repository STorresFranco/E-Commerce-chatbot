import sys, os
sys.path.append(os.path.abspath("."))

import streamlit as st
import Backend.faq as faq
import Backend.sql as sql
import Backend.conversation as conv
from Backend.semantic_routing import rl

# --- initialize FAQ collection
client = faq.initializer()
collection = faq.create_collection(client, "faqs_collection")
rl = rl

# --- helper ---
def process_query(route, query):
    """Run the correct backend branch once route + query are known."""
    if route == "FAQ":
        client = faq.initializer()
        return faq.faq_chain(client, query, "faqs_collection")
    elif route == "Products":
        return sql.concatenated_process(query)
    elif route == "Conversation":
        return conv.conv_response(query)
    return "Please provide query related to FAQs, products, or conversation."


# --- UI ---
st.title("🛍️ E-Commerce Chatbot")

# session setup
if "history" not in st.session_state:
    st.session_state.history = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None
if "manual_route" not in st.session_state:
    st.session_state.manual_route = None

# display history
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# step 1: new query from user
query = st.chat_input("Write your query")
if query:
    st.session_state.pending_query = query
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.history.append({"role": "user", "content": query})

# step 2: if we have a query but no route yet → classify or ask user
if st.session_state.pending_query and not st.session_state.manual_route:
    route_res = rl.router(st.session_state.pending_query)
    route = route_res.name if route_res and route_res.name else None

    if not route:
        st.warning("⚠️ I couldn't classify this query. Please choose a route:")
        c1, c2, c3 = st.columns(3)
        chosen_route = None
        if c1.button("💬 Conversation"):
            chosen_route = "Conversation"
        if c2.button("❓ FAQ"):
            chosen_route = "FAQ"
        if c3.button("🛒 Products"):
            chosen_route = "Products"

        # 👉 run immediately when user clicks
        if chosen_route:
            st.session_state.manual_route = chosen_route
            answer = process_query(chosen_route, st.session_state.pending_query)
            with st.chat_message("assistant"):
                st.markdown(answer)
            st.session_state.history.append({"role": "assistant", "content": answer})
            st.session_state.pending_query = None
            st.session_state.manual_route = None
            st.stop()  # stop after showing result
        else:
            st.stop()
    else:
        st.session_state.manual_route = route


# step 3: once both query + route exist → run backend and show answer
if st.session_state.pending_query and st.session_state.manual_route:
    answer = process_query(st.session_state.manual_route, st.session_state.pending_query)
    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.history.append({"role": "assistant", "content": answer})
    # reset for next turn
    st.session_state.pending_query = None
    st.session_state.manual_route = None
