from setuptools import find_packages, setup

package_name = 'so101_tools'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Yovan Hirales',
    maintainer_email='yovanhirales@gmail.com',
    description='Helper nodes and test scripts for the SO-101 arm',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'mirror = so101_tools.mirror:main',
        ],
    },
)
