from setuptools import setup

setup(
    name='guaraguao',
    version='0.1.0',    
    description='A python package to download and cache satellite images',
    url='',
    author='Andres Ramos',
    author_email='ramosandres443@gmail.com',
    license='BSD 2-clause',
    packages=['guaraguao'],
    install_requires=[
                      'numpy',                     
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
    ],
)
