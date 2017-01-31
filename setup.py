from setuptools import setup, find_packages

setup(
    name="django-template-multiprocessing",
    description="Use all your CPU cores to render templates.",
    long_description = open("README.rst", "r").read() + open("AUTHORS.rst", "r").read() + open("CHANGELOG.rst", "r").read(),
    version="0.1",
    author="Praekelt Consulting",
    author_email="dev@praekelt.com",
    license="BSD",
    url="http://github.com/praekelt/django-template-multiprocessing",
    packages = find_packages(),
    dependency_links = [
    ],
    install_requires = [
        "django>=1.9",
    ],
    tests_require = [
        "tox"
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    zip_safe=False,
)
