import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# Create the engine
engine = create_engine("mysql+pymysql://root:shawn@localhost:3306/Foodwaste")
st.set_page_config(page_title="Food Wastage Management System", layout="wide")
st.title("Local Food Wastage Management System")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Introduction", "15 Queries", "CRUD Operations", "Filter & Contact"]
)

# --- Introduction Tab ---
with tab1:
    st.header("Welcome to the Local Food Wastage Management System")
    st.markdown("""
Food wastage is a significant global issue: numerous households and restaurants discard surplus food, while many people face food insecurity.

**Project Goal:**  
To develop a Local Food Wastage Management System that efficiently connects surplus food providers (restaurants, individuals) with NGOs and individuals in need.

**Key Features:**  
- Providers can list surplus food availability.  
- Receivers (NGOs, individuals) can claim available food.  
- SQL database securely stores food details, locations, and provider info.  
- Streamlit app enables easy interaction with:  
  - Filtering options by city, provider, food and meal type.  
  - CRUD operations to manage listings and claims in real time.  
  - Visualization and reporting to analyze food wastage trends.

Together, this system aims to reduce food waste, support food justice initiatives, and improve accessibility to surplus food in local communities.
    """)

# --- 15 Queries Tab ---
with tab2:
    st.header("Project SQL Queries")
    queries = {
        "Providers and receivers count by city": """
            SELECT p.City, 
                   COUNT(DISTINCT p.Provider_ID) AS Providers, 
                   COUNT(DISTINCT r.Receiver_ID) AS Receivers
            FROM providers p
            LEFT JOIN receivers r ON p.City = r.City
            GROUP BY p.City;
        """,
        "Top food provider type by contributions": """
            SELECT Provider_Type, COUNT(Food_ID) AS Total_Contributions
            FROM food_listings
            GROUP BY Provider_Type
            ORDER BY Total_Contributions DESC;
        """,
        "Provider contact info by city": None,  # handled separately
        "Most frequent food receivers": """
            SELECT r.Name AS Receiver_Name, COUNT(c.Claim_ID) AS Total_Claims
            FROM claims c
            JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
            GROUP BY r.Name
            ORDER BY Total_Claims DESC;
        """,
        "Total food quantity available": """
            SELECT SUM(Quantity) AS Total_Quantity_Available
            FROM food_listings;
        """,
        "City with highest listings": """
            SELECT Location AS City, COUNT(Food_ID) AS Total_Listings
            FROM food_listings
            GROUP BY Location
            ORDER BY Total_Listings DESC
            LIMIT 1;
        """,
        "Most common food types": """
            SELECT Food_Type, COUNT(Food_ID) AS Count
            FROM food_listings
            GROUP BY Food_Type
            ORDER BY Count DESC;
        """,
        "Claims per food item": """
            SELECT f.Food_Name, COUNT(c.Claim_ID) AS Total_Claims
            FROM claims c
            JOIN food_listings f ON c.Food_ID = f.Food_ID
            GROUP BY f.Food_Name
            ORDER BY Total_Claims DESC;
        """,
        "Top provider by successful claims": """
            SELECT p.Name AS Provider_Name, COUNT(c.Claim_ID) AS Successful_Claims
            FROM claims c
            JOIN food_listings f ON c.Food_ID = f.Food_ID
            JOIN providers p ON f.Provider_ID = p.Provider_ID
            WHERE c.Status = 'Completed'
            GROUP BY p.Name
            ORDER BY Successful_Claims DESC
            LIMIT 1;
        """,
        "Claims status percentages": """
            SELECT Status,
                   COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims) AS Percentage
            FROM claims
            GROUP BY Status;
        """,
        "Avg quantity claimed per receiver": """
            SELECT r.Name AS Receiver_Name,
                   AVG(f.Quantity) AS Avg_Quantity_Claimed
            FROM claims c
            JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
            JOIN food_listings f ON c.Food_ID = f.Food_ID
            WHERE c.Status = 'Completed'
            GROUP BY r.Name
            ORDER BY Avg_Quantity_Claimed DESC;
        """,
        "Most claimed meal type": """
            SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims
            FROM claims c
            JOIN food_listings f ON c.Food_ID = f.Food_ID
            GROUP BY f.Meal_Type
            ORDER BY Total_Claims DESC;
        """,
        "Quantity donated per provider": """
            SELECT p.Name AS Provider_Name, SUM(f.Quantity) AS Total_Quantity_Donated
            FROM food_listings f
            JOIN providers p ON f.Provider_ID = p.Provider_ID
            GROUP BY p.Name
            ORDER BY Total_Quantity_Donated DESC;
        """,
        "Top demand locations": """
            SELECT f.Location AS City, COUNT(c.Claim_ID) AS Total_Claims
            FROM claims c
            JOIN food_listings f ON c.Food_ID = f.Food_ID
            GROUP BY f.Location
            ORDER BY Total_Claims DESC
            LIMIT 5;
        """,
        "Most wasted (unclaimed) food types": """
            SELECT f.Food_Type, COUNT(f.Food_ID) AS Unclaimed_Items
            FROM food_listings f
            LEFT JOIN claims c ON f.Food_ID = c.Food_ID
            WHERE c.Claim_ID IS NULL
            GROUP BY f.Food_Type
            ORDER BY Unclaimed_Items DESC;
        """
    }
    query_keys = list(queries.keys())
    selected_q = st.selectbox("Choose a query to run:", query_keys)
    if selected_q == "Provider contact info by city":
        cities = pd.read_sql("SELECT DISTINCT City FROM providers", engine)["City"].tolist()
        city = st.selectbox("Select a city:", cities)
        sql = f"SELECT Name, Contact FROM providers WHERE City = '{city}';"
        if st.button("Run Query"):
            result = pd.read_sql(sql, engine)
            st.dataframe(result)
    else:
        sql = queries[selected_q]
        if st.button("Run Query"):
            try:
                result = pd.read_sql(sql, engine)
                st.dataframe(result)
            except Exception as e:
                st.error(str(e))


