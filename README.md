# Python for Data Analysis: From Basics to Interactive Dashboards

A hands-on workshop teaching Python data analysis using Lisbon road accidents data.

## 📚 Prerequisites

Before the class, complete the **Kaggle Python Course**:  
👉 https://www.kaggle.com/learn/python

## 🛠️ Setup

### Option 1: Google Colab (Recommended for class)
1. Open [Google Colab](https://colab.research.google.com)
2. Upload `Python_Data_Analysis_Lesson.ipynb`
3. Upload the dataset from `data/Road_Accidents_Lisbon.csv`

### Option 2: Local Installation (For Streamlit dashboard)
```bash
# Clone the repository
git clone https://github.com/tamagusko/lisbon-accidents-dashboard.git
cd lisbon-accidents-dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

## 📁 Repository Structure

```
lisbon-accidents-dashboard/
├── app.py                           # Streamlit dashboard
├── Python_Data_Analysis_Lesson.ipynb # Google Colab notebook
├── requirements.txt                 # Python dependencies
├── data/
│   └── Road_Accidents_Lisbon.csv    # Dataset
└── docs/
    ├── Tutorial_1_Google_Colab.pdf  # Colab quick start guide
    └── Tutorial_3_Streamlit_Setup.pdf # Local setup guide
```

## 📖 Topics Covered

1. Loading and exploring data (CSV/Excel)
2. Data cleaning and preparation
3. Statistical analysis (groupby, aggregations)
4. Data visualization (bar charts, pie charts, line plots)
5. Geospatial visualization with interactive maps
6. Building Streamlit dashboards

## 📊 Dataset

Lisbon road accidents data (2023) - for educational purposes only.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍🏫 Author

**Dr. Tiago Tamagusko**  
[tamagusko.com](https://tamagusko.com) · [tamagusko@gmail.com](mailto:tamagusko@gmail.com)
