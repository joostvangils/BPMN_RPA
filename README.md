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
* [Example](#Example)


#### Quick start
- Open the diagram.net (or DrawIO desktop) app
- Import the BPMN RPA Shapes ( file -> import from -> device)
- Create your Diagram in https://app.diagrams.net/ or in the Desktop application by using the BPMN_RPA Shape-set
- Set the right mappings for each shape
- Save your diagram as XML
- Run your workflow by using the WorkflowEngine

#### Allowed Shapes
For the Workflow engine to recognize the flow, you are restricted to use the following Shapes:

##### Tasks

   * Mandatory attributes:
     * Module: This is the full path to the Python file that contains your Class and/or function.
        * From file: specify the full path (including extension .py) if you want to load you module from a specific file location.
        * From file in Script directory: specify only the module name (including extension .py) of the module you want to use.
        * From installed package: specify only the module name (without extension .py).
     * Class: for reference to the Class to use in the Module.
     * Function: The name of the Function to Call.
     * Output_variable: The name of the variable that must store the output of the current action.
     * Mapping: The mapping of the input parameters to the output of the previous task. This shoul be a string, containing the key-value pairs. <br>
       P.e.: param1=0;param2=%test[2]% which means: use the first output of the previous step as the input parameter with the name 'param1' and use the third element of the variable with name '%test%' as the second input parameter with the name 'param2'.
    
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
The % sign is used as brackets around a Variable. For example, "%name%" is the Variable 'name'. When you use %name% as an input, the Action will use the value that has previously been stored in that Variable, so you should have an earlier Action that assigned a value to %name% as an output. By assigning output values to Variables, and then using them as input in later steps, you can pass information through a Workflow.
 
You can store any type of information into a variable, like:
* Texts
* Numbers
* Booleans
* Lists
* Class objects 
etc. etc.

##### Retreiving information
In order to retrieve a specific item of a list, you must use the following format (notation): %VariableName[ItemNumber]%. The “ItemNumber” should be 0 for the first item of the list, 1 for the second and so on. For example, if you have a list that is stored in the variable %MyList% and contains 10 items, you can retrieve the first item with: %MyList[0]% and the last item with %MyList[9]%.

For data tables, you must use the following notation: %VariableName[RowNumber][ColumnNumber]%. “RowNumber” and “ColumnNumber” should be 0 for the first item (row or column), 1 for the second and so on. For example, if you have a data table that is stored in the variable %MyDataTable%, you can retrieve the first item with: %MyDataTable[0][0]%. 

##### Example

```Python
engine = WorkflowEngine("c:\\\python\\\python.exe")
doc = engine.open("test.xml")
steps = engine.get_flow(doc)
engine.run_flow(steps)
```

You can download the DrawIO desktop version [here](https://github.com/jgraph/drawio-desktop/releases)