# --- CRUD Operations Tab ---
with tab3:
    st.header("CRUD Operations")
    crud_tab = st.radio("Choose Table", ("Providers", "Receivers", "Food Listings", "Claims"))

    # Providers CRUD
    if crud_tab == "Providers":
        provider_df = pd.read_sql("SELECT * FROM providers", engine)
        st.dataframe(provider_df)
        action = st.radio("Action", ("Add", "Update", "Delete"))

        if action == "Add":
            with st.form("AddProv", clear_on_submit=True):
                name = st.text_input("Name")
                type_ = st.text_input("Type")
                address = st.text_input("Address")
                city = st.text_input("City")
                contact = st.text_input("Contact")
                submitted = st.form_submit_button("Add Provider")
                if submitted:
                    with engine.begin() as conn:
                        conn.execute(text(
                            "INSERT INTO providers (Name, Type, Address, City, Contact) "
                            "VALUES (:name, :type_, :address, :city, :contact)"),
                            {"name": name, "type_": type_, "address": address, "city": city, "contact": contact}
                        )
                    st.success("Provider added.")

        elif action == "Update":
            ids = provider_df["Provider_ID"].tolist()
            pid = st.selectbox("Provider_ID", ids)
            row = provider_df.set_index('Provider_ID').loc[pid]
            with st.form("UpdProv"):
                name = st.text_input("Name", value=row["Name"])
                type_ = st.text_input("Type", value=row["Type"])
                address = st.text_input("Address", value=row["Address"])
                city = st.text_input("City", value=row["City"])
                contact = st.text_input("Contact", value=row["Contact"])
                submitted = st.form_submit_button("Update Provider")
                if submitted:
                    with engine.begin() as conn:
                        conn.execute(
                            text("UPDATE providers SET Name=:name, Type=:type_, Address=:address, City=:city, Contact=:contact WHERE Provider_ID=:pid"),
                            {"pid": pid, "name": name, "type_": type_, "address": address, "city": city, "contact": contact}
                        )
                    st.success("Provider updated.")

        elif action == "Delete":
            ids = provider_df["Provider_ID"].tolist()
            pid = st.selectbox("Provider_ID", ids)
            if st.button("Delete Provider"):
                with engine.begin() as conn:
                    conn.execute(text("DELETE FROM providers WHERE Provider_ID=:pid"), {"pid": pid})
                st.success("Provider deleted.")

    # Receivers CRUD
    elif crud_tab == "Receivers":
        receiver_df = pd.read_sql("SELECT * FROM receivers", engine)
        st.dataframe(receiver_df)
        action = st.radio("Action", ("Add", "Update", "Delete"))

        if action == "Add":
            with st.form("AddRecv", clear_on_submit=True):
                name = st.text_input("Name")
                type_ = st.text_input("Type")
                city = st.text_input("City")
                contact = st.text_input("Contact")
                submitted = st.form_submit_button("Add Receiver")
                if submitted:
                    with engine.begin() as conn:
                        conn.execute(
                            text("INSERT INTO receivers (Name, Type, City, Contact) VALUES (:name,:type_,:city,:contact)"),
                            {"name": name, "type_": type_, "city": city, "contact": contact}
                        )
                    st.success("Receiver added.")

        elif action == "Update":
            ids = receiver_df["Receiver_ID"].tolist()
            rid = st.selectbox("Receiver_ID", ids)
            row = receiver_df.set_index('Receiver_ID').loc[rid]
            with st.form("UpdRecv"):
                name = st.text_input("Name", value=row["Name"])
                type_ = st.text_input("Type", value=row["Type"])
                city = st.text_input("City", value=row["City"])
                contact = st.text_input("Contact", value=row["Contact"])
                submitted = st.form_submit_button("Update Receiver")
                if submitted:
                    with engine.begin() as conn:
                        conn.execute(
                            text("UPDATE receivers SET Name=:name, Type=:type_, City=:city, Contact=:contact WHERE Receiver_ID=:rid"),
                            {"rid": rid, "name": name, "type_": type_, "city": city, "contact": contact}
                        )
                    st.success("Receiver updated.")

        elif action == "Delete":
            ids = receiver_df["Receiver_ID"].tolist()
            rid = st.selectbox("Receiver_ID", ids)
            if st.button("Delete Receiver"):
                with engine.begin() as conn:
                    conn.execute(text("DELETE FROM receivers WHERE Receiver_ID=:rid"), {"rid": rid})
                st.success("Receiver deleted.")

    # Food Listings CRUD
    elif crud_tab == "Food Listings":
        food_df = pd.read_sql("SELECT * FROM food_listings", engine)
        st.dataframe(food_df)
        action = st.radio("Action", ("Add", "Update", "Delete"))

        if action == "Add":
            with st.form("AddFood", clear_on_submit=True):
                name = st.text_input("Food Name")
                quantity = st.number_input("Quantity", min_value=1, step=1)
                expiry = st.date_input("Expiry Date")
                provider_id = st.number_input("Provider_ID", step=1)
                provider_type = st.text_input("Provider Type")
                location = st.text_input("City/Location")
                food_type = st.text_input("Food Type")
                meal_type = st.text_input("Meal Type")
                submitted = st.form_submit_button("Add Food")
                if submitted:
                    with engine.begin() as conn:
                        conn.execute(
                            text("""INSERT INTO food_listings 
                            (Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
                            VALUES (:name,:quantity,:expiry,:provider_id,:provider_type,:location,:food_type,:meal_type)"""),
                            {
                                "name": name, "quantity": quantity, "expiry": expiry,
                                "provider_id": provider_id, "provider_type": provider_type, "location": location,
                                "food_type": food_type, "meal_type": meal_type
                            }
                        )
                    st.success("Food listing added.")

        elif action == "Update":
            ids = food_df["Food_ID"].tolist()
            fid = st.selectbox("Food_ID", ids)
            row = food_df.set_index('Food_ID').loc[fid]
            with st.form("UpdFood"):
                name = st.text_input("Food Name", value=row["Food_Name"])
                quantity = st.number_input("Quantity", min_value=1, step=1, value=int(row["Quantity"]))
                expiry = st.date_input("Expiry Date", value=pd.to_datetime(row["Expiry_Date"]).date())
                provider_id = st.number_input("Provider_ID", step=1, value=int(row["Provider_ID"]))
                provider_type = st.text_input("Provider Type", value=row["Provider_Type"])
                location = st.text_input("City/Location", value=row["Location"])
                food_type = st.text_input("Food Type", value=row["Food_Type"])
                meal_type = st.text_input("Meal Type", value=row["Meal_Type"])
                submitted = st.form_submit_button("Update Food Listing")
                if submitted:
                    with engine.begin() as conn:
                        conn.execute(
                            text("""UPDATE food_listings 
                                SET Food_Name=:name, Quantity=:quantity, Expiry_Date=:expiry, 
                                Provider_ID=:provider_id, Provider_Type=:provider_type, Location=:location, 
                                Food_Type=:food_type, Meal_Type=:meal_type
                                WHERE Food_ID=:fid"""),
                            {
                                "fid": fid, "name": name, "quantity": quantity, "expiry": expiry,
                                "provider_id": provider_id, "provider_type": provider_type, "location": location,
                                "food_type": food_type, "meal_type": meal_type
                            }
                        )
                    st.success("Food listing updated.")

        elif action == "Delete":
            ids = food_df["Food_ID"].tolist()
            fid = st.selectbox("Food_ID", ids)
            if st.button("Delete Food Listing"):
                with engine.begin() as conn:
                    conn.execute(text("DELETE FROM food_listings WHERE Food_ID=:fid"), {"fid": fid})
                st.success("Food listing deleted.")

    # Claims CRUD
    elif crud_tab == "Claims":
        claims_df = pd.read_sql("SELECT * FROM claims", engine)
        st.dataframe(claims_df)
        action = st.radio("Action", ("Add", "Update", "Delete"))

        if action == "Add":
            with st.form("AddClaim", clear_on_submit=True):
                food_id = st.number_input("Food_ID", step=1)
                receiver_id = st.number_input("Receiver_ID", step=1)
                status = st.selectbox("Status", ("Pending", "Completed", "Cancelled"))
                timestamp = st.date_input("Timestamp")
                submitted = st.form_submit_button("Add Claim")
                if submitted:
                    with engine.begin() as conn:
                        conn.execute(
                            text("INSERT INTO claims (Food_ID, Receiver_ID, Status, Timestamp) VALUES (:food_id,:receiver_id,:status,:timestamp)"),
                            {
                                "food_id": food_id, "receiver_id": receiver_id,
                                "status": status, "timestamp": timestamp
                            }
                        )
                    st.success("Claim added.")

        elif action == "Update":
            ids = claims_df["Claim_ID"].tolist()
            cid = st.selectbox("Claim_ID", ids)
            row = claims_df.set_index('Claim_ID').loc[cid]
            with st.form("UpdClaim"):
                food_id = st.number_input("Food_ID", step=1, value=int(row["Food_ID"]))
                receiver_id = st.number_input("Receiver_ID", step=1, value=int(row["Receiver_ID"]))
                status = st.selectbox("Status", ("Pending", "Completed", "Cancelled"), index=["Pending", "Completed", "Cancelled"].index(row["Status"]))
                timestamp = st.date_input("Timestamp", value=pd.to_datetime(row["Timestamp"]).date())
                submitted = st.form_submit_button("Update Claim")
                if submitted:
                    with engine.begin() as conn:
                        conn.execute(
                            text("UPDATE claims SET Food_ID=:food_id, Receiver_ID=:receiver_id, Status=:status, Timestamp=:timestamp WHERE Claim_ID=:cid"),
                            {
                                "cid": cid, "food_id": food_id, "receiver_id": receiver_id,
                                "status": status, "timestamp": timestamp
                            }
                        )
                    st.success("Claim updated.")

        elif action == "Delete":
            ids = claims_df["Claim_ID"].tolist()
            cid = st.selectbox("Claim_ID", ids)
            if st.button("Delete Claim"):
                with engine.begin() as conn:
                    conn.execute(text("DELETE FROM claims WHERE Claim_ID=:cid"), {"cid": cid})
                st.success("Claim deleted.")


