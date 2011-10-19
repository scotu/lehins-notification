from setuptools import setup, find_packages

setup(
    name='incuna-notification',
    version=__import__('notification').__version__,
    description='User notification management for the Django web framework',
    long_description=open('docs/usage.txt').read(),
    author='James Tauber, Incuna',
    author_email='info@incuna.com',
    url='https://github.com/incuna/incuna-notification',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
)
