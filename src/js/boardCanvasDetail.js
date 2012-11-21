// BoardCanvasDetail.js -- Tyler Smith -- 10/31/12

var pins; 

var script_tag = document.getElementById('ajaxScript');
var url = script_tag.getAttribute("data-url");
var isEditable = (script_tag.getAttribute("data-editable")=="True")?true:false;

var isDragging = false;
var isResizing = false;

var startMousePosition;
var currentImage;
var imageIndex;
var canvas;
var ctx;
var dotRadius = 10;
var dotIndex = 0;

function Vector(pointA,pointB) {
	this.pointA = pointA;
	this.pointB = pointB;
	this.deltaX = pointB.x-pointA.x,
	this.deltaY = pointB.y-pointA.y,
	this.add = function(vector){
		return new Vector(this.pointA,this.pointB.add(new Point(vector.deltaX,vector.deltaY)));
	},
	this.subtract = function(vector){
		return new Vector(this.pointA,this.pointB).add(vector.negate());
	},
	this.negate = function(vector){
		return new Vector(pointA,new Point(pointA.x-pointB.x,pointA.y-pointB.y));
	}
	
}

function Rectangle(topLeftPoint, bottomRightPoint)
{
	this.topLeftPoint = topLeftPoint ? topLeftPoint : new Point(),
	this.bottomRightPoint = bottomRightPoint ? bottomRightPoint : new Point(),	
	this.x = topLeftPoint.x ? topLeftPoint.x : 0,
	this.y = topLeftPoint.y ? topLeftPoint.y : 0,		
	this.width = this.bottomRightPoint.x-this.topLeftPoint.x,
	this.height = this.bottomRightPoint.y-this.topLeftPoint.y,
	this.topRightPoint = new Point(this.bottomRightPoint.x,this.topLeftPoint.y),
	this.bottomLeftPoint = new Point(this.topLeftPoint.x,this.bottomRightPoint.y)
	this.contains = function(point){
		console.log("CONTAINS:");
		console.log(this);
		console.log(point);
		console.log('*****');
		if (this.x <= point.x && this.x+this.width >= point.x && this.y <= point.y && this.y+this.height >= point.y)
		{
			console.log("CONTAINS TRUE");
			return true;
		}
		else
		{
			console.log("CONTAINS FALSE");
			return false;
		}
	}
}

function Point (x,y)
{
	this.x = parseInt(x) ? parseInt(x) : 0,
	this.y = parseInt(y) ? parseInt(y) : 0,
	this.add = function(point){
		return new Point(this.x+point.x,this.y+point.y);
	},
	this.subtract = function(point){
		return new Point(this.x-point.x,this.y-point.y);
	},
	this.addVector = function(vector){
		return new Point(this.x+vector.deltaX,this.y+vector.deltaY);
	},
	this.subtractVector = function(vector){
		return new Point(this.x-vector.deltaX,this.y-vector.deltaY);
	}
}


function updateView()
{
	clearCanvas();
	$.each(pins,function(index,pin){
//		console.log(pin);
		ctx.drawImage(pin.image,parseInt(pin['x']),parseInt(pin['y']),pin.image.width,pin.image.height);
		if (index == imageIndex)
		{
			  var centerX = parseInt(pin['x']);
		      var centerY = parseInt(pin['y']);
		     
		      drawDot(new Point(parseInt(pin['x']),parseInt(pin['y'])));
		      drawDot(new Point(parseInt(pin['x'])+pin.image.width,parseInt(pin['y'])));
		      drawDot(new Point(parseInt(pin['x']),parseInt(pin['y'])+pin.image.height));
		      drawDot(new Point(parseInt(pin['x'])+pin.image.width,parseInt(pin['y'])+pin.image.height));     
		}
	});
	
}

function drawDot(point)
{
	
     ctx.beginPath();
     ctx.arc(point.x, point.y, dotRadius, 0, 2 * Math.PI, false);
     ctx.fillStyle = 'green';
     ctx.fill();
     ctx.lineWidth = 2;
     ctx.strokeStyle = '#003300';
     ctx.stroke();
}


function createView()
{
	$.each(pins,function(index,pin){
		  var img = new Image();
		  img.onload = function(){
			  ctx.drawImage(img,parseInt(pin['x']),parseInt(pin['y']),parseInt(pin['width']),parseInt(pin['height']));
		  };
		  img.src = pin['imgUrl'];
		  img.width = parseInt(pin['width']);
		  img.height = parseInt(pin['height']);
		  pin.image = img;
		  console.log(pin);
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
			console.log(pins);
			createView();
			console.log("Data found successfully: " + data);
		},
		error: function(error)
		{
			alert("An error occurred finding the data: " + error["status"] + " error");
		}
		
	});
}

