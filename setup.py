from setuptools import setup, find_packages


setup(
    name='tadataka',
    description='VITAMIN-E',
    url='http://github.com/IshitaTakeshi/VITAMIN-E',
    author='Takeshi Ishita',
    author_email='ishitah.takeshi@gmail.com',
    license='MIT',
    packages=['tadataka'],
    install_requires=[
        'autograd',
        'bidict',
        'Cython',
        # TODO make independent from opencv
        'matplotlib',
        'numpy',
        'opencv-python',
        'opencv-contrib-python',
        'scikit-image',
        'scikit-learn',
        'scipy',
        'sympy',
        'sparseba'
    ]
)
