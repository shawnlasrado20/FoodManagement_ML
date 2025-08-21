# Local Food Wastage Management System

This repository contains the complete project code and resources for the **Local Food Wastage Management System**, a comprehensive solution aimed at reducing food waste and alleviating food insecurity through technology-enabled redistribution.

---

## Project Overview

Food wastage is a major global and local challenge, affecting economies, the environment, and social welfare. Every day, a huge amount of edible food is discarded by households, restaurants, and grocery stores, while many individuals face food insecurity.

The core issue is inefficient redistribution of surplus food—food that could benefit others goes to waste. This project develops a platform that connects food providers (restaurants, grocery stores, individuals) with people and organizations in need, ensuring surplus food finds new purpose.

---

## Key Features

- **Data Management:** Uses a MySQL database to store detailed information about providers, receivers, food listings, and claims.
- **Interactive UI:** Built with Streamlit, allowing:
  - Filtering food donations by location, provider, and food type.
  - Real-time CRUD operations to add, update, or remove data.
  - Execution of 15 insightful SQL queries for analytics.
- **Contact Access:** Displays contact details of providers and receivers to facilitate coordination.
- **Analytics:** Enables data-driven insights on food wastage trends, donation volumes, and demand hotspots.

---

## Dataset Description

- **Providers:** Contains donors like restaurants, grocery stores, supermarkets (ID, name, type, address, city, contact).
- **Receivers:** Contains recipients such as NGOs, community centers, individuals (ID, name, type, city, contact).
- **Food Listings:** Records available food items with details like quantity, expiry, location, type.
- **Claims:** Tracks who claimed which food item, its status, and timestamps.

---

## Technologies Used

- Python
- Streamlit
- MySQL
- SQLAlchemy
- Pandas
- PyMySQL

---

## Setup Instructions

1. Clone this repository:
```bash
git clone <repository-url>
cd <repository-folder>
```


text

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```


text

3. Set up MySQL database:
- Create database `Foodwaste`.
- Import datasets into tables `providers`, `receivers`, `food_listings`, and `claims`.

4. Update the database connection string in `app.py` with your credentials.

5. Run the Streamlit app:
streamlit run app.py

text

6. Open the browser at `http://localhost:8501` to access the dashboard.

---

## Usage

- Navigate tabs to explore features:
- **Introduction:** Project overview.
- **Queries:** Run predefined SQL analytics queries.
- **CRUD:** Manage providers, receivers, food listings, and claims.
- **Filter & Contact:** Find food donations with relevant contact info.

- Use CRUD functions to keep your database updated.

- Use Filters to search available food and connect with providers or claimants.

---

## Learnings & Insights

This project enhanced my skills in:

- Data cleaning and database design.
- Complex SQL querying for data insights.
- Building responsive web apps using Streamlit.
- Addressing social issues with technology.
- Understanding food redistribution logistics and community impact.

*Thank you for your interest in the Local Food Wastage Management System.*  
Together, let's reduce waste and promote food justice.
