
/*=============================================================
    Authour URI: www.binarycart.com
    Version: 1.1
    License: MIT
    
    http://opensource.org/licenses/MIT

    100% To use For Personal And Commercial Use.
   
    ========================================================  */

(function ($) {
    "use strict";
    var mainApp = {

        main_fun: function () {
            /*====================================
            METIS MENU 
            ======================================*/
            $('#main-menu').metisMenu();

            /*====================================
              LOAD APPROPRIATE MENU BAR
           ======================================*/
            $(window).bind("load resize", function () {
                if ($(this).width() < 768) {
                    $('div.sidebar-collapse').addClass('collapse')
                } else {
                    $('div.sidebar-collapse').removeClass('collapse')
                }
            });

            /*====================================
            MORRIS BAR CHART
         ======================================*/

            /*====================================
          MORRIS DONUT CHART
       ======================================*/

            /*====================================
         MORRIS AREA CHART
      ======================================*/

            /*====================================
    MORRIS LINE CHART
 ======================================*/
     
        },

        initialization: function () {
            mainApp.main_fun();

        }

    };
    // Initializing ///

    $(document).ready(function () {
        mainApp.main_fun();
    });

}(jQuery));

formerUploadHtml = 0;

$('#menu-upload').click(function(){
    if (formerUploadHtml == 0) {
        formerUploadHtml = $('#uploadModal').html();
    } else {
        $('#uploadModal').html(formerUploadHtml);
    }
   $('#uploadModal').modal();
});

/* UPLOAD BUTTON */
$(document).on("click", ".send-upload", function(){

    // Getting our weapons.
    var uploadModal = $('#uploadModal');
    var uploadForm = uploadModal.find('#upload-form');
    var responseDiv = $('#upload-response');
    var uploadButton = $(this);
    var modalTitle = $('#uploadModalLabel');
    var formData = new FormData(uploadForm);
    var modalFooter = uploadModal.find('.modal-footer');

    $.ajax({
        url: '/upload',  //Server script to process data
        type: 'POST',
        //Ajax events
        beforeSend: function(){
            uploadButton.html('Uploading file...');
        },
        success: function(){
            uploadButton.html('File uploaded successfully.');
        },
        error: function(e){
            responseDiv.html('<p class="ajax-modal-response bg-danger">Failed to upload... ' +
            '<br>This is not expected but hopefully you are already the admin.<br> ' +
            'Shame on you!</p>');
            console.log('Failed to upload... response object is bellow: ');
            console.log(e);
        },
        complete: function(e){
            // Resetting the form state.
            responseDiv.removeClass('hidden');
            uploadForm.addClass('hidden');
            modalTitle.html('Server Response: ' + e.status);
            modalFooter.html('<button type="button" class="btn btn-default" data-dismiss="modal">' +
            '<i class="fa fa-sign-out"></i>Close</button>')
        },
        // Form data
        data: formData,
        //Options to tell jQuery not to process data or worry about content-type.
        cache: false,
        contentType: false,
        processData: false
    });
});
