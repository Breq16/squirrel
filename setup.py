import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="squirrel-lps",
    version="0.0.1",
    author="Wesley Chalmers",
    author_email="breq@breq.dev",
    description="Local positioning system for ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Breq16/squirrel",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.6',
    install_requires=[
        "flask"
    ],
)
