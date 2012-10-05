var websiteURL = "http://tsmith14-pinboard.appspot.com";
images = document.getElementsByTagName("img");
var newContent = "<div style='padding:20px;'><h1 style='font-size:30px;'>Pin It</h1>";
newContent+='<h4 style="font-size:16px;">Enter a caption and hit "Create Pin" to create a new pin.</h4>';
newContent+= "<div class='content'>";
var srcs = new Array();
for (image in images)
{
	if (image != "length" || image != "item")
	{
		var src = images[image].src;
		if (src == "undefined")
			console.log("UNDEFINDED "+src+image)
		if (src!==undefined && srcs.indexOf(src)==-1)
		{
			newContent+="<div class='imageContainer' style='display:inline; float:left; margin:20px; text-align:center; width:400px; border: solid #24687F 3px'>";
			newContent+="<form action='"+websiteURL+"/pin' method='POST'>"
			newContent+="<div><img src='"+src+"' style='min-width:100px; max-width:400px;'><input name='imageUrl' value='"+src+"' type='hidden'></input></div>"; 
			newContent+="<div><label for='caption'>Caption: </label><input name='caption' type='text' style=''></input></div>";
			newContent+="<div><label for='private'>Private: </label>";
				newContent+="<select name='private' style='width:200px;'>";
					newContent+="<option value='1'>Private</option>";
					newContent+="<option value='0'>Public</option>"; 
				newContent+="</select>";
			newContent+="</div>";  
			newContent+="<div><input type='submit' value='Create Pin' style='width:50%; margin-top:10px; margin-bottom:10px;' class='fancyButton submitButton'></div>";
			newContent+="</form>";
			newContent+="</div>";
			srcs.push(src);
		}
	}
}
newContent+= "</div>";

document.getElementsByTagName('head')[0].innerHTML = '<link rel="stylesheet" href="'+websiteURL+'/css/style.css" type="text/css">';

document.body.removeAttribute("style");
document.body.backgroundColor = "white";
document.body.innerHTML= newContent;