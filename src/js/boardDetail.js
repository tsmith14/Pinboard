// BoardDetail.js -- Tyler Smith -- 10/16/12

var boardPins;
var otherPins;

var script_tag = document.getElementById('ajaxScript');
var url = script_tag.getAttribute("data-url");
var isEditable = (script_tag.getAttribute("data-editable")=="True")?true:false;

function updateView(data)
{
	if (data['pins'].length>0)
		$("#placeholder").hide();
	else
		$("#placeholder").show();
	boardPins = data['pins'];
	$.each(data['pins'],function(index, pin){
		createBoardPin(index,pin);
	});
	if (isEditable)
	{
		otherPins = data['publicPins'];
		$.each(data['publicPins'],function(index, pin){
			createOtherPin(index,pin)
		});
	}


	
}

function createBoardPin(index,pin)
{
	var pinFrame = $("#pinFrame").clone();
	pinFrame.attr("id","boardPin"+index);
	pinFrame.css("display","inline");
	pinFrame.find("img").attr("src",pin["imgUrl"]);
	pinFrame.find(".pinCaption").text(pin["caption"]);
	if (!isEditable)
		pinFrame.find(".removeButton").remove();
	pinFrame.hide().appendTo("#boardPins").show();
}

function createOtherPin(index,pin)
{
	var pinFrame = $("#smallPinFrame").clone();
	pinFrame.attr("id","publicPin"+index);
	pinFrame.css("display","inline");
	pinFrame.find("img").attr("src",pin["imgUrl"]);
	pinFrame.find(".pinCaption").text(pin["caption"]);
	pinFrame.hide().appendTo("#otherPins").show();	
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

function addPin()
{
	console.log($(this).parent().parent()[0]);
	$parentDiv = $(this).parent().parent();
	$parentDiv.remove();
	$id = parseInt($parentDiv.attr("id").substring(9));
	console.log($id);
	console.log(otherPins[$id]);
	createBoardPin($id,otherPins[$id]);
	$.ajax(url,
	{
		type:"POST",
		data: {
			"method":"AddPin",
			"pinID":otherPins[$id]["id"]
		},
		success: function(data)
		{
			clearView();
			getContent();
			console.log("Data saved");
			
		},
		error: function(error)
		{
			console.log(error);
			alert("An error occurred adding the pin: " + error["status"] + " error");
			clearView();
			getContent();
		}
		
	});
}

function removePin()
{
	$parentDiv = $(this).parent().parent();
	$parentDiv.remove();
	$id = parseInt($parentDiv.attr("id").substring(8));
	createOtherPin($id,boardPins[$id]);
	$.ajax(url,
	{
		type:"POST",
		data: {
			"method":"RemovePin",
			"pinID":boardPins[$id]["id"]
		},
		success: function(data)
		{
			clearView();
			getContent();
			console.log("Data saved");
		},
		error: function(error)
		{
			alert("An error occurred removing the pin: " + error);
			clearView();
			getContent();
		}
		
	});
}

function clearView()
{
	boardPins = new Array();
	otherPins = new Array();
	$("#boardPins").html("");
	$("#otherPins").html("");
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