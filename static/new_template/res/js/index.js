$(document).ready(function() {

  // smooth scrolling
    $("a").click(function(event) {
      if (this.hash !== "") {
       event.preventDefault();
       var linkOffset = 0;
       $("html, body").animate({
         scrollTop: $(this.hash).offset().top - $(".navbar").height() + linkOffset
       }, 600);
      }
    });

});
