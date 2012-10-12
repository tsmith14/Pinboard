/** pinAjax.js 
 * Created by Tyler Smith, 10/11/12
 */


function privateValueChanged(e)
{
	console.log($(this).val());
    var script_tag = document.getElementById('ajaxScript');
	var url = script_tag.getAttribute("data-url");
	$.ajax(url,
	{
		type:"POST",
		data:{
			private: $(this).val()
		},
		success: function(data)
		{
			console.log("Data save successfully: " + data);
		},
		error: function(error)
		{
			alert("An error occurred saving the data: " + error);
		}
		
	});
}

function isEditingCaption()
{
	$("#caption").hide();
	$("#caption-edit").show().focus();
}

function keyPressedOnCaptionEdit(e)
{
	 var code = (e.keyCode ? e.keyCode : e.which);
	 if(code == 13) 
	 { 
	     $("#caption").val($("#caption-edit").val());
	     $("#caption").text($("#caption-edit").val());
	     $("#caption-edit").hide();
	     $("#caption").show();
		 saveCaption();
	 }
}

function saveCaption()
{
    var script_tag = document.getElementById('ajaxScript');
	var url = script_tag.getAttribute("data-url");
	$.ajax(url,
	{
		type:"POST",
		data:{
			caption: $("#caption").val()
		},
		success: function(data)
		{
			console.log("Data save successfully: " + data);
		},
		error: function(error)
		{
			alert("An error occurred saving the data: " + error);
		}
		
	});
}



$(document).ready(function(){
	$("#private").on("change",privateValueChanged);
	$("#caption").on("click", isEditingCaption);
	$("#caption-edit").unbind('keypress');
	$("#caption-edit").bind("keyup",keyPressedOnCaptionEdit);
	
});