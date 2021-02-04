Draw.loadPlugin(function(ui) {

// The BPMN-RPA Windows module is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// The BPMN-RPA Windows module is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.


	// ui.editor = mxEditor!!!!!!


	// Adds menu
	mxResources.parse('Reset=Reset');
	mxResources.parse('Check Flow=Check Flow');
	var graph = ui.editor.graph;
	var model = graph.model;
	var tp;
    ui.actions.addAction('Reset', function()
    {
		 // Displays status message
		ui.editor.setStatus('Resetting the flow...');
		graph.clearCellOverlays(tmp);
		for (var key in graph.getModel().cells)
		{
			var tmp = graph.getModel().getCell(key);
			graph.setCellStyles(mxConstants.STYLE_STROKECOLOR, 'black', [tmp]);
		}
		ui.editor.setStatus('Reset Done.');

    });


    ui.actions.addAction('Check Flow', function()
    {
		graph.getModel().beginUpdate();
		ui.editor.setStatus('Checking the flow for errors...');
		var variables = [];
		var img = new mxImage(mxClient.imageBasePath + '/error.gif', 15,16);
		var _err = 0;
		var has_start = -1;
		var has_end = 0;
		var has_loopcounter = -1;
		var has_loopitemscheck = -1;
		var startnode;
		var forgotten_loopvariable = -1
		for (var key in graph.getModel().cells)
		{
			var tmp = graph.getModel().getCell(key);
			graph.setCellStyles(mxConstants.STYLE_STROKECOLOR, 'black', [tmp]);
			graph.clearCellOverlays(tmp);
			var outgoing = graph.getEdges(tmp, null, false, true, false, false);
			if(outgoing.length > 1)
			{
				//Exclusive gateway
				var blntrue = -1;
				var blnfalse = -1;
				var msg = "";
				var attr;
				for(var c = 0; c < outgoing.length; c++)
				{
					outg = outgoing[c];
					try{
						if(String(graph.getLabel(outg)).toLowerCase()== "true")
						{
							blntrue = 0;
						}
					}
					catch(err){
					}
					try{
						if(String(graph.getLabel(outg)).toLowerCase()== "false")
						{
							blnfalse = 0;
						}
					}
					catch(err){
					}
				}
				if(blntrue == -1 && blnfalse == -1)
				{
					attr = tmp.getAttribute('Type', '')
					if(attr=='Exclusive Gateway')
					{
						msg = "This exclusive gateway has neither a 'True' nor a 'False' outgoing sequence arrow." ;
					}
					else
					{
						msg = "This step has more than one outgoing sequence arrow." ;
					}
				}
				if(blntrue == 0 && blnfalse == -1)
				{
					msg = "This exclusive gateway has no 'False' outgoing sequence arrow." ;
				}
				if(blntrue == -1 && blnfalse == 0)
				{
					msg = "This exclusive gateway has no 'True' outgoing sequence arrow." ;
				}
				if(blntrue == -1 || blnfalse == -1)
				{
					graph.setCellStyles(mxConstants.STYLE_STROKECOLOR, 'red', [tmp]);
					var overlay_gw = new mxCellOverlay(img, msg);
					graph.addCellOverlay(tmp, overlay_gw);
				}
			}
			if (graph.getModel().isVertex(tmp))
			{

				if(String(graph.getLabel(tmp)).toLowerCase()== "start")
				{
					has_start = 0;
					startnode = tmp;
				}
				if(String(graph.getLabel(tmp)).toLowerCase()== "end")
				{
					has_end = 0
				}
				if (mxUtils.isNode(tmp.value))
				{
					attr = tmp.getAttribute('Loopcounter', '')
					if(attr !='')
					{
						has_loopcounter = 0;
					}
					attr = tmp.getAttribute('Function', '')
					if(attr =='loop_items_check')
					{
						has_loopitemscheck = 0;
						lv = tmp.getAttribute('Loop_variable', '');
						if (lv=='')
						{
							forgotten_loopvariable = 0
							var overlay_source = new mxCellOverlay(img, "This loop items check has no variable to check.");
							graph.addCellOverlay(tmp, overlay_source);
							graph.setCellStyles(mxConstants.STYLE_STROKECOLOR, 'red', [tmp]);
							_err = -1;
						}
					}
				}

				//try{
				//	if(tmp.hasAttribute('Function'))
				//	{
				//		if(tmp.getAttribute('Function', null)=='loop_items_check')
				//		{
				//			has_loopitemscheck = 0;
				//		}
				//	}
				//}
				//catch (err){}
				//try{
				//	if(tmp.hasAttribute('Output_variable'))
				//	{
				//		variables.push(tmp.getAttribute('Output_variable', null));
				//	}
				//}
				//catch (err){}

			}
			if (graph.getModel().isEdge(tmp))
			{
				try{
					var src = tmp.source.id;
				}
				catch(err) {
					var overlay_source = new mxCellOverlay(img, "This sequence arrow is not connected to a source.");
					graph.addCellOverlay(tmp, overlay_source);
					graph.setCellStyles(mxConstants.STYLE_STROKECOLOR, 'red', [tmp]);
					_err = -1;
				}
				try{
					var x = tmp.target.id;
				}
				catch(err) {
					var overlay_target = new mxCellOverlay(img, "This sequence arrow is not connected to a target.");
					graph.addCellOverlay(tmp, overlay_target);
					graph.setCellStyles(mxConstants.STYLE_STROKECOLOR, 'red', [tmp]);
					_err = -1
				}
			}
		}
		graph.getModel().endUpdate();
		if (_err == 0 && has_start == 0 && has_end==0){
			if (has_loopcounter==0 && has_loopitemscheck==-1)
			{
				mxUtils.error("Your Flow has a Loopcounter, but no Loopitems check (like 'more loop items?'). Please check...", 250, true, mxUtils.errorImage);
				 _err = -1;
			}
			else if (has_loopcounter==-1 && has_loopitemscheck==0)
			{
				mxUtils.error("Your Flow has a Loop Items Check, but no Loopcounter. Please check...", 250, true, mxUtils.errorImage);
				 _err = -1;
			}
			else{ui.editor.setStatus('Flow checked, no errors found.');}

		}
		else if(has_start==-1 && has_end == 0)
		{
			 mxUtils.error("Your Flow has no Start!", 250, true, mxUtils.errorImage);
			 _err = -1;
		}
		//else if(has_end==-1 && has_start==0)
		//{
			 //mxUtils.error("Your Flow has no End!", 250, true, mxUtils.errorImage);
			 //_err = -1;
		//}
		else if(has_end==-1 && has_start==-1)
		{
			 mxUtils.error("Your Flow has no Start and no End!", 250, true, mxUtils.errorImage);
			 _err = -1;
		}
		else{
			mxUtils.error("Your Flow has Errors. Please check...", 250, true, mxUtils.errorImage);
			 _err = -1;
		}
		//Walk the loop from startnode
		//if (_err == 0)
		//{
		//	current_node = startnode;
		//	while(current_node)
		//	{
		//		outgoing = graph.getEdges(current_node, null, false, true, false, false);
		//		if(outgoing.length == 1)
		//		{
		//
		//			current_node = graph.getCell(outgoing[0].id);
		//		}
		//	}
		//
		//}

    });

	ui.menus.put('BPMN-RPA', new Menu(function(menu, parent)
	{
		ui.menus.addMenuItems(menu, ['-', 'Check Flow', '-', 'Reset']);
	}));

    if (ui.menubar != null)
    {
		var menu = ui.menubar.addMenu('BPMN-RPA', ui.menus.get('BPMN-RPA').funct);
		menu.parentNode.insertBefore(menu, menu.previousSibling.previousSibling.previousSibling);
    }

});
