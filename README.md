# BPMN_RPA
Robotic Process Automation in Windows by using Driagrams.net BPMN diagrams.

With this Framework you can draw Business Process Model Notation based Diagrams and run those diagrams with a WorkflowEngine.
It is based on the mxGraph model notation of https://app.diagrams.net/.

### Content:
* [Quick Start](#Quick-start)
* [Allowed Shapes](#Allowed-Shapes)
  * [Tasks](#Tasks)
  * [Gateways](#Gateways)
  * [Sequence flow arrow](#Sequence-flow-arrow)
* [Variables](#Variables)
* [Loops](#Loops)
* [Example](#Example)


#### Quick start
- Open the diagram.net (or DrawIO desktop) app
- Import one of the BPMN RPA Shape libraries ( file -> import from -> device)
- Create your Diagram in https://app.diagrams.net/ or in the Desktop application by using the BPMN_RPA Shape-set
- Set the right mappings for each shape
- Save your diagram as XML
- Run your workflow by using the WorkflowEngine

#### Allowed Shapes
For the Workflow engine to recognize the flow, you are restricted to use the following Shapes:

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
     * You can specify any input value for the called function directly by adding an extra attribute to the shape with **exactly the same name** as the expected input parameter(s) of the function. If you add these extra attributes, but decide to leave these value(s) blank, then the mapping values (output values from previous step) will be used. In this way you can combine direct values with mapping values.
      
      P.e.: to call 
      ```Python
      os.system('Notepad')
      ```
      You look up the name of the input parameter(s) in the official documentation (or in the code). In this example, the input parameter is called 'command'. You then set the following attributes:<br><br>
      <a href="url"><img src="https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/Images/os_system.PNG" height="450" width="400" ></a>
    
##### GateWays
   * For now you can only use the Exclusive Gateway. This Gateway has to have a Data attribute named 'Type' with the value 'Exclusive Gateway'.
##### Sequence flow arrow
   * If the Sequence flow arrow is originating from an Exclusive Gateway, the Sequence flow arrow must have a value of 'True' or 'False'.

#### Variables
The % sign is used as brackets around a Variable. For example, "%name%" is the Variable 'name'. When you use %name% as an input, the Action will use the value that has previously been stored in that Variable, so you should have an earlier Action that assigned a value to %name% as an output. By assigning output values to Variables, and then using them as input in later steps, you can pass information through a Workflow.<br><br>
You can store any type of information into a variable, like:
* Texts
* Numbers
* Booleans
* Lists
* Class objects <br>
etc. etc.

#### Loops
You can create loops by using exclusive gateways. An exclusive gateway should always have two sequence flow arrows: one with the label "True" and the other with the label "False". The actual true/false decision isn't made in the exclusive gateway itself, but in the last sask before the exclusive gateway. An example:<br>
<a href="url"><img src="https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/Images/Loop_example.PNG" height="300" width="400" ></a>

Explanation:
1. The loop starts with the 'Loop list' Task. This The function 'returnlist'is called in the module 'hello_world.py. There is no path specified for the module and the module name ends with '.py', so the path to the module will be '<current directory>\Scripts\hello_world.py'. This script returns a List with the elements ["this", "is", "a", "test"] and stores it in the variable named '%test%'. The attribute 'Loopcounter'is the important indication that this Task will be the start of a loop. The number in this field will be the start for the loop (p.e.: setting 'Loopcounter'to 1 results in loping the list from the second element in the list).<br>
<a href="url"><img src="https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/Images/Looplist_attributes.PNG" height="100" width="400" ></a>
2. The MessageBox function is called ('<current directory>\Scripts\MessageBox.py'). The title will be "test", and the message will be a word from the list in confirmity with the 'Loopcounter' number ('%test%').<br>
<a href="url"><img src="https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/Images/MessageBox_attributes.PNG" height="100" width="400" ></a><br>
<a href="url"><img src="https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/Images/loop_firstexecution.PNG" height="200" width="400" ></a><br>
3. The 'More loop items?' Task checks if the List in the variable '%test%' has any items left to loop. If so, then it returns True, otherwise it will return False. If it returns True, the 'Loopcounter' is raised by 1. The function is called within the WorkflowEngine class (no 'Module'or 'Class' specified).<br>
<a href="url"><img src="https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/Images/Looptest_attributes.PNG" height="100" width="400" ></a>
4. The Exclusive Gateway is deciding which Sequence Flow Arrow to follow. If the loop is still ongoing, the 'Loop List' Task will be called again and the next element in the list will be returned.

##### Retreiving information
In order to retrieve a specific item of a list, you must use the following format (notation): %VariableName[ItemNumber]%. The “ItemNumber” should be 0 for the first item of the list, 1 for the second and so on. For example, if you have a list that is stored in the variable %MyList% and contains 10 items, you can retrieve the first item with: %MyList[0]% and the last item with %MyList[9]%. For data tables, you must use the following notation: %VariableName[RowNumber][ColumnNumber]%.

If you would like to retreive an attribute of a stored object or dictionary in a variable, then you must use the %VariableName.attributeName% notation. Just use the %VariableName% notation to retreive the full object or dictionary.

##### Example

```Python
engine = WorkflowEngine("c:\\\python\\\python.exe")
doc = engine.open("test.xml")
steps = engine.get_flow(doc)
engine.run_flow(steps)
```

You can download the DrawIO desktop version [here](https://github.com/jgraph/drawio-desktop/releases)
