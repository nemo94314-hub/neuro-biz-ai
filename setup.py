from setuptools import setup, find_packages

setup(
    name="llm-business-tuner",
    version="0.1.0",
    author="Your Name",
    description="Локальная утилита для дообучения LLM на бизнес-интервью",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.36.0",
        "peft>=0.7.0",
        "trl>=0.7.0",
        "bitsandbytes>=0.41.0",
        "datasets>=2.14.0",
        "accelerate>=0.25.0",
        "click>=8.1.0",
    ],
    entry_points={
        "console_scripts": [
            "llm-tuner=llm_tuner.cli:cli",
        ],
    },
    python_requires=">=3.9",
)
