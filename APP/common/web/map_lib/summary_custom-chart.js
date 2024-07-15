import { main } from './summary_india_map_script.js';

//
//function initDateRangePicker(maxDate, minDate) {
//
//      $('.input-daterange').datepicker('setStartDate', minDate.format('MM, YYYY'));
//      $('.input-daterange').datepicker('setEndDate', maxDate.format('MM, YYYY'));
//
//    let startOfMonth = maxDate.clone().startOf('month');
//    let endOfMonth = maxDate.clone().endOf('month');
//
//    function cb(start, end) {
//        $('#filterDaterange span').html(start.format('MMM, YYYY') + ' - ' + end.format('MMM, YYYY'));
//        $('#filterDaterangeText').html(start.format('MMM, YYYY') + ' - ' + end.format('MMM, YYYY')); // Update the text element
//    }
//
//    $('#filterDaterange').daterangepicker({
//        startDate: startOfMonth,
//        endDate: maxDate,
//        minDate: minDate,
//        maxDate: maxDate,
//        ranges: {
//            'Last 7 Days': [maxDate.clone().subtract(6, 'days'), maxDate],
//            'Last 30 Days': [maxDate.clone().subtract(29, 'days'), maxDate],
//            'This Month': [startOfMonth, maxDate],
//            'Last Month': [startOfMonth.clone().subtract(1, 'month'), endOfMonth.clone().subtract(1, 'month')],
//        },
//        opens: "left",
//        cancelClass: "btn-secondary",
//        "alwaysShowCalendars": true,
//    }, cb);
//
//    $('#filterDaterange').on('apply.daterangepicker', function(ev, picker) {
//        let formattedStartDate = picker.startDate.format('YYYY-MM-DD');
//        let formattedEndDate = picker.endDate.format('YYYY-MM-DD');
//        onDateRangeChange(formattedStartDate, formattedEndDate);
//    });
////
//    cb(startOfMonth, maxDate);
////    main(startOfMonth.format('YYYY-MM-DD'), maxDate.format('YYYY-MM-DD'));
//    main('04', '2024', '04', '2024', 'None', 'None');
//
//}

export async function loadTopDistrictLogisticsChart(domainName, startDate, endDate, category, subCategory) {
  const SessionStatename = localStorage.getItem('statename');

  const processAndRenderDistrictData = async (fetchFunction, chartId) => {
    try {
      const data = await fetchFunction(domainName, startDate, endDate, category, subCategory, SessionStatename);
      if (data) {
        renderTopStateOrdersChart(data, chartId);
      } else {
        console.info(`No data returned from ${fetchFunction.name}`);
      }
    } catch (error) {
      console.info(`Error processing data for ${chartId}:`, error);
    }
  };

  processAndRenderDistrictData(fetchTopDistrictHyperlocal, '#topDist_logistics');
}

export async function loadTopDistrictOrdersChart(domainName, startDate, endDate, category, subCategory) {
  $('.loadingTopDistrictOrders').html(loaderDiv);

  const SessionStatename = localStorage.getItem('statename');
  const processAndRenderDistrictData = async (fetchFunction, chartId) => {
    try {
      const data = await fetchFunction(domainName, startDate, endDate, category, subCategory, SessionStatename);
      if (data) {
        renderTopStateOrdersChart(data, chartId);
      } else {
        console.info(`No data returned from ${fetchFunction.name}`);
      }
    } catch (error) {
      console.info(`Error processing data for ${chartId}:`, error);
    } finally {
      $('.loadingTopDistrictOrders').empty();
    }
  };

  processAndRenderDistrictData(fetchTopDistrictOrders, '#topDist_order_summary');
}



export async function loadTopStateLogisticsChart(domainName, startDate, endDate, category, subCategory, state) {
  const SessionStatename = localStorage.getItem('statename');

  $('.loadingTopStateLogistics').html(loaderDiv);
  fetchTopStateLogistics(domainName, startDate, endDate, category, subCategory, SessionStatename)
    .then(data => {
      $('.loadingTopStateLogistics').empty();
      renderTopStateLogisticsChart(data, '#topStateChart_logistics');
    })
    .catch(error => {
      $('.loadingTopStateLogistics').empty();
      console.error('Error in fetchTopStateLogistics:', error);
    });
}



