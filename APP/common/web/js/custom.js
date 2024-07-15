
$( document ).ready(function() {
 $('body').on('click', '.funFactClosebtn', function(e){
   $("#funFactWrapper").removeClass("top-0");
   if ($(window).width() < 992) {
      if ($("#funFactWrapper").hasClass("top-350")) {
        $('.funFactbtn').show();
      } else {
        $('.funFactbtn').hide();
      }
  }
   if ($("#funFactWrapper").hasClass("top-350")) {
     $("#funFactWrapper").addClass("top-0").removeClass("top-350");
     $(".funFactbtn").css("bottom","10px")
     $(".iconUp").removeClass("mdi-chevron-double-down").addClass("mdi-chevron-double-up");
   
   } else {
     $("#funFactWrapper").addClass("top-350")
     $("#funFactWrapper").removeClass("top-0")
     $(".funFactbtn").css("bottom","240px")
     $(".iconUp").addClass("mdi-chevron-double-down").removeClass("mdi-chevron-double-up"); 
   }

 });
});

$('.indicator').on('click', function(e){
e.preventDefault()
if ($("#mapFilterData").hasClass("right-0")) {
 $("#mapFilterData").removeClass('right-0');
 $(".ind-noti").text('1');
} else {
 $("#mapFilterData").addClass('right-0');
 $(".ind-noti").text('0');
}
})




$(window).resize(function() {
    if ($(window).width() > 576) {
        $(".btnWrapper").fadeIn(600);
    } else {
        $(".btnWrapper").fadeOut(600);
    }
});


let nav = document.getElementById('resmenu_wrapper');
function toggleMenu() {
  nav.classList.toggle('resmenu-visible');
}