function checkImage(e)
{
	var imageFound = false;
	$.each(pins,function(index,pin)
	{
		var image = pin.image;

		var mousePosition = new Point(parseInt(e.pageX - $(e.target).offset().left),parseInt(e.pageY - $(e.target).offset().top));
		var imageBounds = new Rectangle(new Point(pin.x,pin.y),new Point(parseInt(pin.x) + parseInt(image.width), parseInt(pin.y) +parseInt(image.height)));

		var dotPoint = new Point(dotRadius,dotRadius);
		
		var outerBounds = new Rectangle(imageBounds.topLeftPoint.subtract(dotPoint),
										imageBounds.bottomRightPoint.add(dotPoint));

		if (outerBounds.contains(mousePosition))
		{
			var topLeftCircle     =  new Rectangle(imageBounds.topLeftPoint.subtract(dotPoint),
												   imageBounds.topLeftPoint.add(dotPoint));
			var topRightCircle    =  new Rectangle(imageBounds.topRightPoint.subtract(dotPoint),
					  						       imageBounds.topRightPoint.add(dotPoint));
			var bottomLeftCircle  =  new Rectangle(imageBounds.bottomLeftPoint.subtract(dotPoint),
					  							   imageBounds.bottomLeftPoint.add(dotPoint));
			var bottomRightCircle =  new Rectangle(imageBounds.bottomRightPoint.subtract(dotPoint),
					                               imageBounds.bottomRightPoint.add(dotPoint));
			
			if (topLeftCircle.contains(mousePosition))
			{
				isDragging = false;
				isResizing = true;
				imageFound = true;
				dotIndex = 1; 
			}
			else if (topRightCircle.contains(mousePosition))
			{
				isDragging = false;
				isResizing = true;
				imageFound = true;
				dotIndex = 2; 
			}
			else if (bottomLeftCircle.contains(mousePosition))
			{
				isDragging = false;
				isResizing = true;
				imageFound = true;
				dotIndex = 3; 
			}
			else if (bottomRightCircle.contains(mousePosition))
			{
				isDragging = false;
				isResizing = true;
				imageFound = true;
				dotIndex = 4; 
			}
			else if (imageBounds.contains(mousePosition))
			{
				isResizing = false;
				isDragging = true;
				imageFound = true;
				dotIndex = 0;
			}
			else
			{
				//Mouse in blank space
			}
			if (imageFound)
			{
				startMousePosition = mousePosition;
				currentImage = image;
				imageIndex = index;
				return;
			}

		}
	});
	
	if (!imageFound)
	{
		imageIndex = null;
		updateView();
	}			
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
		var mousePosition = new Point(mouseX,mouseY);
		
		var newLocation = new Point(parseInt(pins[imageIndex]['x']),parseInt(pins[imageIndex]['y'])).add(mousePosition).subtract(startMousePosition);

//		if (newLocation.x>0 && newLocation.x <canvas.width -currentImage.width)
			pins[imageIndex]['x'] = newLocation.x;
//		if (newLocation.y>0 && newLocation.y <canvas.height -currentImage.height)
			pins[imageIndex]['y'] = newLocation.y;

		startMousePosition = mousePosition;

		updateView();
	}
	else if (isResizing)
	{
		var mousePosition = new Point(e.pageX - $(e.target).offset().left, e.pageY - $(e.target).offset().top);
		var imagePosition = new Point(pins[imageIndex]['x'],pins[imageIndex]['y']);
		var imageSize = new Point(pins[imageIndex]['image']['width'],pins[imageIndex]['image']['height']);
		var newLocation;
		var newSize;
		if (dotIndex == 1)
		{
			var mouseVector = new Vector(startMousePosition,mousePosition);
			
			newLocation = imagePosition.addVector(mouseVector);
			newSize = imageSize.subtractVector(mouseVector);
		}
		else if (dotIndex == 2)
		{
			var mouseVector = new Vector(startMousePosition,mousePosition);

			newLocation = imagePosition.add(new Point(0,mouseVector.deltaY));	
			newSize = imageSize.add(new Point(mouseVector.deltaX,-mouseVector.deltaY));
		}
		else if (dotIndex == 3)
		{
			var mouseVector = new Vector(startMousePosition,mousePosition);

			newLocation = imagePosition.add(new Point(mouseVector.deltaX,0));	
			newSize = imageSize.add(new Point(-mouseVector.deltaX,mouseVector.deltaY));
		}
		else if (dotIndex == 4)
		{
			var mouseVector = new Vector(startMousePosition,mousePosition);

			newLocation = imagePosition.add(new Point(0,0));	
			newSize = imageSize.add(new Point(mouseVector.deltaX,mouseVector.deltaY));
		}
		else
		{
			
		}
		
		pins[imageIndex]['x'] = newLocation.x;
		pins[imageIndex]['y'] = newLocation.y;
		pins[imageIndex]['image']['width'] = newSize.x;
		pins[imageIndex]['image']['height'] = newSize.y;
		
		startMousePosition = mousePosition;
		updateView();
	}
		
}

function mouseReleased()
{
	if (isDragging)
	{
		savePostion();
		isDragging = false;
		currentImage = null;
	} 
	else if (isResizing)
	{
		savePostion();
		isResizing = false;
		currentImage = null;
		dotIndex = 0;
	}
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
			"y":parseInt(pins[imageIndex]["y"]),
			"width":parseInt(pins[imageIndex]["image"]["width"]),
			"height":parseInt(pins[imageIndex]["image"]["height"])
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
	canvas = document.getElementById('boardCanvas');
	ctx = canvas.getContext('2d');
	
	var v = new Vector(new Point(1,1),new Point(4,5));
	console.log(v.add(new Vector(new Point(1,2),new Point(4,2))));
	
});