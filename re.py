import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf
from docx import Document
import json

# Function to extract text from PDF
def extract_text_from_pdf(file):
    reader = pdf.PdfReader(file)
    text = ""
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()
    return text

# Function to extract text from DOCX
def extract_text_from_docx(file):
    doc = Document(file)
    return '\n'.join([paragraph.text for paragraph in doc.paragraphs])

# GenAI request function
def get_gemini_response(input_prompt, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input_prompt)
    return json.loads(response.text)  # Assuming the response is a JSON string

# Input prompt template for GenAI
input_prompt_template = """
Hey Act Like a skilled or very experienced ATS (Application Tracking System)
. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving the resumes. Assign the percentage Matching based 
on JD and
the missing keywords with high accuracy.
resume: {text}
description: {jd}
weights: {weights}
quantifiable_areas: {quantifiable_areas}

I want the response in one single string having the structure
{{"CandidateName": "", "OverallScore":"%", "ExperienceScore":"%", "AdditionalExperienceNeeded": "", "SkillsScore":"%", "AdditionalSkillsNeeded": "", "EducationMatch":"%", "AdditionalEducationNeeded": "", "CertificationMatch":"%", "AdditionalCertificationsNeeded": "", "QuantifiableResultsMatch":"%", "AreasNeedingImprovement": ""}}
"""

# Streamlit app
st.title("Resume and Job Description Matcher")

st.markdown("""

This tool helps recruiters and hiring managers quickly evaluate how well a candidate's CV matches a job description. Here's how to use it:

1. **Upload the Candidate's CV**: You can upload a PDF or Word document of the candidate's CV.
2. **Enter the Job Description**: Copy and paste the job description into the text area.
3. **Adjust Weights**: Use the sliders to set how important each factor is for the job. For example:
    - **Title Weight**: How important is it that the candidate's job title matches the job description?
    - **Experience Weight**: How crucial is the amount of relevant experience the candidate has?
    - **Skills Weight**: How important are specific skills listed in the job description?
    - **Education Weight**: How important is the candidate's educational background?
    - **Certifications Weight**: How significant are relevant certifications?
    - **Quantifiable Results Weight**: How important are quantifiable achievements or results (e.g., "grew followers by 30% in three months")?

    Each slider allows you to specify a percentage (0 to 100) indicating how much weight you want to give to that particular factor. The total should ideally sum up to 100%, but the tool will automatically adjust to give you a comprehensive match score.

4. **Specify Areas for Quantifiable Results**: Indicate where you expect the candidates to have quantifiable results on their CVs.
    - **Leadership**
    - **Revenue Generation / Reducing Cost**
    - **Saving Time**
    - **Collaboration**
    

5. **Get Results**: The tool will analyze the CV against the job description and provide a match score and detailed feedback.


Give it a try to see how well a candidate fits your job requirements!

""")

# Input field for API key
api_key = ''
if not api_key:
    st.warning("Please enter your API key to proceed.")

# Job description input
jd = st.text_area("Paste the Job Description")

# Resume file uploader
uploaded_file = st.file_uploader("Upload Your Resume", type=["pdf", "docx"], help="Please upload the PDF or DOCX file")

# Weights for different criteria
st.sidebar.header("Assign Weights (0-100)")
st.sidebar.write("""
Adjust the weights for different criteria according to your preference. 
The weights determine how much each criterion contributes to the overall matching score.

""")

weights = {
    "title": st.sidebar.slider("Job Title Weight", 0, 100, 20),
    "experience": st.sidebar.slider("Experience Weight", 0, 100, 20),
    "skills": st.sidebar.slider("Skills Weight", 0, 100, 20),
    "education": st.sidebar.slider("Education Weight", 0, 100, 20),
    "quantifiable_results": st.sidebar.slider("Quantifiable Results Weight", 0, 100, 20)
}

# Select areas for quantifiable results
st.sidebar.header("Select Areas for Quantifiable Results")
st.sidebar.write("""
Select areas where you expect candidates to provide quantifiable results. 
Quantifiable results should include numbers or percentages that provide context.
For example, "Led a team of 5" or "Increased revenue by 20%".
""")

quantifiable_areas = st.sidebar.multiselect(
    "Select areas where you expect the candidate to have quantifiable results",
    ["Leadership", "Cost Reduction", "Revenue Generation", "Time Saving", "Collaboration"]
)

# Submit button
if uploaded_file and api_key:
    submit = st.button("Submit")

    if submit:
        # Extract text from the uploaded file
        if uploaded_file.type == "application/pdf":
            text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = extract_text_from_docx(uploaded_file)

        # Create the input prompt
        input_prompt = input_prompt_template.format(
            text=text, 
            jd=jd, 
            weights=json.dumps(weights), 
            quantifiable_areas=json.dumps(quantifiable_areas)
        )

        # Get response from GenAI
        response = get_gemini_response(input_prompt, api_key)

        # Display results
        st.header(uploaded_file.name)
        st.write(f"**Candidate Name**: {response.get('CandidateName', 'N/A')}")
        st.write(f"**Overall Score**: {response.get('OverallScore', 'N/A')}")
        st.write(f"**Experience Score**: {response.get('ExperienceScore', 'N/A')}")
        if 'ExperienceScore' in response and float(response['ExperienceScore'].strip('%')) < 80:
            st.write(f"**Additional Experience Needed**: {response.get('AdditionalExperienceNeeded', 'N/A')}")
        st.write(f"**Skills Score**: {response.get('SkillsScore', 'N/A')}")
        if 'SkillsScore' in response and float(response['SkillsScore'].strip('%')) < 80:
            st.write(f"**Additional Skills Needed**: {response.get('AdditionalSkillsNeeded', 'N/A')}")
        st.write(f"**Education Match**: {response.get('EducationMatch', 'N/A')}")
        if 'EducationMatch' in response and float(response['EducationMatch'].strip('%')) < 80:
            st.write(f"**Additional Education Needed**: {response.get('AdditionalEducationNeeded', 'N/A')}")
        st.write(f"**Certification Match**: {response.get('CertificationMatch', 'N/A')}")
        if 'CertificationMatch' in response and float(response['CertificationMatch'].strip('%')) < 80:
            st.write(f"**Additional Certifications Needed**: {response.get('AdditionalCertificationsNeeded', 'N/A')}")
        st.write(f"**Quantifiable Results Match**: {response.get('QuantifiableResultsMatch', 'N/A')}")
        if 'QuantifiableResultsMatch' in response and float(response['QuantifiableResultsMatch'].strip('%')) < 80:
            st.write(f"**Areas Needing Improvement**: {response.get('AreasNeedingImprovement', 'N/A')}")
else:
    st.write("Please upload a PDF or DOCX file.")