export async function loadTopStateOrdersChart(domainName, startDate, endDate, category, subCategory, state) {
  const SessionStatename = localStorage.getItem('statename');
  $('.loading_topStateChart_order').html(loaderDiv);
  fetchTopStateOrders(domainName, startDate, endDate, category, subCategory, SessionStatename)
    .then(data => {
      $('.loading_topStateChart_order').empty();
      renderTopStateOrdersChart(data, '#topStateChart_order_summary');
    })
    .catch(error => {
      $('.loading_topStateChart_order').empty();
      console.error('Error in fetchTopStateOrders:', error);
    });

 $('.loading_cumulativeChart').html(loaderDiv);
  fetchCummulativeOrders(domainName, startDate, endDate, category, subCategory)
    .then(data => {
      $('.loading_cumulativeChart').empty();
      renderTopStateOrdersChart(data, '#cumulativeChart_order_summary');
    })
    .catch(error => {
      $('.loading_cumulativeChart').empty();
      console.error('Error in fetchCummulativeOrders:', error);
    });
}

$(function() {
            let max_date;
            let min_date;
            console.log("here");

            // Initialize the date range picker with month/year format
            $('.input-daterange').datepicker({
                format: "mm, yyyy",
                minViewMode: 1,
                autoclose: true,
                todayHighlight: true
            }).on('changeDate', function(e) {
                if ($(e.target).attr('name') === 'end') {
                    // Close datepicker after selecting end date
                    $('.input-daterange').datepicker('hide');
                }
            });

            // Fetch max and min dates from the server
            $.ajax({
                url: 'get-max-date/',
                method: 'GET',
                success: function(data) {
                    max_date = data.max_date;
                    min_date = data.min_date;
                    let maxDate = moment(max_date, 'YYYY-MM');
                    let minDate = moment(min_date, 'YYYY-MM');
                    initDateRangePicker(maxDate, minDate);
                    updateDateInputs(minDate, maxDate); // Update text fields after API call
                    $(".db_updated_date").html(moment(data.max_date).format('MMM, YYYY'));
                },
                error: function(error) {
                    console.error("Error fetching maximum date:", error);
                    flashMessage("Error", "Error fetching maximum date", 'warning');
                }
            });

            // Initialize date range picker with provided min and max dates
            function initDateRangePicker(maxDate, minDate) {
                $('.input-daterange').datepicker('setStartDate', minDate.format('MM, YYYY'));
                $('.input-daterange').datepicker('setEndDate', maxDate.format('MM, YYYY'));
            }

            // Update text fields for start and end dates
            function updateDateInputs(start, end) {
                $('input[name="start"]').val(start.format('MM, YYYY'));
                $('input[name="end"]').val(end.format('MM, YYYY'));
            }

            // Handle date range change
            function onDateRangeChange(start, end) {
                const dateRangeDisplayString = `${start.format('MMM, YYYY')} to ${end.format('MMM, YYYY')}`;
                $(".dateRangeTitle").html(dateRangeDisplayString);
                main(start, end);
            }

            // Event listener for the submit button
            document.getElementById('submitFilter').addEventListener('click', function() {
                dateRangeFilter();
            });

            // Clear filter function
            function clearFilter() {
                try {
                    initDateRangePicker(moment(max_date, 'YYYY-MM'), moment(min_date, 'YYYY-MM'));
                    $("#submitFilter").click();
                } catch (error) {
                    console.error("Error clearing filter:", error);
                }
            }

            // Check if category filtering is included
            if (typeof includeCategory !== 'undefined' && includeCategory) {
                $('#clearFilterBtn').on('click', function() {
                    clearFilter();
                });
            }

            // Date range filter function
            function dateRangeFilter() {
                const startDateString = $('input[name="start"]').val();
                const endDateString = $('input[name="end"]').val();
                const category = 'None';
                const subCategory = 'None';

                console.log(startDateString);
                console.log(endDateString);

                const start_year = startDateString.split(',')[1].trim();
                const start_month = startDateString.split(',')[0].trim();
                const end_year = endDateString.split(',')[1].trim();
                const end_month = endDateString.split(',')[0].trim();

                main(start_month, start_year, end_month, end_year, category, subCategory);
            }

            // Clear date range function
            function clearDateRange(maxDate) {
                try {
                    initDateRangePicker(moment(maxDate, 'YYYY-MM'), moment(min_date, 'YYYY-MM'));
                    console.log("Date range cleared successfully.");
                } catch (error) {
                    console.error("Error clearing date range:", error);
                }
            }

            // Clear filter with default max date
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
        });
