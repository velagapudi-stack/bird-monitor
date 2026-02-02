import streamlit as st
import pandas as pd
import os
from datetime import date, datetime

# --- CONFIGURATION ---
FILE_NAME = 'bird_data.csv'

# Pre-defined coordinates for known locations (Lat, Lon)
# Based on Alligator Creek, Sarasota County, FL
LOCATION_COORDS = {
    "Alligator Creek": [27.042, -82.430],
    # Add other locations here if you expand monitoring sites in the future
    # "Lemon Bay": [26.960, -82.353],
}

# Corrected Species List (AOU Codes and Common Names)
SPECIES_LIST = [
    "Palm Warbler (PAWA)", 
    "Red-bellied Woodpecker (RBWO)", 
    "Great Egret (GREG)", 
    "Blue Jay (BLJA)", 
    "Carolina Wren (CAWR)", 
    "Fish Crow (FICR)", 
    "Northern Cardinal (NOCA)", 
    "Tricolored Heron (TRHE)", 
    "Red-shouldered Hawk (RSHA)", 
    "Yellow-rumped Warbler (YRWA)", 
    "Wood Stork (WOST)", 
    "White Ibis (WHIB)", 
    "Eastern Phoebe (EAPH)", 
    "Little Blue Heron (LBHE)", 
    "Mourning Dove (MODO)", 
    "Blue-gray Gnatcatcher (BGGN)", 
    "Gray Catbird (GRCA)", 
    "Common Grackle (COGR)", 
    "Tufted Titmouse (TUTI)", 
    "Downy Woodpecker (DOWO)", 
    "Sandhill Crane (SACR)"
]

def load_data():
    if os.path.exists(FILE_NAME):
        return pd.read_csv(FILE_NAME)
    else:
        columns = [
            "Date", "Location", "Recorder", "Start Time", "End Time",
            "Wind", "Precipitation", "Tide", "Temperature",
            "Species", "Count_le_50m", "Count_gt_50m", "Flythrough", "Notes"
        ]
        return pd.DataFrame(columns=columns)

def save_data(df):
    df.to_csv(FILE_NAME, index=False)

# --- MAIN APP UI ---
st.set_page_config(page_title="Alligator Creek Bird Monitor", layout="wide")

st.title("🦅 Alligator Creek Bird Monitoring Project")
st.markdown("Digital Point Count Collection Form")

tab1, tab2 = st.tabs(["📝 New Entry", "📊 View Data & History"])

# --- TAB 1: DATA ENTRY ---
with tab1:
    with st.form("entry_form"):
        st.subheader("Field Conditions")
        c1, c2, c3 = st.columns(3)
        with c1:
            entry_date = st.date_input("Date", value=date.today())
            
            # Location Logic: Dropdown with known locations + "Other" option
            loc_options = list(LOCATION_COORDS.keys()) + ["Other"]
            loc_selection = st.selectbox("Location ID", loc_options)
            
            if loc_selection == "Other":
                location = st.text_input("Enter New Location Name")
            else:
                location = loc_selection
                
            recorder = st.text_input("Recorder/Censuser")
        with c2:
            start_time = st.time_input("Start Time", value=datetime.now().time())
            end_time = st.time_input("End Time", value=datetime.now().time())
            temp = st.text_input("Temperature (e.g., 36°F)")
        with c3:
            wind = st.text_input("Wind (e.g., 7mph NE)")
            precip = st.text_input("Precipitation")
            tide = st.text_input("Tide")

        st.divider()
        st.subheader("Species Counts")
        
        species_entries = []
        st.info("Enter counts below. Leave 0 if not seen.")
        
        # Grid Layout for Species
        for sp in SPECIES_LIST:
            with st.expander(f"{sp}", expanded=False):
                col_a, col_b, col_c, col_d = st.columns([1, 1, 1, 3])
                with col_a:
                    c_50 = st.number_input(f"≤50m", min_value=0, key=f"{sp}_50")
                with col_b:
                    c_gt50 = st.number_input(f">50m", min_value=0, key=f"{sp}_gt50")
                with col_c:
                    c_fly = st.number_input(f"Flythru", min_value=0, key=f"{sp}_fly")
                with col_d:
                    notes = st.text_input(f"Notes", key=f"{sp}_note")
                
                if c_50 > 0 or c_gt50 > 0 or c_fly > 0:
                    species_entries.append({
                        "Species": sp, "Count_le_50m": c_50, "Count_gt_50m": c_gt50, 
                        "Flythrough": c_fly, "Notes": notes
                    })

        st.markdown("**Add Other Species**")
        other_sp = st.text_input("Species Code/Name")
        c1_o, c2_o, c3_o, c4_o = st.columns([1,1,1,3])
        o_50 = c1_o.number_input("≤50m", min_value=0, key="other_50")
        o_gt50 = c2_o.number_input(">50m", min_value=0, key="other_gt50")
        o_fly = c3_o.number_input("Flythru", min_value=0, key="other_fly")
        o_note = c4_o.text_input("Notes", key="other_note")

        submitted = st.form_submit_button("Save Entry")

        if submitted:
            if other_sp and (o_50 > 0 or o_gt50 > 0 or o_fly > 0):
                species_entries.append({
                    "Species": other_sp, "Count_le_50m": o_50, "Count_gt_50m": o_gt50, 
                    "Flythrough": o_fly, "Notes": o_note
                })
            
            if not species_entries:
                st.warning("No bird counts entered!")
            else:
                df = load_data()
                new_rows = []
                for entry in species_entries:
                    row = {
                        "Date": entry_date, "Location": location, "Recorder": recorder,
                        "Start Time": start_time, "End Time": end_time, "Wind": wind,
                        "Precipitation": precip, "Tide": tide, "Temperature": temp,
                        "Species": entry["Species"], "Count_le_50m": entry["Count_le_50m"],
                        "Count_gt_50m": entry["Count_gt_50m"], "Flythrough": entry["Flythrough"],
                        "Notes": entry["Notes"]
                    }
                    new_rows.append(row)
                
                df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
                save_data(df)
                st.success(f"Saved {len(species_entries)} species records for {entry_date}!")

# --- TAB 2: DATA VISUALIZATION ---
with tab2:
    st.header("Historical Data & Map")
    
    df = load_data()
    
    if not df.empty:
        # Filters
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            loc_filter = st.multiselect("Filter by Location", options=df["Location"].unique())
        with col_f2:
            dates = pd.to_datetime(df["Date"]).dt.date.