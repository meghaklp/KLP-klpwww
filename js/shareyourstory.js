var schoolid;
var handle;
var cal1;
var typeform="schoolform";
var type;

function initCap(str)
{
  str = str.substring(0,1).toUpperCase() + str.substring(1,str.length).toLowerCase();
 return str;
}


function isNumeric(str)
{
  if (!(/^\d*$/.test(str.value)))
  {
    alert(str.id+" should only be numeric");
    str.value="";
    str.focus();
    return false;
  }
  return true;
}


function initialise()
{
   var query= window.location.search.substring(1);
   var variables = query.split("?");
   type=variables[0].split("=")[1];
   schoolid=variables[1].split("=")[1];
   document.schoolform.action ="/postSYS/"+type
   initializeData();
   getSchoolInfo();
   initializeDate();
   document.getElementById("schoolid").value = schoolid;
}

function initializeData()
{
  document.getElementById("toppara").innerHTML='<p>Please fill in this form using the data you have collected from your '+type+' visit.If you have any trouble, please call us at +91 80 25429726 or email us at team@klp.org.in </p>';
  document.getElementById("formtoppara").innerHTML='The '+type+' you have visited should be displayed below. If not, please select the correct '+type+' from the map and then click Share Your Story.';
  document.getElementById("forminfoheading").innerHTML='<b>'+initCap(type)+' Information:</b>';
  document.getElementById("dateofvisittext").innerHTML='<i>[Mandatory. Please tell us when you visited the '+type+'.]</i>';
  document.getElementById("feedbackheading").innerHTML='<i>Please enter as much information here as you have collected from your '+type+' visit.</i>';
  document.getElementById("commentheading").innerHTML=' <i>Please use this space to give us your comments and feedback on the experience and the '+type+' you visited.</i>';
}


function initializeDate()
{
  YUI({insertBefore: 'styleoverrides', groups: { yui2: { combine: true, base: 'http://yui.yahooapis.com/2.8.0r4/build/', comboBase: 'http://yui.yahooapis.com/combo?', root: '2.8.0r4/build/', modules:  { yui2_yde: { path: 'yahoo-dom-event/yahoo-dom-event.js' }, yui2_calendar: { path: 'calendar/calendar-min.js', requires: ['yui2_yde', 'yui2_calendarcss'] }, yui2_calendarcss: { path: 'calendar/assets/skins/sam/calendar.css', type: 'css' } } } }}).use('node', function(Y, result) {
 
    // The callback supplied to use() will be executed regardless of
    // whether the operation was successful or not.  The second parameter
    // is a result object that has the status of the operation.  We can
    // use this to try to recover from failures or timeouts.
    if (!result.success) {
 
        Y.log('Load failure: ' + result.msg, 'warn', 'Example');
 
    } else {
              // Add a button click listener to load the calendar
        handle = Y.on('click', function(e) {
 
            // dynamically load the 2.x calendar and 3.x drag and drop
            Y.use('yui2_calendar', function(Y) {
                cal1 = new YAHOO.widget.Calendar('cal1','cal1Cont');
                cal1.show()
                cal1.render();
                cal1.selectEvent.subscribe(handleCal1Select,cal1,this);
            });
      
        }, '#dateofvisit');
        
    }
 
});
}


function handleCal1Select(type,args,obj) {
  cal1.hide();
  var dates = args[0];
  var date = dates[0];
  var year = date[0], month = date[1], day = date[2];
  var txtDate1 = document.getElementById("dateofvisit");
  txtDate1.value = day + "-" + month + "-" + year;
}

function getSchoolInfo()
{
  YUI({base: 'yui/build/',
    timeout: 10000}).use("io-base","json-parse",
      function(Y, result) {
        if (!result.success) {
          Y.log('Load failure: ' + result.msg, 'warn', 'program');
        }
        var callback = {
          on: { success:
            function(id, o) {
              var info;
              try {
                info= Y.JSON.parse(o.responseText);
              } catch (e) {
                Y.log('Could not parse json', 'error', 'info');
                return;
              }
              populateInfo(info);
            },
            failure: function(id, o) {
               Y.log('Could not retrieve data ','error','info');
            } 
          }
        };
        url = "schoolInfo/"+schoolid;
        var request = Y.io(url, callback);
       });
}

function populateInfo(info)
{
    if(info.type==1)
    {
      document.getElementById("schoolInfo").innerHTML= '<table id=\"schoolInfo\" border=1 width="30%"><tr><td><b>State</b></td><td>Karnataka</td></tr><tr><td><b>District</b></td><td>'+info.district+'</td></tr><tr><td><b>Block</b></td><td>'+info.block+'</td></tr><tr><td><b>Cluster</b></td><td>'+info.cluster+'</td></tr><tr><td><b>School Name</b></td><td>'+info.schoolname+'</td></tr></table>';
    }
    else
    {
      document.getElementById("schoolInfo").innerHTML= '<table id=\"schoolInfo\" border=1 width="30%"><tr><td><b>State</b></td><td>Karnataka</td></tr><tr><td><b>District</b></td><td>'+info.district+'</td></tr><tr><td><b>Project</b></td><td>'+info.block+'</td></tr><tr><td><b>Circle</b></td><td>'+info.cluster+'</td></tr><tr><td><b>Preschool Name</b></td><td>'+info.schoolname+'</td></tr></table>';
    }
}


function submitData()
{
  var columnValues = [];
  var info = document.forms[typeform];
  var filled=0;
  for (num in info.elements )
  {
    var element = info.elements[num];
    if(element.id != "schoolid")
    {
      if( element.type == "text" || element.type=="textarea")
      {
        if( element.value != "" )
        {
          filled=1;
        }
      }
      else if( element.type =="radio")
      {
        if(element.checked)
        {
          filled=1;
        }
      }
    }
  }
  if( filled == 0)
  {
    alert("Please enter some data before submitting");
    return false;
  }
  else
  {
    return true;
  }
}


function postData()
{
  var form = document.createElement("form");
  form=document.forms['story'];
  form.setAttribute("method", "post");
  form.setAttribute("action", "/postSYS/"+schoolType);
  var result = form.submit();
}
