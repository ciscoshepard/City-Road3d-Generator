from setuptools import setup, find_packages

setup(
    name="city-road3d-generator",
    version="1.0.0",
    description="3D city road network generator with variable density zones",
    author="CiscoShepard",
    packages=find_packages(),
    install_requires=[
        "Flask>=3.0.0",
        "numpy>=1.24.3",
        "Pillow>=10.0.1",
        "matplotlib>=3.7.2",
        "noise>=1.2.2",
        "scipy>=1.11.3"
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "city-generator=city_generator.main:main",
        ],
    },
)