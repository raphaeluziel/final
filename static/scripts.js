var url = "https://api.nasa.gov/planetary/apod?api_key=vIYFQTalk1kgo3J9YlgHDuSSZSTOJsjKkoqiRxuT";
var d = new Date();
d.setMonth(d.getMonth() + 1);
var date = d.getFullYear() + "-" + d.getMonth() + "-" + d.getDate();
url += "&date=" + date;

var quotetosubmit = "";

// Execute when the DOM is fully loaded
$(document).ready(function() {

  document.getElementById("setDate").innerHTML = date;
  document.getElementById("setDateBtn").addEventListener("click", changeUrlDate);


  function getPhoto(){
      $.ajax({
          url: url,
          success: function(result){
            if("copyright" in result) {
              $("#copyright").text("Image Credits: " + result.copyright);
            }
            else {
              $("#copyright").text("Image Credits: " + "Public Domain");
            }

            if(result.media_type == "video") {
              $("#apod_img_id").css("display", "none");
              $("#apod_vid_id").attr("src", result.url);
            }
            else {
              $("#apod_vid_id").css("display", "none");
              $("#apod_img_id").attr("src", result.url);
            }

          $("#reqObject").text(url);
          $("#apod_explaination").text(result.explanation);
          $("#apod_title").text(result.title);

          $("#picture_link").attr("href", result.url);

          $("#image_link").attr("value", result.url);
          $("#image_title").attr("value", result.title);
        }
      });
  }

  getPhoto();

  function changeUrlDate(){
    date = document.getElementById("setDate").value;
    document.getElementById("fromDate").innerHTML = date;
    url = "https://api.nasa.gov/planetary/apod?api_key=vIYFQTalk1kgo3J9YlgHDuSSZSTOJsjKkoqiRxuT&date=";
    url += date;
    getPhoto();
  }

  // Twitter javascript template
  window.twttr = (function(d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0],
    t = window.twttr || {};
  if (d.getElementById(id)) return t;
  js = d.createElement(s);
  js.id = id;
  js.src = "https://platform.twitter.com/widgets.js";
  fjs.parentNode.insertBefore(js, fjs);
  t._e = [];
  t.ready = function(f) {
    t._e.push(f);
  };
  return t;
  }(document, "script", "twitter-wjs"));

  quotetosubmit = document.getElementById("what_to_tweet").innerHTML;

  $("#twitterButton").attr("data-text", quotetosubmit);

});
