import { main } from './b2b_india_map_script.js';


$(function() {
    let max_date;
    let min_date;

    $.ajax({
        url: 'get-max-date/',
        method: 'GET',
        success: function(data) {
            max_date = data.max_date; 
            min_date = data.min_date;
            let maxDate = moment(max_date);
            let minDate = moment(min_date);
            initDateRangePicker(maxDate, minDate);
            let datePic = $("#filterDaterange span").text();
          $(".dateRangeTitle").html(datePic);
          $(".db_updated_date").html(moment(data.max_date).format('MMM DD, YYYY'));
          
        },
        error: function(error) {
          console.error("Error fetching maximum date:", error);
          flashMessage("Error", "Error fetching maximum date", 'warning');
        }
    });

    function onDateRangeChange(start, end) {
        const dateRangeDisplayString = document.getElementById('filterDaterange').textContent;
        $(".dateRangeTitle").html(dateRangeDisplayString);
      main(start, end);
    }

    function initDateRangePicker(maxDate, minDate) {
        let startOfMonth = maxDate.clone().startOf('month');
        let endOfMonth = maxDate.clone().endOf('month');

        function cb(start, end) {
            $('#filterDaterange span').html(start.format('MMM DD, YYYY') + ' - ' + end.format('MMM DD, YYYY'));
            $('#filterDaterangeText').html(start.format('MMM DD, YYYY') + ' - ' + end.format('MMM DD, YYYY')); // Update the text element
        }

        $('#filterDaterange').daterangepicker({
            startDate: startOfMonth,
            endDate: maxDate,
            minDate: minDate,
            maxDate: maxDate,
            ranges: {
                'Last 7 Days': [maxDate.clone().subtract(6, 'days'), maxDate],
                'Last 30 Days': [maxDate.clone().subtract(29, 'days'), maxDate],
                'This Month': [startOfMonth, maxDate],
                'Last Month': [startOfMonth.clone().subtract(1, 'month'), endOfMonth.clone().subtract(1, 'month')],
            },
            opens: "left",
            cancelClass: "btn-secondary",
            "alwaysShowCalendars": true,
        }, cb);

        $('#filterDaterange').on('apply.daterangepicker', function(ev, picker) {
            let formattedStartDate = picker.startDate.format('YYYY-MM-DD');
            let formattedEndDate = picker.endDate.format('YYYY-MM-DD');
            onDateRangeChange(formattedStartDate, formattedEndDate);
        });

        cb(startOfMonth, maxDate);
        main(startOfMonth.format('YYYY-MM-DD'), maxDate.format('YYYY-MM-DD'));
    }

    document.getElementById('submitFilter').addEventListener('click', function() {
        dateRangeFilter();
    });

    function clearFilter() {
        try {
            initDateRangePicker(moment(defaultMaxDate));
            $("#submitFilter").click();
        } catch (error) {
            console.error("Error clearing filter:", error);
        }
    }

    if (includeCategory){
        $('#clearFilterBtn').on('click', function() {
            clearFilter();
        });
    }


    function dateRangeFilter() {
        const startDateString = $('#filterDaterange').data('daterangepicker').startDate.format('YYYY-MM-DD');
        const endDateString = $('#filterDaterange').data('daterangepicker').endDate.format('YYYY-MM-DD');
        const category = 'None'
        const subCategory = 'None'
        console.log(startDateString)
        console.log(endDateString)
        main(startDateString, endDateString, category, subCategory);
    }

    if (includeCategory){
        document.getElementById('clearFilterBtn').addEventListener('click', function() {
            clearFilter(max_date);
        });
    }

    function clearDateRange(maxDate) {
        try {
            initDateRangePicker(moment(maxDate));
            console.log("Date range cleared successfully.");
        } catch (error) {
            console.error("Error clearing date range:", error);
        }
    }

    function clearFilter(defaultMaxDate) {
        try {
            $("#categoryDropdown").val("all").change();
            clearDateRange(defaultMaxDate);
            $("#submitFilter").click();
            console.log("Filter cleared successfully.");
        } catch (error) {
            console.error("Error clearing filter:", error);
        }
    }

    function formatDate(date) {
        return moment(date).format('YYYY-MM-DD');
    }

});

function formatDateStringDB(inputDateStr) {
  let dateObj = new Date(inputDateStr);
  let year = dateObj.getFullYear();
  let month = (dateObj.getMonth() + 1).toString().padStart(2, '0');
  let day = dateObj.getDate().toString().padStart(2, '0');

  return `${year}-${month}-${day}`;
}


const loaderDiv = `<div class="innerLoader">
      <span class="loader-dot"></span>
     </div>`



$(document).ready(function() {
  let ellipsisText = $("#max_orders_delivered_category .ellipsis-text").text();
  $("#max_orders_delivered_category .ellipsis-text").attr("title", ellipsisText);
});

$('.text-truncate').tooltipOnOverflow();

