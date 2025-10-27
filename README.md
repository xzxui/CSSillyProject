Welcome to our project! 

This brief intro serves as an aid to read our code and test our entire program and its several modules. 

  

The newest version of our project can always be found at: 

https://github.com/xzxui/CSSillyProject 

  

Our project is divided into modules in a manner that limits all user input inside the ModuleMainLoop.py, which is the GUI for our program, and this module shall passes these input into other modules when they are called. Therefore, only ModuleMainLoop has instructions for user input, so when grading modules other than ModuleMainLoop, the documentation of the arguments of the functions might be interpreted as the instruction for input. 

On the other hand, the output of our program are excel files that the user can directly read and messages shown to the user in the GUI. 

  

To build the environment, a ‘requirements.txt’ is provided. Simply run pip install -r requirements.txt in cmd. Alternatively, use command line and run ./venv/Scripts/activate.bat or use powershell and run ./venv/Scripts/Activate.ps1, and use that command line/powershell window to do all the testing. 

  

To run our project, simply type python ModuleMainLoop.py, and open the url as instructed. 
