# BPMN_RPA
Robotic Process Automation in Windows and Linux by using BPMN diagrams.

With this Framework you can draw Business Process Model Notation based Diagrams and run those diagrams with a WorkflowEngine.
You can run flows that were made in DrawIO (based on the mxGraph model notation of https://app.diagrams.net/) or with Ms Visio. There is no need for installing DrawIO or Visio to run the flows. Installing these applications is only needed for creating the flows.

### Content:
* [Quick Start](#Quick-start)
* [First start](#First-start)
* [Recognized Shapes](#Recognized-Shapes)
  * [Tasks](#Tasks)
  * [Gateways](#Gateways)
  * [Sequence flow arrow](#Sequence-flow-arrow)
* [Variables](#Variables)
  * [System variables](#System-variables)
* [Loops](#Loops)
  * [Special loop variable options](#Special-loop-variable-options)
* [Instantiate a Class and use in Flow](#Instantiate-a-Class-and-use-in-Flow)
* [Passing input to the WorkflowEngine](#Passing-input-to-the-WorkflowEngine)
* [Logging](#Logging)
* [End a flow](#End-a-flow)
  * [End flow with exitcode](#End-flow-with-exitcode)
* [PlugIn](#PlugIn)
* [Example](#Example)


#### Quick start
- Open the application for creating the flow (diagram.net, DrawIO desktop app or Ms Visio)
- Import the BPMN RPA Shape library ( file -> open library, which you can download for DrawIO [here](https://github.com/joostvangils/BPMN_RPA/raw/main/BPMN_RPA/Shapes.xml) and for MsVisio [here](https://github.com/joostvangils/BPMN_RPA/raw/main/BPMN_RPA/Shapes.vssx))
- Create your Diagram in https://app.diagrams.net/ or in the Desktop application (DrawIO or Ms Visio) by using the appropriate BPMN_RPA Shape-set
- Save your diagram (as XML for DrawIO or as vsdx for Visio)
- Run your workflow by using the [BPMN_RPA_Starter.py](https://github.com/joostvangils/BPMN_RPA/raw/main/BPMN_RPA/BPMN_RPA_Starter.py) or the WorkflowEngine by code

#### First start
The first time you will try to run a Flow, you will be asked to enter the path of your install directory. If you are using Windows, the path of the install directory will be saved in the registry (path saved in registry key 'HKEY_CURRENT_USER\Software\BPMN_RPA\dbPath') and is used to create a SQLite database for logging purposes, called 'Orchestrator.db'. The WorkflowEngine must also know where your python.exe is located. You will be asked to enter the full path to the python.exe file (including the '.exe' extension). Again, if you are using Windows this path will be saved in registry key 'HKEY_CURRENT_USER\Software\BPMN_RPA\PythonPath'. For Linux users a "settings" file together with the orchestrator database will be created.

#### Recognized Shapes
For the Workflow engine to recognize the flow, you must use the recommended shape attributes with the following Shapes:

##### Tasks<br>
You can use Tasks to call Python scripts. For the WorkflowEngine to recognize the Tasks, each Task has to contain certain attributes to make this possible.<br>
   * Recommended attributes:
     * Module: This is the full path to the Python file that contains your Class and/or function.
        * From file: specify the full path (including extension .py) if you want to load you module from a specific file location.
        * From file in Script directory: specify only the module name (including extension .py) of the module you want to use.
        * From installed package: specify only the module name (without extension .py).
        * No Module field: you can delete the Module field to call a function in the WorkflowEngine class directly.
     * Class: for reference to the Class to use in the Module. You can delete this field if the called module has only functions and no class.
     * Function: The name of the Function to Call. This field is mandatory.
     * Output_variable: The name of the variable that must store the output of the current action. If you don't use this field (or delete it), the current Task will have no output that can be used by other Tasks.
    
   * Optional attributes:
     * You can specify any input value for the called function directly by adding an extra attribute to the shape with **exactly the same name** as the expected input parameter(s) of the function.
      
      P.e.: to call 
      ```Python
      os.system('Notepad')
      ```
      You look up the name of the input parameter(s) in the official documentation (or in the code). In this example, the input parameter is called 'command'. You then set the following attributes:<br><br>
      <a href="url"><img src="https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/BPMN_RPA/Images/os_system.PNG" height="450" width="400" ></a>
    
##### GateWays
   * For now you can only use the Exclusive Gateway and the Parallel Gateway. These Gateways must have a Data attribute named 'Type' with the value 'Exclusive Gateway' or 'Parallel Gateway' respectively. The use of the Parallel Gateway is momentarely restricted to transform multiple inputs into one output. At this moment multiple outputs are not yet allowed.
   
##### Sequence flow arrow
   * If the Sequence flow arrow is originating from an Exclusive Gateway, the Sequence flow arrow must have a value of 'True' or 'False'.

#### Variables
The % sign is used as brackets around a Variable. For example, "%name%" is the Variable 'name'. When you use %name% as an input, the Action will use the value that has previously been stored in that Variable, so you should have an earlier Action that assigned a value to %name% as an output. By assigning output values to Variables, and then using them as input in later steps, you can pass information through a Workflow.<br><br>
You can store any type of information into a variable, like:
* Texts
* Numbers
* Booleans
* Lists
* Dictionary
* Class objects <br>
etc. etc.

##### System variables
System variables are pre-defined variables that provide information that can be used in flow attributes. The System variables content is set by the WorkflowEngine automatically and cannot be changed. All system variables begin with a double underscore between precent signs. Available variables:<br>
* __%\_\_folder_desktop\_\_%__: returns the desktop folder of the current user
* __%\_\_folder_downloads\_\_%__: returns the downloads folder of the current user
* __%\_\_folder_system\_\_%__: returns the windows system folder
* __%\_\_month\_\_%__: returns the current month
* __%\_\_now\_\_%__: returns the datetime now() object
* __%\_\_now_formatted\_\_%__: returns today with time in the format 'dd-mm-yyyy_hhmmss'
* __%\_\_time\_\_%__: returns the current time
* __%\_\_time_formatted\_\_%__: returns the current time in 'hh:mm:ss' format
* __%\_\_today\_\_%__: returns the current date
* __%\_\_today_formatted\_\_%__: returns the current date in 'dd-mm-yyyy' format
* __%\_\_tomorrow\_\_%__: returns the date of tomorrow
* __%\_\_tomorrow_formatted\_\_%__: returns the date of tomorrow in 'dd-mm-yyyy' format
* __%\_\_user_name\_\_%__: returns the account name of the user that is currently logged in
* __%\_\_weeknumber\_\_%__: returns the current weeknumber
* __%\_\_year\_\_%__: returns the current year number
* __%\_\_yesterday\_\_%__: returns the date of yesterday
* __%\_\_yesterday_formatted\_\_%__: returns the date of yesterday in 'dd-mm-yyyy' format

#### Loops
You can create loops by using exclusive gateways. An exclusive gateway should always have two sequence flow arrows: one with the label "True" and the other with the label "False". The actual true/false decision isn't made in the exclusive gateway itself, but in the last Task before the exclusive gateway. A loop is started by a Task that is calling a Python script that returns a list. The task is recognized as the start of the loop by adding/using the attribute 'Loopcounter'. The loopcounter number is the starting point for the loop (for returning the n-th element of the list). The task before the Exclusive Gateway should be the 'More loop items?' Task. You can find this Task in the predefined Shapes. This Task should have two attributes: 'Function' with value 'loop_items_check' will call the loop_items_check() function in the WorkflowEngine object, and 'Loop_variable' with the variable name to loop as value. The loop_items_check() function will return True or False, which will be used by the WorkflowEngine to decide which Sequence Flow Arrow to follow.

##### Special loop variable options
You can get the value of the loopvariable counter by using the '.counter' attribute of the loopvariable (p.e.: %test.counter%). To get the whole list that is looped, use the '.object' attribute of the loopvariable (p.e.: '%test.object%') or just the variable name (like '%test%').

An example:<br>
<a href="url"><img src="https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/BPMN_RPA/Images/Loop_example.PNG" height="300" width="400" ></a>

Explanation:
1. The loop starts with the 'Loop list' Task. This The function 'returnlist' is called in the module 'hello_world.py'. There is no path specified for the module and the module name ends with '.py', so the path to the module will be '*current directory*\Scripts\hello_world.py'. This script returns a List with the elements ["this", "is", "a", "test"] and stores it in the variable named '%test%'. The attribute 'Loopcounter' is the important indication that this Task will be the start of a loop. The number in this field will be the start for the loop (p.e.: setting 'Loopcounter' to 1 results in loping the list from the second element in the list).<br>
<a href="url"><img src="https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/BPMN_RPA/Images/Looplist_attributes.PNG" height="100" width="400" ></a>
2. The MessageBox function is called ('*current directory*\Scripts\MessageBox.py'). The title will be "test", and the message will be a word from the list in confirmity with the 'Loopcounter' number ('%test%').<br>
<a href="url"><img src="https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/BPMN_RPA/Images/MessageBox_attributes.PNG" height="100" width="400" ></a><br>
<a href="url"><img src="https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/BPMN_RPA/Images/loop_firstexecution.PNG" height="200" width="400" ></a><br>
3. The 'More loop items?' Task checks if the List in the variable '%test%' has any items left to loop. If so, then it returns True, otherwise it will return False. If it returns True, the 'Loopcounter' is raised by 1. The function is called within the WorkflowEngine class (no 'Module'or 'Class' specified).<br>
<a href="url"><img src="https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/BPMN_RPA/Images/Looptest_attributes.PNG" height="100" width="400" ></a>
4. The Exclusive Gateway is deciding which Sequence Flow Arrow to follow. If the loop is still ongoing, the 'Loop List' Task will be called again and the next element in the list will be returned.

#### Retreiving information
In order to retrieve a specific item of a list, you must use the following format (notation): %VariableName[ItemNumber]%. The “ItemNumber” should be 0 for the first item of the list, 1 for the second and so on. For example, if you have a list that is stored in the variable %MyList% and contains 10 items, you can retrieve the first item with: %MyList[0]% and the last item with %MyList[9]%. For data tables, you must use the following notation: %VariableName[RowNumber][ColumnNumber]%.

If you would like to retreive an attribute of a stored object or dictionary in a variable, then you must use the %VariableName.attributeName% notation. Just use the %VariableName% notation to retreive the full object or dictionary.

#### Instantiate a Class and use in Flow
You can instantiate a Python class by using ony these attributes (leave the 'Function' attribute blank or delete it):<br>
<a href="url"><img src="https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/BPMN_RPA/Images/Instantiate_class1.PNG" height="100" width="400" ></a><br>
This instantiates the class and saves the instance in the variable %test%.
You can call any function of the class object by use of these attributes in Tasks following the instantiation Task (leave the 'Module' attribute blank or delete it):<br>
<a href="url"><img src="https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/BPMN_RPA/Images/Instantiate_class2.PNG" height="100" width="400" ></a><br>

#### Passing input to the WorkflowEngine
You can pass input to the WorkflowEnging by using the 'input_parameter' argument. Please note that it is only possible to pass a single object to the WorkflowEngine. Wrap all your inputs into a single object (like: dictionary or custom object) to pass multiple values to the WorkflowEngine.
```Python
myObject = ['this could be', 'any', 'type', 'of', 'object']
engine = WorkflowEngine(input_parameter=myObject)
```
Call the internal 'get_input_parameter' function to retreive this input value and assign it to a variable name for later use in your flow:<br>
<a href="url"><img src="https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/BPMN_RPA/Images/Get_input_parameter.PNG" height="100" width="400" ></a><br>

When starting a Workflow from the commandline, you may use the 'As_ditcionary' option in the 'Get input paramater' Shape of your Flow with the value 'True' to convert the string input to a dictionary object. P.e.: 
```console
c:\> python BPMN_RPA_Starter.py test.xml "{\"key1\": \"value1\",\"key2\": \"value2\"}"
```

#### Logging
The WorkflowEngine logs all executed steps in a SQLite database, called 'Orchestrator.db'. This database is located in the install directory. If the install directory is unknown when starting the WorkflowEngine, the WorkflowEngine will ask you for the folder. This path then will be saved in the registry and the Orchestrator database will be created in that folder.

#### End a flow
The ending of a flow will also be logged in the Orchestrator database. When ending a flow, the output of the last executed step will also be the output of the entire flow, unless the flow is ended with an exitcode.

##### End flow with exitcode
If you wish to end your flow with an exitcode (0 for OK and -1 for not OK) then you can call one of the internal functions of the WorkflowEngine:
* exitcode_ok
* exitcode_not_ok<br>
<br>
Just call one of the above functions by only passing the 'function' parameter (thus not passing the 'Module' and 'Class' parameter):<br>
<a href="url"><img src="https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/BPMN_RPA/Images/Exit_not_ok.PNG" height="120" width="350" ></a><br>

#### PlugIn
BPMN-RPA has a Drawio plugin for checking your flows. You can download it here: <a href="https://github.com/joostvangils/BPMN_RPA/raw/main/BPMN_RPA/BPMN-RPA_PlugIn.js">PlugIn</a><br>

#### Example
Start a flow from the commandline:
1. Open a command prompt
2. Enter:
```console
c:\> python BPMN_RPA_Starter.py test.xml
```

Start a flow in code:
```Python
engine = WorkflowEngine()
doc = engine.open("test.xml")
steps = engine.get_flow(doc)
engine.run_flow(steps)
```

You can download the DrawIO desktop version [here](https://github.com/jgraph/drawio-desktop/releases)
