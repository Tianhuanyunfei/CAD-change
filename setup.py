from setuptools import setup, find_packages

setup(
    name="cad-change",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask",
        "ezdxf",
        # 其他依赖项...
    ],
    entry_points={
        "console_scripts": [
            "cad-change-web = design.app:main",
        ],
    },
)
