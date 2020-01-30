# import sys
# from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
# build_exe_options = {"packages": ["os", "pygame", "logging", "random", "sys"], "excludes": [
#    "tkinter"], "include_files": ["resources"], "includes": ["StarTradingCompany"]}

# base = None

# setup(name="StarTradingCompany",
#      version="0.1",
#      description="Star Trading Company",
#      options={"build_exe": build_exe_options},
#      executables=[Executable("app.py", base=base)])

from cx_Freeze import setup, Executable

executables = [
    Executable('app.py')
]

include_files = [
    #    ("resources/fonts/TruenoBd.otf", "Resources/TruenoBd.otf"),
    #    ("resources/images/16ShipCollection.png", "Resources/16ShipCollection.png")
    "Resources"
]

build_exe_options = {"packages": ["os", "pygame", "logging", "random", "sys"], "excludes": [
    "tkinter"], "include_files": include_files, "includes": ["StarTradingCompany"]}


setup(name='StarTradingCompany',
      version='0.1',
      description='Star Trading Company',
      options={"build_exe": build_exe_options},
      executables=executables
      )
