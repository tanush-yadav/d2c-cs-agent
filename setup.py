"""
Setup script for D2C CS Agent
"""

from setuptools import setup, find_packages

setup(
    name="d2c_cs_agent",
    version="0.1.0",
    description="A customer service agent system for D2C e-commerce brands using Google ADK with Shopify integration",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=["google-adk"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
)
