from distutils.core import setup
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='templatemail',
    version='0.1.7',
    packages=['templatemail'],
    package_data={'templatemail': ['templates/*.html', 'templates/mailgun-transactional/*.html']},
    data_files=['README.md'],
    url='https://github.com/kkinder/templatemail',
    license='Apache 2.0',
    author='Ken Kinder',
    author_email='ken@kkinder.com',
    description='Templated Email for Python',
    python_requires='>=3.6',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'requests',
        'Jinja2'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Communications :: Email',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
