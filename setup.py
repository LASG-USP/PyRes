from setuptools import setup, find_packages

setup(
    name="PyRes",
    version="0.1.0",
    packages=find_packages(),
    # Project metadata
    author="Leonardo Fonseca Reginato",
    author_email="leonardofonseca.r@gmail.com",
    description="Description of your project",
    long_description="Long description of your project",
    url="https://github.com/yourusername/yourproject",
    # Dependencies
    install_requires=[
       'numpy',
       'pandas',
       'matplotlib'
       'scikit-learn'
       'ypstruct'
       'PyYAML',
    ],
    # Entry points
    entry_points={
        "console_scripts": [
            "your_script_name = your_package.module:main_function",
        ],
    },
    # Other configurations
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        # Add more classifiers as needed
    ],
    keywords="reservoir simulation, cmg, optimization, npv, machine learning",
    license="MIT",
    # Additional project URLs
    project_urls={
        "Source": "https://github.com/yourusername/yourproject",
        "Bug Reports": "https://github.com/yourusername/yourproject/issues",
    },
)
