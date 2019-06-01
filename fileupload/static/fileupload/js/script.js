// Generate 32 char random uuid
function gen_uuid() {
    var uuid = ""
    for (var i=0; i < 32; i++) {
        uuid += Math.floor(Math.random() * 16).toString(16);
    }
    return uuid
}

$(function()
{
  var $loader = $('#loader');
  // $loader.hide();
  var $progress = $("<div id='upload-progress' class='upload-progress'><div class='box'><p>Uploading ...</p><div class='progress-container'><div class='progress-bar'><span class='progress-info'></span></div></div></div></div></div>").appendTo('#loader');
  $progress.hide();
    // $('form[@enctype=multipart/form-data]').submit(function(){
  $('form').submit(function()
  {
    // debugger
    // alert("form submitted");
    // Prevent multiple submits
    if ($.data(this, 'submitted')) return false;

    var freq = 1000; // freqency of update in ms
    var uuid = gen_uuid(); // id for this upload so we can fetch progress info.
    // var progress_url = '/admin/upload_progress/'; // ajax view serving progress info
    var progress_url = '/admin/upload_progress/'; // ajax view serving progress info

    // Append X-Progress-ID uuid form action
    this.action += (this.action.indexOf('?') == -1 ? '?' : '&') + 'X-Progress-ID=' + uuid;

    // var $progress = $('<div id="upload-progress" class="upload-progress"></div>').
        // appendTo(document.body).append('<div class="progress-container"><span class="progress-info">uploading 0%</span><div class="progress-bar"></div></div>');

        var $loader = $('#loader');
        $($loader).removeClass("hide");

        var $progress = $("<div id='upload-progress' class='upload-progress'><div class='box'><p>Uploading ...</p><div class='progress-container'><div class='progress-bar'><span class='progress-info'></span></div></div></div></div></div>").appendTo('#loader');
        $progress.hide();
    // var $progress = $('.overlay')

    // progress bar position
    // $progress.show();

    // var $progress_bar = $progress.find('.progress-bar');
    // var $progress_info = $progress.find('.progress-bar');
    //
    // $progress_bar.css({
    //     border: '1px solid green'
    // });
    //
    // $progress_info.css({
    //     'font-size': '32px'
    // });

    // Update progress bar
    function update_progress_info()
    {
        // $progress.show();

      $.getJSON(progress_url, {'X-Progress-ID': uuid})
      .done(function(data, status)
      {
        // debugger;
        // alert('getJSON request succeeded! DATA : ' + data + " | Status : " + status);
        console.log("ResponseStatus:" + status)
          if (data)
          {

            if(parseInt(data.uploaded) > 0 && parseInt(data.abort)==0 )
            {

              var $progress = $('#upload-progress')
              $progress.show();

              // debugger
              var progress = parseInt(data.uploaded) / parseInt(data.length);

              var sizeInMB = (parseInt(data.length) / (1024*1024)).toFixed(2);
              // alert(sizeInMB + 'MB')

              if(sizeInMB>2000) // 2 GB
                freq = 240000; // 4 min
              else if(sizeInMB>1000) // 1 GB
                freq = 180000 ;// 3 min
              else if(sizeInMB>500) // 0.5 GB
                freq = 120000; // 2 min
              else if(sizeInMB>200) // 200 MB
                freq = 60000; // 1 min
              else if(sizeInMB>10) // 10 mb
                freq = 5000 ;// 5 sec
              else if(sizeInMB>5) // 5 mb
                freq = 3000; // 3 sec

              // alert("freq: " + freq);

              // alert("data.uploaded : " + data.uploaded + " data.length : " + data.length);

              var uploaded_status = $('#uploaded_status').text(parseInt(progress*100) + '%');

              var width = $('.progress-container').width()
              var progress_percentage = parseInt(100 * progress)+ '%';
              // $('.progress-bar').css('width':progress_percentage);
              $('.progress-bar').width(progress_percentage);
              $('.progress-info').text(progress_percentage);
            }
            }
            else {
              $progress.hide();
            }

          if(parseInt(data.abort)==0 )
            window.setTimeout(update_progress_info, freq);
          else {
              var $progress = $('#upload-progress')
              $progress.hide();
              var $loader = $('#loader');
              // $loader.hide();
              $($loader).addClass("hide");
              var error = $('.form').children('h5').eq(1)
              $(error).text("Uploading Canceled!")

          }
      })
      .fail(function(jqXHR, textStatus, errorThrown)
      {
        console.log("error " + textStatus);
        console.log("incoming Text " + jqXHR.responseText);
        alert("incoming Text " + jqXHR.responseText + ". Text Status : " + textStatus + ". errorThrown : " + errorThrown);
        var $progress = $('.overlay')
        $progress.hide();
        var $loader = $('#loader');
        //$loader.hide();
        $($loader).addClass("hide");
        var error = $('.form').children('h5').eq(1)
        $(error).text("Uploading Failed!")
      })
      .always(function()
      {
        console.log( "complete" );
      });
    }

    window.setTimeout(update_progress_info, freq);
    $.data(this, 'submitted', true); // mark form as submitted.

  });
});
