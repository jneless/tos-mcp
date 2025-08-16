from setuptools import setup, find_packages

setup(
    name="tos-mcp",
    version="1.0.0",
    description="TOS (火山引擎对象存储) MCP Server",
    author="TOS MCP Team",
    packages=find_packages(),
    install_requires=[
        "tos>=2.6.0",
        "mcp>=0.3.0"
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "tos-mcp=tos_mcp_server:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)