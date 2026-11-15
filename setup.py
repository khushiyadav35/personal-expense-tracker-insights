from setuptools import setup, find_packages

setup(
    name="personal-expense-tracker-insights",
    version="1.0.0",
    description="Personal Expense Tracker with ML Transaction Categorization, Overspending Alerts & Spending Forecast",
    author="Khushi Yadav",
    author_email="ky19tech@gmail.com",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0",
        "streamlit>=1.30.0",
        "plotly>=5.18.0",
        "joblib>=1.3.0",
        "python-dateutil>=2.8.2",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
