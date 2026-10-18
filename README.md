# 💸 SpendWise — Smart Expense Tracker

![Django](https://img.shields.io/badge/Django-5.0-darkgreen?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-orange?style=for-the-badge&logo=scikit-learn)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?style=for-the-badge&logo=bootstrap)
![PWA](https://img.shields.io/badge/PWA-Ready-success?style=for-the-badge)

**SpendWise** is a feature-rich, AI-powered personal finance management system built with Django. It goes beyond basic expense tracking by utilizing Machine Learning for category prediction, offering AI-driven financial insights, and functioning as an installable Progressive Web App (PWA).

Developed as a 2nd Mini Project for the **Cybernaut Edtech Internship** by **Abi Angelin**.

---

## ✨ Key Features

### 🧠 AI & Machine Learning
*   **Hybrid Category Prediction:** Uses a Naive Bayes classifier (scikit-learn) trained on the user's own data, with a regex-based keyword fallback (100% uptime).
*   **Smart Insights:** Generates personalized financial advice (e.g., "Spending Spike Detected", "Monthly Projection") based on spending patterns.
*   **Money Personality Analyzer:** Classifies users into 5 personalities (e.g., Impulse Buyer, Smart Saver) with customized tips.

### 💰 Core Finance Management
*   **Expense CRUD:** Add, edit, and delete expenses with receipt image uploads.
*   **Dashboard & Visuals:** Interactive Chart.js line & doughnut charts, plus a GitHub-style 91-day spending heatmap.
*   **Budgeting & Goals:** Monthly budget progress rings and savings goals with automated per-day target calculations.
*   **Multi-Currency Support:** Log expenses in 8 currencies with automatic INR normalization.
*   **Recurring Expenses:** Track subscriptions, rent, and EMIs with auto-expense creation on payment.

### 🤝 Collaboration & Sharing
*   **Split Expenses:** Splitwise-style bill sharing with settlement tracking.
*   **Family/Groups:** Create shared expense groups with role-based memberships and contribution charts.

### 🚀 Modern Web Features
*   **Progressive Web App (PWA):** Installable on mobile/desktop with offline static caching via Service Workers.
*   **Voice Input:** Log expenses using the Web Speech API.
*   **Dark/Light Mode:** Automatic system preference detection with manual toggle override.
*   **Export Data:** Generate CSV, PDF (ReportLab), and styled Excel (openpyxl) reports.
*   **SMS Alerts:** Budget warnings at 80% and 100% via Twilio (with console fallback for development).

---

## 🛠️ Tech Stack

*   **Backend:** Django 5.x, Python 3.11+
*   **Database:** SQLite (Development)
*   **ML:** scikit-learn, joblib
*   **Frontend:** HTML5, CSS3, JavaScript (ES6), Bootstrap 5, Chart.js
*   **Exports:** ReportLab, openpyxl
*   **APIs:** Web Speech API, Twilio (SMS)

---

## ⚙️ Installation & Setup

Follow these steps to run SpendWise locally:

**1. Clone the repository**
```bash
git clone https://github.com/Angel5326/smart-expense-tracker.git
cd smart-expense-tracker

2. Create and activate a virtual environment

bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
3. Install dependencies

bash
pip install -r requirements.txt
4. Apply database migrations

bash
python manage.py makemigrations
python manage.py migrate
5. Create a superuser (Admin)

bash
python manage.py createsuperuser
6. Run the development server

bash
python manage.py runserver
7. Access the application
Open your browser and go to http://127.0.0.1:8000/

📸 Screenshots
Login	Dashboard
https://./screenshots/Login.png	https://./screenshots/Dashboard.png
Dashboard (Analytics)	Add Expense
https://./screenshots/Dashboard-1.png	https://./screenshots/Add-Expenses.png
All Expenses	Group Tracking
https://./screenshots/All_Expenses.png	https://./screenshots/Group.png
Monthly Budget	Recurring Expenses
https://./screenshots/Monthly-Budget.png	https://./screenshots/Recurring-Expenses.png
Savings Goals	Split Detail
https://./screenshots/Saving-Goals.png	https://./screenshots/Split-Detail.png
📂 Project Structure
text
smart_expense_tracker/
│
├── smart_expense_tracker/   # Main Django configuration
├── expenses/                # Main application
│   ├── models.py            # 11 Models (Expense, Budget, Goal, Group, etc.)
│   ├── views.py             # 30+ View logic
│   ├── ml_predictor.py      # Machine Learning pipeline
│   ├── sms_utils.py         # Twilio Integration
│   └── utils.py             # AI Insights & Heatmap logic
├── templates/               # 25+ HTML Templates
├── static/                  # CSS, JS, PWA Manifest, Service Worker
└── requirements.txt         # Project dependencies
🚀 Future Enhancements
Bank SMS parsing to auto-create expenses.

Receipt OCR using Tesseract for auto-filling details.

Migration to PostgreSQL and Docker for production deployment.

REST API integration with a React Native mobile app.

👩‍💻 Author
Abi Angelin
B.E. Computer Science and Engineering
Developed during the Cybernaut Edtech Internship (2026-2027)