// *----------------------------------------------------------*
// off-canvas-menu
// *----------------------------------------------------------*
$(function () {
  'use strict'

  $('.off-canvas-menu').on('click', function (e) {
    e.preventDefault();
    var target = $(this).attr('href');
    $(target).addClass('show');
  });


  $('.off-canvas .close').on('click', function (e) {
    e.preventDefault();
    $(this).closest('.off-canvas').removeClass('show');
  })

  $(document).on('click touchstart', function (e) {
    e.stopPropagation();
    if (!$(e.target).closest('.off-canvas-menu').length) {
      var offCanvas = $(e.target).closest('.off-canvas').length;
      if (!offCanvas) {
        $('.off-canvas.show').removeClass('show');
      }
    }
  });


});

// *----------------------------------------------------------*
// topFilterCollapse
// *----------------------------------------------------------*
$("#topFilterCollapse").on("click", function () {
  if ($("#collapseFilters").hasClass("show")) {
    $(".top-filter").removeClass("tops-0");

    $("#topFilterCollapse .ficon").removeClass('mdi-filter-off-outline tx-orange').addClass('mdi-filter-outline tx-primary');
  } else {
    $(".top-filter").addClass("tops-0");
    $("#topFilterCollapse .ficon").removeClass('mdi-filter-outline tx-primary').addClass('mdi-filter-off-outline tx-orange');
  }
});

// *----------------------------------------------------------*
// data-toggle="tooltip"
// *----------------------------------------------------------*
$('[data-toggle="tooltip"]').tooltip();


$('body').on('click', 'a[data-toggle="tab"]', function(e) {
      var target = e.currentTarget.id // activated tab
    if (target == "supply-tab"){
        $('#active-sellers-metrics-btn').trigger('click');
    } else if (target == "summary-tab"){
        $('#orders-metrics-btn').trigger('click');
    }else if(target == "logistics-tab"){
        $('#zonal-commerce-metrics-btn').trigger('click');
    }
});

// *----------------------------------------------------------*
// Text Truncate and tooltips
// *----------------------------------------------------------*

$.fn.tooltipOnOverflow = function (options) {
  $(this).on("mouseenter", function () {
    if (!window.jQuery.fn.tooltip) {
      console.error("Tooltip plugin is not loaded.");
      return;
    }

    if (this.offsetWidth < this.scrollWidth) {
      options = options || {
        placement: "auto"
      };

      try {
        $(this).tooltip("dispose");
      } catch (e) {
        console.error("Error disposing tooltip:", e);
      }

      options.title = $(this).text();
      $(this).tooltip(options);
      $(this).tooltip("show");
    } else {
      if ($(this).data("bs.tooltip")) {
        $(this).tooltip("hide").removeData("bs.tooltip");
      }
    }
  });
};


// *----------------------------------------------------------*
// expandContract
// *----------------------------------------------------------*  
  function expandContract() {
    $("#sidebarCollapse").on("click", function() {
      if ($(".searchbar").hasClass("expand")) {
        $(".searchbar").removeClass("expand");
        $(".searchbar .ficon").removeClass('mdi-filter-off-outline tx-orange').addClass('mdi-filter-outline tx-primary');
      } else{
        $(".searchbar").addClass("expand");
        $(".searchbar .ficon").removeClass('mdi-filter-outline tx-primary').addClass('mdi-filter-off-outline tx-orange');
      }
    });
  
};
  
// *----------------------------------------------------------*
// Sticky Menu on scroll
// *----------------------------------------------------------*  
var lastScrollTop = 0;
$(window).scroll(function() {
    var st = $(this).scrollTop();
    var windowHeight = $(window).height();
    var documentHeight = $(document).height();
    var bottomScrollPosition = documentHeight - windowHeight;

    if (st > lastScrollTop) {
      if ($(window).width() <= 576 && st < bottomScrollPosition) {
          $(".btnWrapper").fadeOut(600);
      }
    } else {

      if ($(window).width() <= 576) {
          $(".btnWrapper").fadeIn(600);
      }
    }
    lastScrollTop = st;
    if (st > 200) {
      $('.mapTitles').addClass('sticky');
      // $('.navbar.navbar-header').fadeOut(600);
    } else {
      $('.mapTitles').removeClass('sticky');
      // $('.navbar.navbar-header').fadeIn(600);
    }
    if ($(window).width() <= 576 && st >= bottomScrollPosition) {
        $(".btnWrapper").fadeIn(600);
    }
});
// *----------------------------------------------------------*
// Connection Lost
// *----------------------------------------------------------*  
setTimeout(function () {
  checkLiveConnection()
}, 1000);

checkLiveConnection()

function checkLiveConnection() {
  if (navigator.onLine) {} else {
    flashMessage(`Connection Lost`, `Lost connection to ONDC You appear to be offline or have a poor connection. Check your network and try again.`, 'danger', )
  }
}

// *----------------------------------------------------------*
// Flash Message
// *----------------------------------------------------------*  
function flashMessage(errorTitle, msg, classdata) {
  flashMessageNew(errorTitle, msg, classdata);
}


function flashMessageNew(errorTitle, msg, classdata) {

  errorType = "";
  custom_str = "";

  if (!errorTitle) {
    errorTitle = "Information";
  }

  if (typeof msg === 'string') {
    custom_str = msg;
  } else {

    custom_str = ""
    custom_str += msg["msg"];

    custom_str += `<a class="error-icon-show" title="Read More">
                        <i class="mdi mdi-chevron-down mdi-18px lh-0 tx-white"></i>
                      </a>
                      <div class="msg_details overflow-auto" style="display: none; max-height:150px">${msg["msg_details"]}</div>`;

  }

  if (classdata == "danger") {
    errorType = "danger";
    iconType = "mdi mdi-power-plug-off-outline"
  } else if (classdata == "warning") {
    errorType = "warning",
      iconType = "mdi mdi-information-off-outline"

  } else if (classdata == "info") {
    errorType = "info",
      iconType = "mdi mdi-information-outline"
  } else {
    errorType = "success";
    iconType = "mdi mdi-tick"
  }

  $.notify({
    // options
    title: '<strong>' + errorTitle + '</strong>',
    message: "<br>" + custom_str,
    icon: iconType,
  }, {
    // settings
    element: 'body',
    position: null,
    type: errorType,
    allow_dismiss: true,
    newest_on_top: true,
    showProgressbar: false,
    placement: {
      from: "bottom",
      align: "right"
    },
    offset: 20,
    spacing: 10,
    z_index: 99999,
    delay: 2000,
    timer: 1000,
    url_target: '_blank',
    mouse_over: null,
    animate: {
      enter: 'animated bounceInDown',
      exit: 'animated bounceOutUp'
    },
    onShow: null,
    onShown: null,
    onClose: null,
    onClosed: null,
    icon_type: 'class',
  });
  ``


}