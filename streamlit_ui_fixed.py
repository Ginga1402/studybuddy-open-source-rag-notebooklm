import streamlit as st
import requests
import json
import os
from typing import List
import base64
from pathlib import Path
from datetime import datetime

# API Configuration
API_BASE_URL = "http://localhost:9000"
DATA_DIRECTORY = "studybuddy/Data"

# Page Configuration
st.set_page_config(
    page_title="📚 StudyBuddy – An Open Source Alternative to Google’s NotebookLM",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .success-message {
        color: #28a745;
        font-weight: bold;
    }
    .error-message {
        color: #dc3545;
        font-weight: bold;
    }
    
    /* Enhanced Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        padding: 8px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0px 20px;
        background-color: white;
        border-radius: 8px;
        color: #495057;
        font-weight: 600;
        font-size: 14px;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #007bff !important;
        color: white !important;
        border-color: #0056b3;
        box-shadow: 0 2px 8px rgba(0,123,255,0.3);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e9ecef;
        border-color: #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/heartbeat", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_api_metrics():
    """Get API usage metrics"""
    try:
        response = requests.get(f"{API_BASE_URL}/metrics", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def save_uploaded_files(uploaded_files):
    """Save uploaded files to Data directory"""
    saved_files = []
    try:
        os.makedirs(DATA_DIRECTORY, exist_ok=True)
        for uploaded_file in uploaded_files:
            file_path = os.path.join(DATA_DIRECTORY, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_files.append(uploaded_file.name)
        return saved_files, None
    except Exception as e:
        return [], str(e)

def create_vectorstore(filenames: List[str], vectorstore_name: str):
    """Create vector store from PDF files"""
    try:
        payload = {
            "filenames": filenames,
            "vectorstore_name": vectorstore_name
        }
        response = requests.post(f"{API_BASE_URL}/create-vectorstore/", json=payload, timeout=300)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_pdf_download_link(pdf_path: str, filename: str):
    """Generate download link for PDF file"""
    try:
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
        b64_pdf = base64.b64encode(pdf_data).decode()
        return f'<a href="data:application/pdf;base64,{b64_pdf}" download="{filename}" target="_blank">📄 View/Download {filename}</a>'
    except:
        return f"📄 {filename} (file not accessible)"

def create_download_button(content: str, filename: str, content_type: str = "Summary"):
    """Create download button for text content"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_filename = f"{filename}_{timestamp}.txt"
    
    # Add header to content
    header = f"StudyBuddy {content_type}\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{'='*50}\n\n"
    full_content = header + content
    
    # Create download button
    st.download_button(
        label=f"💾 Download {content_type}",
        data=full_content,
        file_name=full_filename,
        mime="text/plain",
        type="secondary",
        help=f"Download {content_type.lower()} as a text file with timestamp"
    )

def generate_content(endpoint: str, payload: dict):
    """Generic function to call content generation endpoints"""
    try:
        response = requests.post(f"{API_BASE_URL}/{endpoint}/", json=payload, timeout=120)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def render_home_page():
    """Render the home/landing page"""
    st.markdown('<h1 class="main-header">📚 StudyBuddy – Open Source RAG-Based AI Notebook and Google NotebookLM Alternative</h1>', unsafe_allow_html=True)
    
    # Project Overview
    st.markdown("""
    <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; color: white; margin-bottom: 2rem;'>
        <h2 style='color: white; margin-bottom: 1rem;'>🧠 Summarize PDFs, ask questions from research papers, auto-generate notes, and turn your documents into an interactive AI workspace.</h2>
        <p style='font-size: 1.1rem; margin-bottom: 0;'>StudyBuddy is a free, open source alternative to Google NotebookLM that lets you chat with your documents, generate smart summaries, and organize knowledge with AI—all securely on your terms.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Cards
    st.subheader("🚀 Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='feature-card'>
            <h4>📁 Vector Store Creation</h4>
            <p>Upload multiple PDFs and create searchable knowledge bases using advanced embeddings.</p>
        </div>
        
        <div class='feature-card'>
            <h4>🧠 Quiz Generation</h4>
            <p>Generate multiple-choice quizzes with customizable difficulty and question count.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='feature-card'>
            <h4>❓ Intelligent Q&A Assistant</h4>
            <p>Ask questions about your study materials and get accurate answers with source references.</p>
        </div>
        
        <div class='feature-card'>
            <h4>❔ FAQ Creation</h4>
            <p>Generate frequently asked questions to help structure your learning process.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='feature-card'>
            <h4>📝 Smart Summaries</h4>
            <p>Create student-friendly summaries with key concepts, formulas, and important points.</p>
        </div>
        
        <div class='feature-card'>
            <h4>📊 Visual Diagrams</h4>
            <p>Generate ASCII flowcharts and diagrams to visualize complex concepts.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Additional Features
    st.markdown("""
    <div class='feature-card'>
        <h4>🏷️ Topic Extraction</h4>
        <p>Automatically discover and organize important topics from your study materials using AI-powered analysis.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # User Guide
    st.subheader("📖 Quick Start Guide")
    
    with st.expander("🚀 How to Get Started", expanded=False):
        st.markdown("""
        ### Step 1: Create a Vector Store
        1. Go to the **Create Vector Store** tab
        2. Upload your PDF files using the file uploader
        3. Give your vector store a memorable name
        4. Click "Create Vector Store" and wait for processing
        
        ### Step 2: Generate Study Materials
        1. Choose any feature tab (Summary, Quiz, FAQ, etc.)
        2. Enter your subject/topic of interest
        3. Use the same vector store name you created
        4. Generate and download your study materials
        
        ### Step 3: Interactive Learning
        - Use **Intelligent Q&A Assistant** for specific questions
        - Generate **Quizzes** to test your knowledge
        - Create **Summaries** for quick review
        - Use **Diagrams** for visual learning
        """)
    
    with st.expander("💡 Pro Tips", expanded=False):
        st.markdown("""
        - **Organize by Subject**: Create separate vector stores for different subjects
        - **Descriptive Names**: Use clear vector store names like "physics_mechanics" or "biology_cells"
        - **Download Everything**: Save generated content as text files for offline study
        - **Ask Specific Questions**: More specific questions yield better answers in Q&A
        - **Combine Features**: Use summaries first, then generate quizzes to test understanding
        """)

def render_analytics_page():
    """Render the analytics/metrics page"""
    st.header("📊 Analytics Dashboard")
    
    # API Status Header
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if check_api_health():
            st.success("🟢 API Status: Online & Healthy")
        else:
            st.error("🔴 API Status: Offline or Unreachable")
    
    with col2:
        if st.button("🔄 Refresh Metrics", type="secondary"):
            st.rerun()
    
    with col3:
        auto_refresh = st.checkbox("🔄 Auto-refresh", help="Refresh every 30 seconds")
        if auto_refresh:
            import time
            time.sleep(30)
            st.rerun()
    
    st.divider()
    
    # API Metrics
    metrics = get_api_metrics()
    if metrics:
        # System Overview
        st.subheader("📊 System Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "⏱️ Uptime", 
                metrics.get('uptime', 'N/A'),
                help="Total time the API has been running"
            )
        
        with col2:
            total_requests = sum(metrics.get('request_counts', {}).values())
            st.metric(
                "📈 Total Requests", 
                f"{total_requests:,}",
                help="Total number of API requests processed"
            )
        
        with col3:
            active_routes = len(metrics.get('request_counts', {}))
            st.metric(
                "🔍 Active Routes", 
                active_routes,
                help="Number of API endpoints that have been accessed"
            )
        
        with col4:
            uptime_seconds = metrics.get('uptime_seconds', 0)
            if uptime_seconds > 0:
                requests_per_hour = round((total_requests / uptime_seconds) * 3600, 2)
                st.metric(
                    "⚡ Requests/Hour", 
                    f"{requests_per_hour}",
                    help="Average requests per hour"
                )
            else:
                st.metric("⚡ Requests/Hour", "0")
        
        st.divider()
        
        # Feature Usage Analysis
        st.subheader("📈 Feature Usage Analysis")
        request_counts = metrics.get('request_counts', {})
        
        if request_counts:
            # Create two columns for charts and details
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Bar chart data
                import pandas as pd
                
                # Clean route names for better display
                clean_routes = {}
                route_mapping = {
                    '/create-vectorstore/': '📁 Vector Store',
                    '/QA-Guide/': '❓ Intelligent Q&A Assistant',
                    '/generate-summary/': '📝 Summary',
                    '/generate-diagram/': '📊 Diagram',
                    '/generate-quiz/': '🧠 Quiz',
                    '/generate-FAQ/': '❔ FAQ',
                    '/generate-important-topics/': '🏷️ Topics',
                    '/heartbeat': '💗 Health Check',
                    '/metrics': '📊 Metrics'
                }
                
                for route, count in request_counts.items():
                    clean_name = route_mapping.get(route, route)
                    clean_routes[clean_name] = count
                
                # Create DataFrame for chart
                df = pd.DataFrame(list(clean_routes.items()), columns=['Feature', 'Requests'])
                df = df.sort_values('Requests', ascending=True)
                
                # Display bar chart
                st.bar_chart(df.set_index('Feature'))
            
            with col2:
                st.markdown("**📉 Usage Statistics**")
                
                # Sort by usage
                sorted_routes = sorted(clean_routes.items(), key=lambda x: x[1], reverse=True)
                
                for i, (feature, count) in enumerate(sorted_routes[:5]):
                    percentage = (count / total_requests) * 100 if total_requests > 0 else 0
                    st.markdown(f"**{i+1}. {feature}**")
                    st.progress(percentage / 100)
                    st.markdown(f"   {count} requests ({percentage:.1f}%)")
                    st.markdown("")
        
        st.divider()
        
        # Detailed Route Information
        st.subheader("🔍 Detailed Route Information")
        
        if request_counts:
            # Create expandable sections for each route
            for route, count in sorted(request_counts.items(), key=lambda x: x[1], reverse=True):
                clean_name = route_mapping.get(route, route)
                
                with st.expander(f"{clean_name} - {count} requests"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Requests", count)
                    
                    with col2:
                        percentage = (count / total_requests) * 100 if total_requests > 0 else 0
                        st.metric("Usage %", f"{percentage:.1f}%")
                    
                    with col3:
                        if uptime_seconds > 0:
                            avg_per_hour = round((count / uptime_seconds) * 3600, 2)
                            st.metric("Avg/Hour", f"{avg_per_hour}")
                        else:
                            st.metric("Avg/Hour", "0")
                    
                    # Route description
                    descriptions = {
                        '/create-vectorstore/': 'Creates searchable knowledge bases from PDF documents',
                        '/QA-Guide/': 'Provides answers to questions using RAG technology',
                        '/generate-summary/': 'Creates student-friendly summaries of topics',
                        '/generate-diagram/': 'Generates ASCII diagrams and flowcharts',
                        '/generate-quiz/': 'Creates multiple-choice quizzes for testing',
                        '/generate-FAQ/': 'Generates frequently asked questions',
                        '/generate-important-topics/': 'Extracts key topics using LDA analysis',
                        '/heartbeat': 'Health check endpoint for monitoring',
                        '/metrics': 'Provides system metrics and usage statistics'
                    }
                    
                    description = descriptions.get(route, 'API endpoint')
                    st.info(f"📝 {description}")
        
        else:
            st.info("📊 No request data available yet. Start using the features to see analytics!")
    
    else:
        st.warning("⚠️ Unable to fetch API metrics. Please ensure the FastAPI server is running on localhost:9000")
        
        # Show connection troubleshooting
        with st.expander("🔧 Troubleshooting"):
            st.markdown("""
            **Common Issues:**
            1. 🔴 FastAPI server not running - Start with `python FastAPI.py`
            2. 🔴 Wrong port - Ensure API is running on port 9000
            3. 🔴 Network issues - Check firewall settings
            4. 🔴 API overloaded - Wait a moment and refresh
            """)

# Main App
def main():
    # Initialize session state
    if 'vectorstore_name' not in st.session_state:
        st.session_state.vectorstore_name = ""
    if 'subject' not in st.session_state:
        st.session_state.subject = ""
    
    # API Status Check (silent)
    api_status = check_api_health()
    
    # Tab Navigation
    tabs = st.tabs([
        "🏠 Home",
        "📁 Create Vector Store", 
        "❓ Intelligent Q&A Assistant",
        "📝 Generate Summary",
        "📊 Create Diagram",
        "🧠 Generate Quiz",
        "❔ Create FAQ",
        "🏷️ Extract Topics",
        "📊 Analytics"
    ])
    
    # Home Tab
    with tabs[0]:
        render_home_page()
        
        # API Status on Home
        st.divider()
        if api_status:
            st.success("🟢 API is running successfully!")
        else:
            st.error("🔴 API is not running. Please start the FastAPI server on localhost:9000")
    
    # Analytics Tab
    with tabs[8]:
        render_analytics_page()
    
    # Create Vector Store Tab
    with tabs[1]:
        st.header("📁 Create Vector Store from PDFs")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📋 Upload PDF Files")
            uploaded_files = st.file_uploader(
                "Choose PDF files:",
                type="pdf",
                accept_multiple_files=True,
                help="Upload multiple PDF files to create your vector store"
            )
            
            vectorstore_name = st.text_input(
                "Vector Store Name:",
                value=st.session_state.vectorstore_name,
                placeholder="my_study_materials",
                help="This name will be remembered across tabs",
                key="vectorstore_create"
            )
            # Update session state
            if vectorstore_name:
                st.session_state.vectorstore_name = vectorstore_name
            
            if uploaded_files:
                st.write(f"📄 Selected files: {len(uploaded_files)}")
                for file in uploaded_files:
                    st.write(f"  • {file.name}")
        
        with col2:
            st.subheader("ℹ️ Instructions")
            st.info("""
            1. Upload PDF files using the file uploader
            2. Files will be saved to the Data directory
            3. Choose a unique vector store name
            4. Click 'Create Vector Store'
            """)
        
        if st.button("🚀 Create Vector Store", type="primary"):
            if uploaded_files and vectorstore_name:
                with st.spinner("Saving files and creating vector store... This may take a few minutes."):
                    # Save uploaded files
                    saved_files, save_error = save_uploaded_files(uploaded_files)
                    
                    if save_error:
                        st.error(f"❌ Error saving files: {save_error}")
                    else:
                        st.success(f"✅ Saved {len(saved_files)} files to Data directory")
                        
                        # Create vector store
                        result = create_vectorstore(saved_files, vectorstore_name)
                        
                        if "error" in result:
                            st.error(f"❌ Error creating vector store: {result['error']}")
                        else:
                            st.success(f"✅ {result.get('status', 'Success')}")
                            st.info(f"📁 Vector store created: {vectorstore_name}")
            else:
                st.warning("⚠️ Please upload PDF files and provide a vector store name.")
    
    # Q&A Assistant Tab
    with tabs[2]:
        if not api_status:
            st.error("🔴 API is not running. Please start the FastAPI server first.")
            st.stop()
        st.header("❓ Intelligent Q&A Assistant")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            question = st.text_area(
                "Ask your question:",
                placeholder="What are the characteristics of sound waves?",
                height=100,
                key="question_qa"
            )
            
            vectorstore_name = st.text_input(
                "Vector Store Name:",
                value=st.session_state.vectorstore_name,
                placeholder="physics_textbook",
                help="Edit to use a different vector store or keep the current one",
                key="vectorstore_qa"
            )
            # Update session state
            if vectorstore_name:
                st.session_state.vectorstore_name = vectorstore_name
        
        with col2:
            st.subheader("💡 Tips")
            st.info("""
            • Ask specific questions about your study material
            • Use the same vector store name you created
            • Questions can be conceptual or factual
            """)
        
        if st.button("🔍 Get Answer", type="primary"):
            if question and vectorstore_name:
                with st.spinner("Searching for answer..."):
                    result = generate_content("QA-Guide", {
                        "question": question,
                        "vectorstore_name": vectorstore_name
                    })
                
                if "error" in result:
                    st.error(f"❌ Error: {result['error']}")
                else:
                    st.success("✅ Answer Generated!")
                    st.subheader("📝 Answer:")
                    st.write(result.get("answer", "No answer generated"))
                    st.subheader("📄 Source Document:")
                    source_path = result.get("source", "")
                    if source_path and os.path.exists(source_path):
                        filename = os.path.basename(source_path)
                        download_link = get_pdf_download_link(source_path, filename)
                        st.markdown(download_link, unsafe_allow_html=True)
                    else:
                        st.write("Source document not available")
            else:
                st.warning("⚠️ Please provide both question and vector store name.")
    
    # Generate Summary Tab
    with tabs[3]:
        if not api_status:
            st.error("🔴 API is not running. Please start the FastAPI server first.")
            st.stop()
        st.header("📝 Generate Summary")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            subject = st.text_input(
                "Subject/Topic:",
                value=st.session_state.subject,
                placeholder="Thrust and Pressure",
                help="This subject will be remembered across tabs",
                key="subject_summary"
            )
            # Update session state
            if subject:
                st.session_state.subject = subject
            
            vectorstore_name = st.text_input(
                "Vector Store Name:",
                value=st.session_state.vectorstore_name,
                placeholder="physics_textbook",
                help="Edit to use a different vector store or keep the current one",
                key="vectorstore_summary"
            )
            # Update session state
            if vectorstore_name:
                st.session_state.vectorstore_name = vectorstore_name
        
        with col2:
            st.subheader("📚 About Summaries")
            st.info("""
            • Student-friendly explanations
            • Key concepts and principles
            • Important formulas
            • Bullet-point format
            """)
        
        if st.button("📄 Generate Summary", type="primary"):
            if subject and vectorstore_name:
                with st.spinner("Generating summary..."):
                    result = generate_content("generate-summary", {
                        "subject": subject,
                        "vectorstore_name": vectorstore_name
                    })
                
                if "error" in result:
                    st.error(f"❌ Error: {result['error']}")
                else:
                    st.success("✅ Summary Generated!")
                    summary_content = result.get("summary", "No summary generated")
                    st.subheader(f"📝 Summary: {subject}")
                    st.markdown(summary_content)
                    
                    # Download button
                    create_download_button(summary_content, f"summary_{subject.replace(' ', '_')}", "Summary")
            else:
                st.warning("⚠️ Please provide both subject and vector store name.")
    
    # Create Diagram Tab
    with tabs[4]:
        if not api_status:
            st.error("🔴 API is not running. Please start the FastAPI server first.")
            st.stop()
        st.header("📊 Create ASCII Diagram")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            subject = st.text_input(
                "Subject/Topic:",
                value=st.session_state.subject,
                placeholder="Thrust and Pressure",
                help="This subject will be remembered across tabs",
                key="subject_diagram"
            )
            # Update session state
            if subject:
                st.session_state.subject = subject
            
            vectorstore_name = st.text_input(
                "Vector Store Name:",
                value=st.session_state.vectorstore_name,
                placeholder="physics_textbook",
                help="Edit to use a different vector store or keep the current one",
                key="vectorstore_diagram"
            )
            # Update session state
            if vectorstore_name:
                st.session_state.vectorstore_name = vectorstore_name
        
        with col2:
            st.subheader("🎨 About Diagrams")
            st.info("""
            • ASCII flowcharts
            • Visual concept representation
            • Hierarchical organization
            • Easy to understand format
            """)
        
        if st.button("🎨 Create Diagram", type="primary"):
            if subject and vectorstore_name:
                with st.spinner("Creating diagram..."):
                    result = generate_content("generate-diagram", {
                        "subject": subject,
                        "vectorstore_name": vectorstore_name
                    })
                
                if "error" in result:
                    st.error(f"❌ Error: {result['error']}")
                else:
                    st.success("✅ Diagram Created!")
                    diagram_content = result.get("diagram", "No diagram generated")
                    st.subheader(f"📊 Diagram: {subject}")
                    st.code(diagram_content, language="text")
                    
                    # Download button
                    create_download_button(diagram_content, f"diagram_{subject.replace(' ', '_')}", "Diagram")
            else:
                st.warning("⚠️ Please provide both subject and vector store name.")
    
    # Generate Quiz Tab
    with tabs[5]:
        if not api_status:
            st.error("🔴 API is not running. Please start the FastAPI server first.")
            st.stop()
        st.header("🧠 Generate Quiz")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            subject = st.text_input(
                "Subject/Topic:",
                value=st.session_state.subject,
                placeholder="Thrust and Pressure",
                help="This subject will be remembered across tabs",
                key="subject_quiz"
            )
            # Update session state
            if subject:
                st.session_state.subject = subject
            
            vectorstore_name = st.text_input(
                "Vector Store Name:",
                value=st.session_state.vectorstore_name,
                placeholder="physics_textbook",
                help="Edit to use a different vector store or keep the current one",
                key="vectorstore_quiz"
            )
            # Update session state
            if vectorstore_name:
                st.session_state.vectorstore_name = vectorstore_name
            
            num_questions = st.slider(
                "Number of Questions:",
                min_value=1,
                max_value=20,
                value=5
            )
        
        with col2:
            st.subheader("🎯 Quiz Features")
            st.info("""
            • Multiple-choice questions
            • 4 options per question
            • Academic-level difficulty
            • Answer key included
            """)
        
        if st.button("🧠 Generate Quiz", type="primary"):
            if subject and vectorstore_name:
                with st.spinner("Generating quiz..."):
                    result = generate_content("generate-quiz", {
                        "subject": subject,
                        "vectorstore_name": vectorstore_name,
                        "num_questions": num_questions
                    })
                
                if "error" in result:
                    st.error(f"❌ Error: {result['error']}")
                else:
                    st.success("✅ Quiz Generated!")
                    st.subheader(f"🧠 Quiz: {subject} ({num_questions} questions)")
                    
                    # Format quiz for better presentation
                    quiz_content = result.get("quiz", "No quiz generated")
                    
                    # Split quiz into questions and answers sections
                    if "Answers:" in quiz_content:
                        questions_part, answers_part = quiz_content.split("Answers:", 1)
                    else:
                        questions_part = quiz_content
                        answers_part = ""
                    
                    # Format questions
                    import re
                    questions = re.split(r'\n(?=\d+\.)', questions_part)
                    
                    for question_block in questions:
                        if question_block.strip():
                            lines = question_block.strip().split('\n')
                            if lines:
                                # Question number and text
                                st.markdown(f"**{lines[0]}**")
                                
                                # Options
                                for line in lines[1:]:
                                    if line.strip() and (line.strip().startswith('A.') or 
                                                        line.strip().startswith('B.') or 
                                                        line.strip().startswith('C.') or 
                                                        line.strip().startswith('D.')):
                                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{line.strip()}")
                                    elif line.strip():
                                        st.markdown(line.strip())
                                
                                st.markdown("")
                    
                    # Display answers if available
                    if answers_part.strip():
                        st.subheader("📋 Answer Key:")
                        st.markdown(f"**Answers:**\n{answers_part.strip()}")
                    
                    # Download button
                    create_download_button(quiz_content, f"quiz_{subject.replace(' ', '_')}", "Quiz")
            else:
                st.warning("⚠️ Please provide both subject and vector store name.")
    
    # Create FAQ Tab
    with tabs[6]:
        if not api_status:
            st.error("🔴 API is not running. Please start the FastAPI server first.")
            st.stop()
        st.header("❔ Create FAQ")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            subject = st.text_input(
                "Subject/Topic:",
                value=st.session_state.subject,
                placeholder="Thrust and Pressure",
                help="This subject will be remembered across tabs",
                key="subject_faq"
            )
            # Update session state
            if subject:
                st.session_state.subject = subject
            
            vectorstore_name = st.text_input(
                "Vector Store Name:",
                value=st.session_state.vectorstore_name,
                placeholder="physics_textbook",
                help="Edit to use a different vector store or keep the current one",
                key="vectorstore_faq"
            )
            # Update session state
            if vectorstore_name:
                st.session_state.vectorstore_name = vectorstore_name
            
            num_questions = st.slider(
                "Number of FAQs:",
                min_value=1,
                max_value=15,
                value=5
            )
        
        with col2:
            st.subheader("❔ FAQ Benefits")
            st.info("""
            • Common student questions
            • Structured Q&A format
            • Learning-focused content
            • Study guide material
            """)
        
        if st.button("❔ Generate FAQ", type="primary"):
            if subject and vectorstore_name:
                with st.spinner("Generating FAQ..."):
                    result = generate_content("generate-FAQ", {
                        "subject": subject,
                        "vector_store_name": vectorstore_name,
                        "num_questions": num_questions
                    })
                
                if "error" in result:
                    st.error(f"❌ Error: {result['error']}")
                else:
                    st.success("✅ FAQ Generated!")
                    st.subheader(f"❔ FAQ: {subject}")
                    
                    # Format FAQ for better presentation
                    faq_content = result.get("faq", "No FAQ generated")
                    
                    # Split by numbered questions and format
                    import re
                    questions = re.split(r'\n(?=\d+\.)', faq_content)
                    
                    for i, question_block in enumerate(questions):
                        if question_block.strip():
                            # Split Q and A
                            if '**A:**' in question_block:
                                parts = question_block.split('**A:**')
                                if len(parts) == 2:
                                    question_part = parts[0].strip()
                                    answer_part = parts[1].strip()
                                    
                                    # Display question
                                    st.markdown(f"**{question_part}**")
                                    # Display answer with indentation
                                    st.markdown(f"**Answer:** {answer_part}")
                                    st.markdown("---")
                                else:
                                    st.markdown(question_block)
                            else:
                                st.markdown(question_block)
                    
                    # Download button
                    create_download_button(faq_content, f"faq_{subject.replace(' ', '_')}", "FAQ")
            else:
                st.warning("⚠️ Please provide both subject and vector store name.")
    
    # Extract Topics Tab
    with tabs[7]:
        if not api_status:
            st.error("🔴 API is not running. Please start the FastAPI server first.")
            st.stop()
        st.header("🏷️ Extract Important Topics")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            vectorstore_name = st.text_input(
                "Vector Store Name:",
                value=st.session_state.vectorstore_name,
                placeholder="physics_textbook",
                help="Edit to use a different vector store or keep the current one",
                key="vectorstore_topics"
            )
            # Update session state
            if vectorstore_name:
                st.session_state.vectorstore_name = vectorstore_name
        
        with col2:
            st.subheader("🏷️ Topic Extraction")
            st.info("""
            • AI-powered topic discovery
            • LDA algorithm analysis
            • Topic names with subthemes
            • Content organization
            """)
        
        if st.button("🏷️ Extract Topics", type="primary"):
            if vectorstore_name:
                with st.spinner("Extracting topics... This may take a moment."):
                    result = generate_content("generate-important-topics", {
                        "vectorstore_name": vectorstore_name
                    })
                
                if "error" in result:
                    st.error(f"❌ Error: {result['error']}")
                else:
                    st.success("✅ Topics Extracted!")
                    topics_content = result.get("topics_description", "No topics generated")
                    st.subheader(f"🏷️ Important Topics from: {vectorstore_name}")
                    st.markdown(topics_content)
                    
                    # Download button
                    create_download_button(topics_content, f"topics_{vectorstore_name}", "Topics")
            else:
                st.warning("⚠️ Please provide vector store name.")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; margin-top: 2rem;'>
        <p>📚 StudyBuddy - AI-Powered Learning Assistant | Built with Streamlit & FastAPI</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
