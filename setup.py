from setuptools import setup


setup(
    name='cldfbench_nominalperson_cldf',
    py_modules=['cldfbench_nominalperson_cldf'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'cldfbench.dataset': [
            'nominalperson_cldf=cldfbench_nominalperson_cldf:Dataset',
        ]
    },
    install_requires=[
        'cldfbench',
        'cldfzenodo',
        'pyglottolog',
    ],
    extras_require={
        'test': [
            'pytest-cldf',
        ],
    },
)
