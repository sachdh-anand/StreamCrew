from setuptools import setup, find_packages

setup(
    name="keynotegenie",
    version="0.1.0",
    description="An AI-powered research and keynote speech generator",
    author="KeynoteGenie Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "mistralai>=1.5.1",
        "openai>=1.0.0",
        "python-dotenv>=1.0.1",
        "colorama>=0.4.6",
        "requests>=2.31.0",
        "crewai>=0.16.0",
        "crewai-tools>=0.0.15",
        "streamlit>=1.31.0",
        "pathlib>=1.0.1",
    ],
    python_requires=">=3.8",
) 