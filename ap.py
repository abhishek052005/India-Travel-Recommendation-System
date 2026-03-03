
import streamlit as st
import pickle
import pandas as pd

# 1. Load data
@st.cache_resource
def load_data():
    try:
        places = pickle.load(open('india_travel_list.pkl', 'rb'))
        similarity = pickle.load(open('similarity_matrix.pkl', 'rb'))
        try:
            popular = pickle.load(open('popularity_df.pkl', 'rb'))
        except:
            popular = None
        return places, similarity, popular
    except Exception as e:
        st.error(f"Error loading files: {e}")
        return None, None, None

places, similarity, popular = load_data()

# 2. Recommendation logic
def get_recommendations(place_name):
    try:
        index = places[places['Name'] == place_name].index[0]
        distances = similarity[index]
        rec_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:7]
        return [places.iloc[i[0]] for i in rec_list]
    except:
        return []

# 3. GLOBAL STATE MANAGER
# This function is the "Brain" that updates everything correctly
def change_place_callback():
    # This reads the value from the dropdown and updates the 'active_place' state
    st.session_state.active_place = st.session_state.main_dropdown

def on_button_click(new_name):
    # This is called when Trending or Card buttons are clicked
    st.session_state.active_place = new_name
    # IMPORTANT: We also update the dropdown's internal state so it changes visually
    st.session_state.main_dropdown = new_name

# Initialize states
if 'active_place' not in st.session_state:
    st.session_state.active_place = places['Name'].iloc[0]





# --- UI START ---
st.set_page_config(page_title="Travel Explorer", layout="wide")
st.title("🗺️ India Travel Recommendation System")

if places is not None:
    # --- 1. TRENDING SECTION ---
    if popular is not None:
        st.subheader("🔥 Trending Destinations")
        st.markdown("Most popular places across India based on user reviews.")

        trending_selection = popular.iloc[1:6]

        trend_cols = st.columns(len(trending_selection))
        t_cols = st.columns(5)
        for i in range(min(5, len(trending_selection))):
            p_name = trending_selection.iloc[i]['Name']
            with t_cols[i]:
                st.success(f"**{p_name}**")
                st.caption(f"📍 {trending_selection.iloc[i]['City']}")
                st.write(f"⭐ {trending_selection.iloc[i]['Google review rating']} | 🎭 {trending_selection.iloc[i]['Type']}")
                # Button updates the state directly
                st.button("Explore", key=f"tr_{i}", on_click=on_button_click, args=(p_name,))

    st.divider()






    # --- 2. THE SEARCH BOX ---
    st.subheader("🤖 Get Personalized Recommendations")
    
    all_names = list(places['Name'].values)
    
    # We use 'key' and 'on_change' to keep the dropdown in sync
    st.selectbox(
        "Select a place you liked or want to visit:", 
        all_names, 
        key="main_dropdown",
        on_change=change_place_callback
    )
    
    # Ensure the dropdown shows the correct 'active_place' if it was changed by a button
    if st.session_state.main_dropdown != st.session_state.active_place:
        st.session_state.main_dropdown = st.session_state.active_place
        st.rerun()

    # --- 3. THE RECOMMENDATION CARDS ---
    recs = get_recommendations(st.session_state.active_place)

    if recs:
        st.write(f"#### Because you liked **{st.session_state.active_place}**, check these out:")
        
        r_cols = st.columns(3)
        for idx, p in enumerate(recs):
            with r_cols[idx % 3]:
                with st.container(border=True):
                    st.info(f"### {p['Name']}")
                    st.write(f"📍 **Location:** {p['City']}, {p['State']}")
                    st.write(f"🎭 **Type:** {p['Type']}")
                    st.write(f"⭐ **Rating:** {p['Google review rating']}/5")
                    st.write(f"⏱️ **Visit Time:** {p['time needed to visit in hrs']} hrs")
                    st.write(f"💰 **Fee:** ₹{p['Entrance Fee in INR']}")
                    
                    # RECURSIVE BUTTON
                    st.button(
                        f"Show Similar", 
                        key=f"card_btn_{idx}_{p['Name']}", 
                        on_click=on_button_click, 
                        args=(p['Name'],)
                    )
    else:
        st.warning("No recommendations found.")