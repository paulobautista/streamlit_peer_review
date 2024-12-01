import streamlit as st
import os
from database_utils import get_mysql_connection, get_document_by_review_index, get_total_review_documents, insert_peer_review_action

st.set_page_config(layout="wide")

# Database connection
if 'db_connection' not in st.session_state:
    st.session_state.db_connection = get_mysql_connection()

# Initialize review index
if "review_index" not in st.session_state:
    st.session_state.review_index = 1

def get_document():
    """Get document with original markdown and latest edit"""
    return get_document_by_review_index(st.session_state.db_connection, st.session_state.review_index)

def navigate(direction):
    total_docs = get_total_review_documents()
    if direction == "next":
        st.session_state.review_index = (st.session_state.review_index % total_docs) + 1
    else:  # previous
        st.session_state.review_index = ((st.session_state.review_index - 2) % total_docs) + 1

# Navigation UI
nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])

with nav_col1:
    if st.button("⬅️ Back"):
        navigate("prev")
        st.rerun()

with nav_col2:
    col_left, col_middle, col_right = st.columns([1, 1, 1])
    with col_middle:
        new_index = st.number_input(
            "Review Index:",
            min_value=1,
            value=st.session_state.review_index
        )
        if new_index != st.session_state.review_index:
            st.session_state.review_index = new_index
            st.rerun()

with nav_col3:
    if st.button("Next ➡️"):
        navigate("next")
        st.rerun()

# Reviewer information
st.text_input("Reviewer Name:", key="reviewer_name", placeholder="Enter your name")

# Team agreement question
st.markdown("### Question")
st.markdown("Would people on your team agree that this is the correct way to annotate this image?")

# Get current document before handling responses
current_doc = get_document()

# Response buttons
response_col1, response_col2 = st.columns([1, 1])
with response_col1:
    yes_clicked = st.button("✅ Yes")
with response_col2:
    no_clicked = st.button("❌ No")

# Comments section
comments = st.text_area("Comments:", key="review_comments", placeholder="Enter your comments here...")

# Handle responses
if (yes_clicked or no_clicked) and current_doc:
    reviewer_name = st.session_state.get('reviewer_name', '').strip()
    if not reviewer_name:
        st.error("Please enter your name before submitting a review.")
    else:
        result = True if yes_clicked else False
        if insert_peer_review_action(
            st.session_state.db_connection,
            current_doc['id'],
            reviewer_name,
            result,
            comments
        ):
            st.success("Review submitted successfully!")
            # Move to next document
            navigate("next")
            st.rerun()
        else:
            st.error("Failed to submit review. Please try again.")

# Add some spacing
st.markdown("---")

# Main content display
if current_doc:
    # Replace toggle with radio buttons
    col_select1, col_select2 = st.columns([1, 1])

    with col_select1:
        left_content = st.radio(
            "Left Column Content:",
            ["Latest Edit", "Original Markdown"],
            key="left_radio"
        )

    with col_select2:
        right_content = st.radio(
            "Right Column Content:",
            ["Image", "Latest Edit", "Original Markdown"],
            key="right_radio"
        )

    # Display in two columns
    col1, col2 = st.columns([1, 1])

    # Left column content
    with col1:
        if left_content == "Original Markdown":
            st.markdown("### Original Markdown")
            st.markdown(current_doc['markdown'], unsafe_allow_html=True)
        else:
            st.markdown("### Latest Edit")
            st.markdown(current_doc.get('latest_edit') or 'No approved edits available', unsafe_allow_html=True)

    # Right column content
    with col2:
        if right_content == "Image":
            st.markdown("### Image")
            image_path = current_doc['image_path']
            try:
                if image_path:
                    s3_base_url = "https://streamlit-images.s3.ap-southeast-1.amazonaws.com/"
                    image_url = s3_base_url + current_doc['image_path']
                    image = st.image(image_url, caption=f"Document {current_doc['review_index']}")
                else:
                    st.warning(f"Image not found at path: {image_path}")
            except Exception as e:
                st.error(f"Error loading image: {str(e)}")
        elif right_content == "Original Markdown":
            st.markdown("### Original Markdown")
            st.markdown(current_doc['markdown'], unsafe_allow_html=True)
        else:  # Latest Edit
            st.markdown("### Latest Edit")
            st.markdown(current_doc.get('latest_edit') or 'No approved edits available', unsafe_allow_html=True)
else:
    st.error("No document found")
