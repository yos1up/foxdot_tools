from setuptools import setup

setup(
    name="foxdot_tools",
    version="0.0.1",
    install_requires=["packageA", "packageB"],
    extras_require={
        "develop": ["dev-packageA", "dev-packageB"]
    },
    entry_points={
        "console_scripts": [
            "foo = package_name.module_name:func_name",
            "foo_dev = package_name.module_name:func_name [develop]"
        ],
        "gui_scripts": [
            "bar = gui_package_name.gui_module_name:gui_func_name"
        ]
    }
)
