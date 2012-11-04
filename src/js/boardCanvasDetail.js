// BoardCanvasDetail.js -- Tyler Smith -- 10/31/12

var pins; 

var script_tag = document.getElementById('ajaxScript');
var url = script_tag.getAttribute("data-url");
var isEditable = (script_tag.getAttribute("data-editable")=="True")?true:false;

var isDragging = false;
var startMouseX;
var startMouseY;
var currentImage;
var imageIndex;
var canvas;
var ctx;
var images = new Array();

function updateView()
{
	images = new Array();
	$.each(pins,function(){
		draw($(this));
	});
	
}

function getContent()
{
	$.ajax(url+".json",
	{
		type:"GET",
		dataType: "json",
		success: function(data)
		{
			pins = data['pins'];
			updateView();
			console.log("Data found successfully: " + data);
		},
		error: function(error)
		{
			alert("An error occurred finding the data: " + error["status"] + " error");
		}
		
	});
}

function draw(pin) 
{
	  canvas = document.getElementById('boardCanvas');
	  ctx = canvas.getContext('2d');
	  var img = new Image();
	  img.onload = function(){
		  ctx.drawImage(img,parseInt(pin[0]['x']),parseInt(pin[0]['y']),200,200);
	  };
	  img.src = pin[0]['imgUrl'];
	  img.width = 200;
	  img.height = 200;
	  images.push(img);
}

function checkImage(e)
{
	$.each(images,function(index,value)
	{
		console.log(value);
		var mouseX = e.pageX - $(e.target).offset().left;
		var mouseY = e.pageY - $(e.target).offset().top;
		var maxPositionX = pins[index]['x'] +$(this)[0].width;
		var maxPositionY = pins[index]['y'] +$(this)[0].height;
		if (pins[index]['x']<mouseX && maxPositionX>mouseX && pins[index]['y']<mouseY && maxPositionY>mouseY)
		{
			isDragging = true;
			startMouseX = mouseX;
			startMouseY = mouseY;
			currentImage = $(this);
			imageIndex = index;
			return;
		}
	});
			
}

function clearCanvas()
{
	ctx.clearRect(0,0,canvas.width,canvas.height);
}

function imageMoving(e)
{
	if (isDragging)
	{
		var mouseX = e.pageX - $(e.target).offset().left;
		var mouseY = e.pageY - $(e.target).offset().top;
		
		var newXLocation = parseInt(pins[imageIndex]['x']) + mouseX - startMouseX;
		var newYLocation = parseInt(pins[imageIndex]['y']) + mouseY - startMouseY;
		
		console.log(pins[imageIndex]['x'] + " " + mouseX + " " + startMouseX + " " + (pins[imageIndex]['x'] + mouseX - startMouseX) + " " + newYLocation);
		if (newXLocation>0 && newXLocation <canvas.width -currentImage[0].width)
			pins[imageIndex]['x'] = newXLocation;
		if (newYLocation>0 && newYLocation <canvas.height -currentImage[0].height)
			pins[imageIndex]['y'] = newYLocation;

		startMouseX = mouseX;
		startMouseY = mouseY;
		clearCanvas();
		updateView();
	}
	
}

function mouseReleased()
{
	savePostion();
	isDragging = false;
	currentImage = null;
}

function savePostion()
{
	console.log(pins[imageIndex]["x"]);
	$.ajax(url,
	{
		type:"POST",
		data: 
		{
			"method":"UpdatePinLocation",
			"pinID":parseInt(pins[imageIndex]["id"]),
			"x":parseInt(pins[imageIndex]["x"]),
			"y":parseInt(pins[imageIndex]["y"])
		},
		success: function(data)
		{
			console.log("Position updated!");
		},
		error: function(error)
		{
			alert("An error occurred finding the data: " + error["status"] + " error");
		}
				
	});
}


$(document).ready(function(){
	getContent();
	if (isEditable)
	{
		$("#boardCanvas").on("mousedown",checkImage);
		$("#boardCanvas").on("mousemove",imageMoving);
		$("body").on("mouseup",mouseReleased);
	}
	else
	{
	}


});