import streamlit as st
import requests
import datetime

# Public On Purpose
ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJkVTNTYXFLOHF1c25rakl4WEFsbE1EZk0zakRLYkJneDd3dlVVMHBsaUhFIn0.eyJleHAiOjE3MzM3ODcyNDYsImlhdCI6MTczMzc4MzY0NiwianRpIjoiMDU0NDViOGItZWU1MS00MzgxLTg1MjMtNzA0YzgwMWJjM2E0IiwiaXNzIjoiaHR0cHM6Ly9hdXRoLmJleGlvLmNvbS9yZWFsbXMvYmV4aW8iLCJzdWIiOiI3OTg1NmY3ZC1lMzdmLTQ4ZDItYTU4ZC1lZDNlOWU3YjdmN2IiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJhMGU1MDc2Ny1jOGM1LTRhYjMtODUwMi04NDY4YTUzN2FhOTIiLCJzaWQiOiI0MDRhMmJkOC1mZDRiLTQ0NTAtOGE5Yy00NGUyMjkxNmU4ZWMiLCJzY29wZSI6ImZpbGUgY29udGFjdF9zaG93IiwibG9naW5faWQiOiI3OTg1NmY3ZC1lMzdmLTQ4ZDItYTU4ZC1lZDNlOWU3YjdmN2IiLCJjb21wYW55X2lkIjoiNnJ5Z21xYnJocGJuIiwidXNlcl9pZCI6NDM5NTUwLCJjb21wYW55X3VzZXJfaWQiOjR9.P0hrK-HN-FQUweObnzL-319KwT2oYsat6kNq04C6fanNIVQMmBumjZswvQ6yiCxIFHdwhpXFvGDMZntFlRQ3Krd-KlcHUQyPqjP7GI8KAWTeiP1VK2Y0bxRPcnmFM_cT4VOgOW9Ja5M9Ll7fLuiZYMFL8ZDgCaMAncAu9WAkrNlC39nZ1qazBZi3iaGafShZ2EvQCc1u9xbKtYsIwTbUWSbpcnwheuaKCbRmBGLGaRlYtNa7g_JxTacN1Idn2h6BwzV2gQEPHZc7tYtp3OwVWyGcO64HpDwWQHMjXqWzkT6nKWCn24doo0-hMfIeiK7y8h4VuwlA7q68i9oEYMKG0w"

# Function to fetch companies
def fetch_companies():
    """
    Fetch a list of companies from Bexio.
    """
    companies_endpoint = "https://api.bexio.com/2.0/contact"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json"
    }
    
    response = requests.get(companies_endpoint, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch companies: {response.text}")
        return []

# Function to fetch files associated with a company
def fetch_files_by_company(contact_id):
    """
    Fetch files from Bexio associated with a specific company.
    """
    files_endpoint = f"https://api.bexio.com/3.0/files"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json"
    }
    params = {
        "contact_id": contact_id
    }
    response = requests.get(files_endpoint, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch files for contact {contact_id}: {response.text}")
        return []

# Streamlit UI
st.title("Salman")

# Inputs for search and filter
search_name = st.text_input("Search by Company Name")
current_year = datetime.datetime.now().year  # Get the current year
filter_year = st.number_input("Filter by Year (if available)", min_value=1900, max_value=2100, value=current_year)

st.write("Fetching list of companies from Bexio...")

# Fetch and display companies
companies = fetch_companies()

if companies:
    # Apply filters
    filtered_companies = [
        company for company in companies
        if (search_name.lower() in company.get('name_1', '').lower())
        and (str(filter_year) in company.get('updated_at', ''))  # Adjust 'updated_at' for year
    ]
    
    st.write(f"Found {len(filtered_companies)} companies matching the filters:")
    for company in filtered_companies:
        company_name = company.get('name_1', 'Kein Name')
        contact_id = company.get('id', None)  # Use contact ID for fetching files
        if st.button(f"View Files for {company_name}"):
            if contact_id:
                st.write(f"Fetching files for company: **{company_name}**")
                files = fetch_files_by_company(contact_id)
                if files:
                    st.write(f"Found {len(files)} files for **{company_name}**:")
                    for file in files:
                        file_name = file.get('name', 'Unnamed File')
                        file_size = file.get('size', 'Unknown Size')
                        created_at = file.get('created_at', 'No Date')
                        st.write(f"- **{file_name}** (Size: {file_size}, Created At: {created_at})")
                else:
                    st.write(f"No files found for company: **{company_name}**")
            else:
                st.write(f"No contact ID found for company: **{company_name}**")
else:
    st.write("No companies found or failed to fetch.")
