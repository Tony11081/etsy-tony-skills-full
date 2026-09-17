from setuptools import find_namespace_packages, setup


setup(
    name="cli-anything-erank",
    version="0.3.0",
    description="CLI-Anything harness for eRank-like Etsy SEO research workflows.",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    install_requires=[
        "click>=8.0",
        "requests>=2.28",
        "Pillow>=10.0",
    ],
    entry_points={
        "console_scripts": [
            "cli-anything-erank=cli_anything.erank.erank_cli:cli",
        ]
    },
    python_requires=">=3.10",
)
