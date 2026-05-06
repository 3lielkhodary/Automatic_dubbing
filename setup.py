from setuptools import setup, find_packages

setup(
    name="video-dubber",
    version="1.0.0",
    description="Automatically dub videos into other languages, mimicking original voice characteristics.",
    author="Your Name",
    python_requires=">=3.9",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "SpeechRecognition>=3.10.0",
        "deep-translator>=1.11.0",
        "gTTS>=2.3.0",
        "pydub>=0.25.1",
    ],
    entry_points={
        "console_scripts": [
            "video-dubber=dubber.cli:main",
        ],
    },
)
