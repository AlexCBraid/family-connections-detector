from setuptools import setup, find_packages

setup(
    name="family_connections",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.0.0",
        "geopy>=2.0.0",
        "thefuzz>=0.19.0",
        "python-Levenshtein>=0.12.0"  # Optional but improves thefuzz performance
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A package for detecting family connections in corporate officer data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/family_connections",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
