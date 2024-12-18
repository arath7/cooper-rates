import requests
import streamlit as st
from modules.nav import SideBarLinks

# Set up basic logging infrastructure
import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(page_title="Flag Reviews", layout="wide")
SideBarLinks()

# Fetch all reviews
response = requests.get('http://api:4000/r/review')
if response.status_code == 200:
    reviews = response.json()
else:
    st.error("Failed to fetch reviews")
    st.stop()

# Fetch all students
response = requests.get('http://api:4000/s/Student')
if response.status_code == 200:
    students = response.json()
else:
    st.error("Failed to fetch students")
    st.stop()

# Create a dictionary to map student NUID to student name
student_name_map = {student['NUID']: f"{student['firstName']} {student['lastName']}" for student in students}

# Search bar to filter reviews by student name
search_query = st.text_input("Search for Review by Student Name")

# Filter reviews based on search query
if search_query:
    filtered_reviews = [review for review in reviews if search_query.lower() in student_name_map.get(review['StudentNUID'], "").lower()]
else:
    filtered_reviews = reviews


# Display reviews
st.title("Student Reviews")
for review in filtered_reviews:
    student_info = { 
        'reviewer_info': f'http://api:4000/s/Student/{review["StudentNUID"]}',
        'job_info': f'http://api:4000/j/jobs/{review["JobID"]}',
        'company_info': f'http://api:4000/j/jobs/employer/{review["JobID"]}' 
        }
    student_json = {}
    for key, route in student_info.items():
        response = requests.get(route)
        if response.status_code == 200:
            student_json[key] = response.json()
        else:
            st.error(f"Failed to fetch student information from {route}")
            st.stop()

    fName = (student_json.get('reviewer_info', []))[0]['firstName']
    lName = (student_json.get('reviewer_info', []))[0]['lastName']
    employer = (student_json.get('company_info', []))[0]['Name']
    job_title = (student_json.get('job_info', []))[0]['Name']
    employer = (student_json.get('company_info', []))[0]['Name']
    st.write("Student Name: " + fName + " " + lName)
    st.write(f"NUID: {review['StudentNUID']}")
    st.write(f"Employer: {employer}")
    st.write(f"Job Title: {job_title}")
    st.write(f"Review: {review['textReview']}")
    
    
    # Form to flag a review
    with st.form(f"flag_review_form_{review['reviewID']}"):
        reason = st.text_input("Reason for flagging")
        submitted = st.form_submit_button("Flag Review")
        if submitted:
            flagged_review = {
                "ReviewID": review['reviewID'],
                # "adminID": adminID,
                "ReasonSubmitted": reason,

            }
            flag_response = requests.post('http://api:4000/fr/flagged_content', json=flagged_review)
            if flag_response.status_code == 200:
                st.success("Review flagged successfully")
            else:
                st.error("Failed to flag review")
                st.stop()