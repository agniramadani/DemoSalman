import streamlit as st
import tempfile
import requests
import datetime
import zipfile
import os

# Public On Purpose
ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJkVTNTYXFLOHF1c25rakl4WEFsbE1EZk0zakRLYkJneDd3dlVVMHBsaUhFIn0.eyJleHAiOjE3MzM5MzAxODMsImlhdCI6MTczMzkyNjU4MywianRpIjoiNDBjMTNkNzctYWFiYy00OTY0LWI1OGQtNzlmOTU5NTBjZTY4IiwiaXNzIjoiaHR0cHM6Ly9hdXRoLmJleGlvLmNvbS9yZWFsbXMvYmV4aW8iLCJzdWIiOiI3OTg1NmY3ZC1lMzdmLTQ4ZDItYTU4ZC1lZDNlOWU3YjdmN2IiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJhMGU1MDc2Ny1jOGM1LTRhYjMtODUwMi04NDY4YTUzN2FhOTIiLCJzaWQiOiJkYjA2NzcyMC02OTQwLTQyYWUtYTA5Yy0wNWJiOGY1MjFmMTIiLCJzY29wZSI6ImZpbGUgY29udGFjdF9zaG93IiwibG9naW5faWQiOiI3OTg1NmY3ZC1lMzdmLTQ4ZDItYTU4ZC1lZDNlOWU3YjdmN2IiLCJjb21wYW55X2lkIjoiNnJ5Z21xYnJocGJuIiwidXNlcl9pZCI6NDM5NTUwLCJjb21wYW55X3VzZXJfaWQiOjR9.PPpfJ_1pAbtdnxOwNef-CNo7xwI0Nj3No61UnIearQ8XBYcUs5NsxOQqOg6cZdw8K5Mp-ZBp-ypplfNkyWy5DJR7HsuY4wqRYJBthPHS9B-pG77zJj_XfQa-EkKIQzSvQJbQC35MO-HA-a-kRyc-Jm7ipBy-rAyGq-KWCRsOPD2SbGvVzPIeHeK4bHrPm92aqvRQs-c1c8YOI_GNlJ_RffB-zXqHyIVeR5_UYhVJMVgLCFMdRPpKq1VsLIoSVbLHTfN6Vk1ACbrcd8jyfgvIdFmJN4LvQiU0TV-9dMygJp_N64lXLLx31u5UMrRwmng5_B9jLH55SKyt00xnoTxbmg"

def fetch_and_save_files(temp_dir):
    """
    Fetch all archived files and save them to a temporary directory.
    """
    files_endpoint = "https://api.bexio.com/3.0/files"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json"
    }
    params = {
        "archived_state": "archived"  # Options: all, archived, not_archived
    }

    response = requests.get(files_endpoint, headers=headers, params=params)

    if response.status_code == 200:
        files = response.json()

        if not files:
            return None, "No archived files found."

        for file in files:
            file_id = file.get("id")
            if not file_id:
                continue  # Skip files without a valid ID
            
            # Fetch the file data
            file_download_endpoint = f"https://api.bexio.com/3.0/files/{file_id}/download"
            file_response = requests.get(file_download_endpoint, headers=headers, stream=True)

            if file_response.status_code == 200:
                # Extract filename from headers or assign a default
                filename = file_response.headers.get("Content-Disposition", f"file_{file_id}.pdf")
                if "filename=" in filename:
                    filename = filename.split("filename=")[-1].strip('"')

                # Save the file to the temporary directory
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, "wb") as f:
                    f.write(file_response.content)
            else:
                st.warning(f"Failed to download file with ID {file_id}. Skipping.")

        return temp_dir, None
    else:
        return None, response.text

def create_zip_from_directory(temp_dir, zip_file_path):
    """
    Create a zip archive from a temporary directory.
    """
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, temp_dir))

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

# Add a "Download All Archives" button
if st.button("Prepare All Archives (Download)"):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir, error = fetch_and_save_files(temp_dir)

        if temp_dir:
            zip_file_path = os.path.join(tempfile.gettempdir(), "all_archived_files.zip")
            create_zip_from_directory(temp_dir, zip_file_path)

            # Provide the zip file for download
            with open(zip_file_path, "rb") as zipf:
                st.download_button(
                    label="Download Archive",
                    data=zipf,
                    file_name="all_archived_files.zip",
                    mime="application/zip"
                )
            
            # Cleanup: Zip file will be automatically removed since it’s in the temp directory
        elif error:
            st.error(f"Error fetching files: {error}")

st.write("Company list:")

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
        if st.button(f"{company_name}"):
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
