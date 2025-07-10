from setuptools import setup

setup(
    name="cryptoweather",
    version="1.0.0",
    description="MCP server for CryptoWeather Bitcoin price prediction AI",
    author="CryptoWeather Team",
    author_email="info@cryptoweather.xyz",
    url="https://github.com/2051project/cryptoweather",
    py_modules=["main"],
    install_requires=[
        "fastmcp>=0.1.0",
        "requests>=2.28.0",
    ],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "cryptoweather=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords=keywords = ["mcp", "bitcoin", "cryptocurrency", "ai", "prediction", "trading", "robo-advisor", "agent", "quant", "chart", "technical"],
)