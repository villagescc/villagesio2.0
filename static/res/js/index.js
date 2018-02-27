$(document).ready(function() {
    let person = new Person();
    // person.getPerson();

  // smooth scrolling
    $("a").click(function(event) {
      if (this.hash !== "") {
       event.preventDefault();
       let linkOffset = 0;
       $("html, body").animate({
         scrollTop: $(this.hash).offset().top - $(".navbar").height() + linkOffset
       }, 600);
      }
    });

    let diffToBottom = 200;

    $('#main').scrollWait(function(){
        let main = $('#main');
        let scrollValue = document.getElementById("main").scrollHeight;
        let django_objects_scroll_offset = document.getElementById("django_scroll_offset").getAttribute("data-offset");
        if (scrollValue < (main.scrollTop() + main.height() + diffToBottom)){
            person.getPerson(django_objects_scroll_offset);
        }
    }, 150);
});

$.fn.scrollWait = function(callback, timeout) {
  $(this).scroll(function(){
    var element = $(this);
    if (element.data('scrollTimeout')) {
      clearTimeout(element.data('scrollTimeout'));
    }
    element.data('scrollTimeout', setTimeout(callback,timeout));
  });
};
