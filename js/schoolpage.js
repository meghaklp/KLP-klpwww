var info;
var map;
var type;
var image={"school":"school.png","preschool":"preschool.png"}

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

function getName(name)
{
  tname=name.split(" ");
  retname="";
  first=1;
  for( entry in tname)
  {
    if(first==1)
    {
      first=0;
      retname=tname[entry].toUpperCase();
    }
    else
    {
      if(tname[entry].length <= 3)
      {
        retname=retname+" "+tname[entry].toUpperCase();
      }
      else
      {
        retname=retname+" "+initCap(tname[entry])
      }
    }
 
  }
  return retname;
}


function initialise(data)
{
  info=data;
  info["name"]=info["name"].toUpperCase();
  if (info["type"]==2)
  {
    type="preschool";
    document.getElementById("school_info_heading").innerHTML = "Preschool Information";
    document.getElementById("school_visits_heading").innerHTML = "Preschool Visits";
    document.title = "Preschool Information";
  }
  else
  {
    type="school";
    document.getElementById("school_info_heading").innerHTML = "School Information";
    document.getElementById("school_visits_heading").innerHTML = "School Visits";
    document.title = "School Information";
  }

  document.getElementById("student_info_heading").innerHTML = "Student Information";
  var latlng = new google.maps.LatLng(info["lat"],info["lon"]);
  var myOptions = {
      zoom: 14,
      center: latlng,
      mapTypeId: google.maps.MapTypeId.ROADMAP,
      disableDoubleClickZoom:false
  };
  map = new google.maps.Map(document.getElementById("map"),myOptions);
  var marker = new google.maps.Marker({
        position: latlng,
        title:info["name"],
        icon:"/images/"+image[type]
      });
                  
  marker.setMap(map);  
  
  document.getElementById("school_name").innerHTML= info["name"];
  address='<table id="infotable" class=\"table1\">' +
                        '<tbody><tr>'; 
  if (info["address"] != "-")
  {
        address=address+'<th scope="row">District</th>' +
                            '<td>:   '+info["b"]+'</td>' +
                        '</tr><tr>' 
        if(info["type"] != 2)
        {
          address = address + '<th scope="row">Block</th>' 
        }else{
          address = address + '<th scope="row">Project</th>' 
        }
        address = address + '<td>:   '+info["b1"]+'</td>' +
                        '</tr><tr>' 
        if(info["type"] != 2)
        {
          address = address + '<th scope="row">Cluster</th>' 
        }else{
          address = address + '<th scope="row">Circle</th>' 
        }
        address = address + '<td>:   '+info["b2"]+'</td>' +
                        '</tr><tr>' +
                            '<th scope="row">Address</th>' +
                            '<td>:   '+info["address"]+ "-" + info["postcode"]+'</td>' +
                        '</tr><tr>' +
                            '<th scope="row">Landmarks</th>' +
                            '<td>:   '+info["landmark_1"]+ ", " + info["landmark_2"]+'</td>' +
                        '</tr><tr>' +
                            '<th scope="row">Identifiers</th>' +
                            '<td>:   '+info["inst_id_1"]+ ", " + info["inst_id_2"]+'</td>' +
                        '</tr><tr>' +
                            '<th scope="row">Buses</th>' +
                            '<td>:   '+info["bus_no"]+'</td>';
  }else{
        address=address+'<th scope="row">Address</th>' +
                            '<td>:   '+info["address"]+'</td>';
  }
        address=address+'</tr></tbody></table>';
        document.getElementById("school_geo").innerHTML= address;


        infotable='<table id="infotable" class=\"table1\">' +
                        '<tbody><tr>' +
                            '<th scope="row">Category</th>' +
                            '<td>:   '+info["cat"]+'</td>'
                  if(info["type"] !=2)
                  {
                        infotable = infotable + '</tr><tr>' +
                            '<th scope="row">Gender</th>' +
                            '<td>:   '+info["sex"]+'</td>' +
                            '</tr><tr>' +
                            '<th scope="row">Medium Of Instruction</th>' +
                            '<td>:   '+info["moi"]+'</td>' 
                        /*'</tr><tr>' +
                            '<th scope="row">Dise Code</th>' +
                            '<td>:   '+info["dise_code"]+'</td>' */
                  }
                  infotable = infotable + '</tr></tbody></table>'
	    document.getElementById("school_info").innerHTML= infotable;
      studentinfo='<img src=\"http://chart.apis.google.com/chart'+
                        '?chf=bg,s,67676704'+
                        '&chs=300x225'+
                        '&cht=p'+
                        '&chco=EFB136|B56F1C|67676704'+
                        '&chdl=No.+of+Boys: '+info["numBoys"]+' ('+ Math.round(info["numBoys"]/info["numStudents"]*100)+'%)' +
                                '|No.+of+Girls: '+ info["numGirls"] +' ('+ Math.round(info["numGirls"]/info["numStudents"]*100)+'%)' + 
                                '|Total: '+info["numStudents"]+
                        '&chd=t:'+ info["numBoys"]+','+ info["numGirls"]+'\"'+ 
                        'width=\"300\" height=\"225\"/>'
	    document.getElementById("student_info").innerHTML= studentinfo;


  infotable='<br/>'+'<table id="systable" class=\"table1\">'+
          	'<tbody><tr><th scope="row">No. of Visits:</th><td>'+info["syscount"]+'</td></tr>';
            if( info["syscount"]>0)
            {
              infotable=infotable+'<tr><th scope="col" colspan=\"2\" align=\"center\">Dates of Visit</th></tr>';
              for(entry in info["sysdate"])
              {
                date = info["sysdate"][entry];
                if(date !="") 
                  infotable=infotable+'<tr><td colspan=\"2\" align=\"left\">'+date+'</td></tr>';
              }
            }
  infotable=infotable+'<tr><td colspan=\"2\" align=\"center\"><b><a href=\"javascript:void(0);\" onclick=window.open("../../shareyourstory'+type+'?type='+type+'?id='+info["id"]+'","mywindow")>Share your Experience</a></b></td></tr></tbody></table>';
  document.getElementById("sys_info").innerHTML= infotable;

if(info["images"].length>0)
{
  school_pics= '<a rel=\"lightbox['+ info['id']+']\" href=\"' + info["image_dir"] + info["images"][0]+'\"><img class="album" src=\"' + info["image_dir"] + 
                info["images"][0]+'\"/>'
  for(i=1;i<info["images"].length;i++)
  {
    school_pics = school_pics+'<a rel=\"lightbox['+ info['id']+']\" href=\"' + info["image_dir"] + info["images"][i] +'\"></a>' 
  }
}else{
  school_pics='This school does not have a picture album yet.<br/><br/>'
}
  document.getElementById("school_pics").innerHTML=school_pics;
 
  tweet='<iframe allowtransparency=\"true\" frameborder=\"0\" scrolling=\"no\" src=\"http://platform.twitter.com/widgets/tweet_button.html?url=' + document.location.href + '&text='+ 'I visited ' + info["name"] +' and shared my story. More on the school here:' +'\" style=\"vertical-align:top; width:130px; height:50px;\"></iframe>'

  fb_like='<iframe src=\"http://www.facebook.com/plugins/like.php?href='+ document.location.href + '&amp;layout=standard&amp;show_faces=true&amp;width=350&amp;action=like&amp;colorscheme=light&amp;height=80\" scrolling=\"no\" frameborder=\"0\" style=\"vertical-align:top; border:none; overflow:hidden; width:350px; height:80px;\" allowTransparency=\"true\"></iframe>'

  document.getElementById("sharing").innerHTML = tweet + fb_like;
}

