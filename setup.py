from pathlib import Path
from setuptools import setup, find_packages

ROOT = Path(__file__).parent
long_description = (ROOT / "README.md").read_text(encoding="utf-8")

setup(
    name="st-datatables",
    version="0.0.1",
    author="junmae",
    description="Streamlit custom component: DataTables (React) wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/junmae/streamlit-datatables",
    license="MIT",
    packages=find_packages(exclude=("examples", "tests", "e2e")),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.7",
    install_requires=[
        "streamlit >= 0.63",
    ],
    extras_require={
        "devel": [
            "wheel",
            "pytest==7.4.0",
            "playwright==1.48.0",
            "requests==2.31.0",
            "pytest-playwright-snapshot==1.0",
            "pytest-rerunfailures==12.0",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Framework :: Streamlit",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries",
    ],
    keywords=["streamlit", "component", "datatable", "react"],
    project_urls={
        "Source": "https://github.com/junmae/streamlit-datatables",
        "Issues": "https://github.com/junmae/streamlit-datatables/issues",
    },
)