# --- Filter & Contact Tab ---
with tab4:
    st.header("Filter Food Donations and Contact Providers/Receivers")
    food_df = pd.read_sql("SELECT * FROM food_listings", engine)
    providers_df = pd.read_sql("SELECT * FROM providers", engine)
    receivers_df = pd.read_sql("SELECT * FROM receivers", engine)
    claims_df = pd.read_sql("SELECT * FROM claims", engine)

    locations = sorted(food_df["Location"].dropna().unique())
    provider_names = sorted(providers_df["Name"].dropna().unique())
    food_types = sorted(food_df["Food_Type"].dropna().unique())

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_loc = st.selectbox("Filter by Location (City):", ["All"] + locations)
    with col2:
        selected_provider = st.selectbox("Filter by Provider:", ["All"] + provider_names)
    with col3:
        selected_food_type = st.selectbox("Filter by Food Type:", ["All"] + food_types)

    filtered = food_df.copy()
    if selected_loc != "All":
        filtered = filtered[filtered["Location"] == selected_loc]
    if selected_provider != "All":
        pid = providers_df[providers_df["Name"] == selected_provider]["Provider_ID"].values
        if len(pid) > 0:
            filtered = filtered[filtered["Provider_ID"] == pid[0]]
    if selected_food_type != "All":
        filtered = filtered[filtered["Food_Type"] == selected_food_type]

    st.subheader("Filtered Food Donations")
    if filtered.empty:
        st.info("No records match your filter.")
    else:
        st.dataframe(filtered.reset_index(drop=True), use_container_width=True)

        st.markdown("#### Provider Contact Info")
        shown_provider_ids = set(filtered["Provider_ID"].unique())
        shown_providers = providers_df[providers_df["Provider_ID"].isin(shown_provider_ids)]
        for _, row in shown_providers.iterrows():
            st.write(f"**{row['Name']}** (Contact: `{row['Contact']}`)")

        st.markdown("#### Receivers Who Claimed Shown Food (if any)")
        filtered_food_ids = filtered["Food_ID"].unique()
        claims_filtered = claims_df[claims_df["Food_ID"].isin(filtered_food_ids)]
        shown_receiver_ids = claims_filtered["Receiver_ID"].unique()
        shown_receivers = receivers_df[receivers_df["Receiver_ID"].isin(shown_receiver_ids)]
        if shown_receivers.empty:
            st.info("No claims on shown food items yet.")
        else:
            for _, row in shown_receivers.iterrows():
                st.write(f"**{row['Name']}** (Contact: `{row['Contact']}`)")

    st.caption("Use the above to find food, and copy contact info to coordinate distribution directly!")