//
//$(function() {
//    let max_date;
//    let min_date;
//    console.log("here")
//    $('.input-daterange').datepicker({
//        format: "mm, yyyy",
//        minViewMode: 1
//    });
//
//    $.ajax({
//        url: 'get-max-date/',
//        method: 'GET',
//        success: function(data) {
//            max_date = data.max_date;
//            min_date = data.min_date;
//            let maxDate = moment(max_date);
//            let minDate = moment(min_date);
//            initDateRangePicker(maxDate, minDate);
//            let datePic = $("#filterDaterange span").text();
//          $(".dateRangeTitle").html(datePic);
//          $(".db_updated_date").html(moment(data.max_date).format('MMM DD, YYYY'));
//
//        },
//        error: function(error) {
//          console.error("Error fetching maximum date:", error);
//          flashMessage("Error", "Error fetching maximum date", 'warning');
//        }
//    });
//
//    function onDateRangeChange(start, end) {
//    debugger;;
//        const dateRangeDisplayString = document.getElementById('filterDaterange').textContent;
//        $(".dateRangeTitle").html(dateRangeDisplayString);
//      main(start, end);
//    }
//
//
//    document.getElementById('submitFilter').addEventListener('click', function() {
//        dateRangeFilter();
//    });
//
//    function clearFilter() {
//        try {
//            initDateRangePicker(moment(defaultMaxDate));
//            $("#submitFilter").click();
//        } catch (error) {
//            console.error("Error clearing filter:", error);
//        }
//    }
//
//    if (includeCategory){
//        $('#clearFilterBtn').on('click', function() {
//            clearFilter();
//        });
//    }
//
//
//    function dateRangeFilter() {
//        const startDateString = $('input[name="start"]').val();
//        const endDateString = $('input[name="end"]').val();
//        const category = 'None'
//        const subCategory = 'None'
//        console.log(startDateString)
//        console.log(endDateString)
//        const start_year = startDateString.split(',')[1].trim()
//        const start_month = startDateString.split(',')[0].trim()
//        const end_year = endDateString.split(',')[1].trim()
//        const end_month = endDateString.split(',')[0].trim()
//        main(start_month, start_year, end_month, end_year, category, subCategory);
//    }
//
//    if (includeCategory){
//        document.getElementById('clearFilterBtn').addEventListener('click', function() {
//            clearFilter(max_date);
//        });
//    }
//
//    function clearDateRange(maxDate) {
//        try {
//            initDateRangePicker(moment(maxDate));
//            console.log("Date range cleared successfully.");
//        } catch (error) {
//            console.error("Error clearing date range:", error);
//        }
//    }
//
//    function clearFilter(defaultMaxDate) {
//        try {
//            $("#categoryDropdown").val("all").change();
//            clearDateRange(defaultMaxDate);
//            $("#submitFilter").click();
//            console.log("Filter cleared successfully.");
//        } catch (error) {
//            console.error("Error clearing filter:", error);
//        }
//    }
//
//    function formatDate(date) {
//        return moment(date).format('YYYY-MM-DD');
//    }
//
//});

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

