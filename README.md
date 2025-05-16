# SchoolHub – AI-Driven School Management Platform

## Overview
SchoolHub is an AI-enhanced school management platform that unifies academic, health, social, and economic data for real-time monitoring of student performance. The system is designed to help educators and administrators identify students who may need additional support early on, by providing a holistic view of each student’s situation. Traditional school management systems usually focus only on grades and attendance, neglecting critical psychosocial factors. SchoolHub addresses this gap by integrating diverse data sources and employing machine learning to generate actionable insights.

## Features
- **Holistic Student Profiles**  
  Combines academic records (grades, attendance) with health, socioeconomic, and behavioral data to form a comprehensive profile for each student.
- **Early Warning Alerts**  
  Uses an AI model to predict students “at risk” of underperformance. Teachers and counselors get alerted early about students who might need intervention.
- **Analytics Dashboard**  
  Provides descriptive analytics (charts and tables) for class or school-level trends. For example, visualize how factors like attendance or stress levels correlate with performance.
- **Data Management**  
  Allows secure storage and management of student data, including personal info, academic history, and any counseling or health notes, in a centralized database.
- **User Roles**  
  - **Admins:** manage all data, users, and system settings.  
  - **Teachers:** view and update their students’ data and see AI-predicted indicators for their class.  
  - **Counselors / Advisors:** access relevant student profiles and analytics to provide targeted support.
- **Privacy & Security**  
  Adopts data privacy best practices. Sensitive data (health, psychology) is protected and only accessible to authorized personnel. A dedicated discussion of ethical and privacy considerations is included in the project documentation.

## System Architecture
**Figure 1: High-Level System Architecture of SchoolHub.**

At a high level, SchoolHub follows a client-server architecture built on the Django web framework:

- **Backend (Django)**  
  The core server-side logic is implemented in Django (Python). It contains multiple Django apps:  
  - **students** and **teachers**: manage student and teacher records (models, views, CRUD forms).  
  - **accounts**: handles user authentication and authorization (login, permissions).  
  - **predictor**: encapsulates the AI components—loads the ML model and exposes prediction logic via Django views or management commands.  
  - **reports** (optional): generates analytical reports and dashboards.

- **Frontend**  
  Uses Django templates and static files for the web interface. The UI is basic but functional, allowing users to navigate student lists, view profiles, and see visualizations. It includes:  
  - HTML templates (e.g., student profile, analytics dashboard).  
  - CSS and JavaScript for styling/interactivity (where applicable).  
  - The Django Admin interface is leveraged for quick data viewing and management.

- **Database**  
  PostgreSQL (or SQLite for testing) stores all persistent data. This includes student info, teacher info, and any logs of model predictions or alerts. Django’s ORM is used to interact with the database, and migrations are provided.

- **Machine Learning Model**  
  A pre-trained Decision Tree model (`student_performance_model.pkl`) is stored on the server. When a student’s data is added or updated, the model can be used to predict an outcome (e.g., “Needs Improvement” or “On Track”). Prediction logic may be triggered on demand (e.g., via a button on the student profile page or a background job).

- **External Integration** (Optional)  
  Supports integration with external sources (CSV imports, IoT health devices), though in this project data is generated synthetically for demonstration.

## Data and AI Methodology
- **Synthetic Data Generation**  
  In the absence of real student datasets (privacy/availability concerns), we created a synthetic dataset of 5,000 records. A custom Python script (`generator.ipynb`) generates realistic data—including academic performance, attendance, stress levels, parental involvement, etc.—based on researched distributions. (All code is available in the [SchoolHub_Codes](https://github.com/Hawraa92/SchoolHub_Codes) repository.)

- **Data Cleaning & Preparation**  
  - Standardized date formats and categorical entries (e.g., unified “None” or missing values).  
  - Ensured no critical missing values; used placeholders like “Not Specified” where needed.  
  - Split data into training and testing sets for model evaluation.

- **Model Training**  
  Trained a Decision Tree classifier on the synthetic dataset to predict student performance outcomes. The Decision Tree was chosen for its interpretability. We also experimented with an XGBoost model for comparison (`XGBoost_Predictive_Analysis.ipynb`).

- **Model Performance**  
  The Decision Tree model achieved over **99% accuracy** on the synthetic test set, with similarly high precision and recall. (High performance is due to simplified patterns in synthetic data; real-world accuracy may be lower. Complexity controls like max depth were applied to avoid overfitting.)

- **Insights from Data Analysis**  
  Students predicted to “Need Improvement” tended to have higher stress levels and lower motivation scores. Consistent attendance strongly correlated with better academic performance. These patterns were uncovered via cross-tabulation and comparative plots.

- **Ethical Considerations**  
  No sensitive personal identifiers were used. We discussed fairness and bias mitigation, ensuring the synthetic data was balanced and diverse.

## Installation and Setup
To set up SchoolHub locally:

1. **Clone the repository**  
   ```bash
   git clone https://github.com/Hawraa92/SchoolHub-Project.git
   cd SchoolHub-Project
