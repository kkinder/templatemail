from distutils.core import setup

setup(
    name='templatemail',
    version='0.1',
    packages=['templatemail'],
    package_data={'templatemail': ['templates/mailgun-transactional/*.html']},
    url='https://github.com/kkinder/templatemail',
    license='Apache 2.0',
    author='Ken Kinder',
    author_email='ken@kkinder.com',
    description='Templated Email for Python',
    python_requires='>=3.6',
    install_requires=[
        'requests',
        'jinja2'
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
