// BoardDetail.js -- Tyler Smith -- 10/16/12

//var boardPins;
//var otherPins;
var pins = new Array();

var script_tag = document.getElementById('ajaxScript');
var url = script_tag.getAttribute("data-url");
var isEditable = (script_tag.getAttribute("data-editable")=="True")?true:false;

function updateView(data)
{
	var count = 0; 
	//boardPins = data['pins'];
	$.each(data['pins'],function(index, pin){
		pin["boardPin"] = true;
		pins.push(pin);
		createBoardPin(count,pin);
		count++;
	});
	if (isEditable)
	{
		//otherPins = data['publicPins'];
		$.each(data['publicPins'],function(index, pin){
			pin["boardPin"] = false;
			pins.push(pin);
			createOtherPin(count,pin);
			count++;
		});
	}
	displayMessage();

}

function createBoardPin(index,pin)
{
	console.log(pin);
	var pinFrame = $("#pinFrame").clone();
	pinFrame.attr("data-identifier", index);
	pinFrame.addClass("boardPin");
	pinFrame.css("display","inline");
	pinFrame.find("img").attr("src",pin["imgUrl"]);
	pinFrame.find(".pinCaption").text(pin["caption"]);
	if (!isEditable)
		pinFrame.find(".removeButton").remove();
	pinFrame.hide().appendTo("#boardPins").show();
	return pinFrame;
}

function createOtherPin(index,pin)
{
	console.log(pin);
	var pinFrame = $("#smallPinFrame").clone();
	pinFrame.attr("data-identifier", index);
	pinFrame.addClass("otherPin");
	pinFrame.css("display","inline");
	pinFrame.find("img").attr("src",pin["imgUrl"]);
	pinFrame.find(".pinCaption").text(pin["caption"]);
	pinFrame.hide().appendTo("#otherPins").show();	
	return pinFrame;
}

function getContent()
{
	$.ajax(url+".json",
	{
		type:"GET",
		dataType: "json",
		success: function(data)
		{
			updateView(data);
			console.log("Data found successfully: " + data);
		},
		error: function(error)
		{
			alert("An error occurred finding the data: " + error["status"] + " error");
		}
		
	});
}

function changePin(method,button) 
{
	var type = (method == "Add")?true:false;
	$parentDiv = $(button).parent().parent();
	console.log($parentDiv);
	$id = parseInt($parentDiv.attr("data-identifier"));
	$parentDiv.remove();
	console.log($id);
	var pinFrame;
	if (type)
		pinFrame = createBoardPin($id,pins[$id]);
	else
		pinFrame = createOtherPin($id,pins[$id]);

	pins[$id]["boardPin"] = !pins[$id]["boardPin"];
	$.ajax(url,
	{
		type:"POST",
		data: 
		{
			"method":(type)?"AddPin":"RemovePin",
			"pinID":pins[$id]["id"]//otherPins[$id]["id"]
		},
		success: function(data)
		{
			displayMessage();
			console.log("Data saved");
		},
		error: function(error)
		{
			pins[$id]["boardPin"] = !pins[$id]["boardPin"];
			pinFrame.remove();
			if (!type)
				pinFrame = createBoardPin($id,pins[$id]);
			else
				pinFrame = createOtherPin($id,pins[$id]);
			console.log(error);
			alert("An error occurred adding the pin: " + error["status"] + " error");
		}
				
	});
}

function addPin()
{
	changePin("Add",this);
}

function removePin()
{
	changePin("Remove",this);
}

function displayMessage()
{
	if ($("#boardPins").find("div").size()>0)
		$("#placeholder").hide();
	else
		$("#placeholder").show();
}

function createNameEditBox()
{
	var title = $("#title").text();
	$("#headerBox").prepend('<input id="title-edit" class="" style="width:70%; display:none; color:#333; font-size:3em; font-weight:bold;" value="'+title+'"></input>');
}

function isEditingTitle()
{
	$("#title").hide();
	$("#title-edit").show().focus();
}

function keyPressedOnTitleEdit(e)
{
	 if ($("#title-edit").val() == "")
		 return;
	 var code = (e.keyCode ? e.keyCode : e.which);
	 if(code == 13) 
	 { 
	     $("#title").text($("#title-edit").val());
	     $("#title-edit").hide();
	     $("#title").show();
		 saveName();
	 }
}

function saveName()
{
	$.ajax(url,
	{
		type:"POST",
		data: {
			"method":"saveName",
			"name":$("#title").text()
		},
		success: function(data)
		{
			console.log("Title Updated: " + data);
		},
		error: function(error)
		{
			alert("An error occurred saving the title: " + error);
		}
		
	});
}

function privateValueChanged(e)
{
	$.ajax(url,
	{
		type:"POST",
		data:{
			"method": "privateChanged",
			"private": $(this).val()
		},
		success: function(data)
		{
			console.log("Changed to " + ((data=="True")?"Private":"Public"));
		},
		error: function(error)
		{
			alert("An error occurred saving the data: " + error);
		}
		
	});
}



$(document).ready(function(){
	getContent();
	if (isEditable)
	{
		$(".addButton").live("click",addPin);
		$(".removeButton").live("click",removePin);
		
		createNameEditBox();
		$("#title").on("click", isEditingTitle);
		$("#title-edit").unbind('keypress');
		$("#title-edit").bind("keyup",keyPressedOnTitleEdit);
		
		$("#private").on("change",privateValueChanged);
	}
	else
	{
		$("#boardPins").css("border-bottom","0px");
	}


});