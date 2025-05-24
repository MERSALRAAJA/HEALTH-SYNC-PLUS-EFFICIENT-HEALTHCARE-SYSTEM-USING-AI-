from setuptools import setup, find_packages

setup(
    name='medical_assistant',  # Changed to match your project name
    version='1.0', 
    packages=find_packages(),
    install_requires=[  # Fixed typo here
        'tk',  # tkinter is usually installed as 'tk'
        'pillow'
    ],
    entry_points={
        'console_scripts': [
            'medical_assistant = main:main'  # Changed to match your main entry point
        ]
    },
)