import { main } from './overall_india_map_script.js';


var loaderDiv = `<div class="innerLoader">
      <span class="loader-dot"></span>
     </div>`

let default_state = 'Maharashtra'.toLocaleUpperCase();


function formatDateStringDB(inputDateStr) {
  let dateObj = new Date(inputDateStr);
  let year = dateObj.getFullYear();
  let month = (dateObj.getMonth() + 1).toString().padStart(2, '0');
  let day = dateObj.getDate().toString().padStart(2, '0');

  return `${year}-${month}-${day}`;
}


async function fetchFromApi(url) {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching data:', error);
    throw error;
  }
}

async function fetchCummulativeOrders(domainName, startDate, endDate, category, subCategory, state) {
  try {
    let pathname = window.location.pathname;
    const queryParams = new URLSearchParams({ domainName, startDate, endDate, category, subCategory, state });
    const response = await fetchFromApi(`${pathname}/api/top_cummulative_orders/?${queryParams}`);
    return response;
  } catch (error) {
    console.error('Error fetching data:', error);
  }
}

async function fetchCummulativeSellers(domainName, startDate, endDate, category, subCategory, state) {
  try {
    let pathname = window.location.pathname;
    const queryParams = new URLSearchParams({ domainName, startDate, endDate, category, subCategory, state });
    const response = fetchFromApi(`${pathname}/api/top_cummulative_sellers/?${queryParams}`);
    return response;
  } catch (error) {
    console.error('Error fetching data:', error);
  }
}



async function fetchTopStateOrders(domainName, startDate, endDate, category, subCategory, state) {
  try {
    let pathname = window.location.pathname;
    const queryParams = new URLSearchParams({ domainName, startDate, endDate, category, subCategory, state });
    const response = fetchFromApi(`${pathname}/api/top_state_orders/?${queryParams}`);
    return response;

  } catch (error) {
    console.error('Error fetching data:', error);
  }

}

async function fetchTopStateSellers(domainName, startDate, endDate, category, subCategory, state) {
  try {
    let pathname = window.location.pathname;
    const queryParams = new URLSearchParams({ domainName, startDate, endDate, category, subCategory, state });
    const response = fetchFromApi(`${pathname}/api/top_state_sellers/?${queryParams}`);
    return response;
  } catch (error) {
    console.error('Error fetching data:', error);
  }

}

async function fetchTopStateLogistics(domainName, startDate, endDate, category, subCategory, state) {
  try {
    let pathname = window.location.pathname;
    const queryParams = new URLSearchParams({ domainName, startDate, endDate, category, subCategory, state });
    const response = fetchFromApi(`${pathname}/api/top_state_hyperlocal/?${queryParams}`);
    return response;
  } catch (error) {
    console.error('Error fetching data:', error);
  }

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

export async function loadTopStateSellersChart(domainName, startDate, endDate, category, subCategory, state) {
    const SessionStatename = localStorage.getItem('statename');

  $('.loading_topStateChart_supply').html(loaderDiv);

  fetchTopStateSellers(domainName, startDate, endDate, category, subCategory, SessionStatename)
    .then(data => {
      $('.loading_topStateChart_supply').empty();
      renderTopStateSellersChart(data, '#topStateChart_supply');
    })
    .catch(error => {
      $('.loading_topStateChart_supply').empty();
      console.error('Error in fetchTopStateSellers:', error);
    });

  $('.loading_cumulativeChart_supply').html(loaderDiv);
  fetchCummulativeSellers(domainName, startDate, endDate, category, subCategory)
    .then(data => {
      $('.loading_cumulativeChart_supply').empty();
      renderTopStateSellersChart(data, '#cumulativeChart_supply');
    })
    .catch(error => {
      $('.loading_cumulativeChart_supply').empty();
      console.error('Error in fetchCummulativeSellers:', error);
    });
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

function filterSeriesByState(series, desiredState) {
  if (desiredState){
    return series.filter(serie => serie.name.toUpperCase() === desiredState.toUpperCase());

  }else{
    return series
    .sort((a, b) => b.totalOrders - a.totalOrders)
    .slice(0, 3);
  }
  
}

async function fetchTopDistrictOrders(domainName, startDate, endDate, category, subCategory, state) {
   let pathname = window.location.pathname;
  const queryParams = new URLSearchParams({ domainName, startDate, endDate });
  if (category) queryParams.append('category', category);
  if (subCategory) queryParams.append('subCategory', subCategory);
  if (state) queryParams.append('state', state);
  
  const url = `${pathname}/api/top_district_orders/?${queryParams.toString()}`;
  
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.info('Error fetching data:', error);
    throw error;
  }
}

async function fetchTopDistrictSellers(domainName, startDate, endDate, category, subCategory, state) {
  let pathname = window.location.pathname;
  const queryParams = new URLSearchParams({ domainName, startDate, endDate });

  if (category) queryParams.append('category', category);
  if (subCategory) queryParams.append('subCategory', subCategory);
  if (state) queryParams.append('state', state);
  
  const url = `${pathname}/api/top_district_sellers/?${queryParams.toString()}`;
  
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.info('Error fetching data:', error);
    throw error;
  }
}

async function fetchTopDistrictHyperlocal(domainName, startDate, endDate, category, subCategory, state) {
  let pathname = window.location.pathname;
  const queryParams = new URLSearchParams({ domainName, startDate, endDate });

  if (category) queryParams.append('category', category);
  if (subCategory) queryParams.append('subCategory', subCategory);
  if (state) queryParams.append('state', state);
  
  const url = `${pathname}/api/top_district_hyperlocal/?${queryParams.toString()}`;
  
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.info('Error fetching data:', error);
    throw error;
  }
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

export async function loadTopDistrictSellersChart(domainName, startDate, endDate, category, subCategory) {
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

  processAndRenderDistrictData(fetchTopDistrictSellers, '#topDist_supply');
}

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

var chartInstances = {};
function renderTopStateOrdersChart(data, chart_id, indiaTrendLine) {

  if (chartInstances[chart_id]) {
    chartInstances[chart_id].destroy();
  }

  if (!data.series || data.series.length === 0 || data.series.length === '' || data.series.length === 'undefined' || data.series.length === 'null' || data.series.length === 'NULL') {
    document.querySelector(chart_id).innerHTML = "<div class='nodata d-flex flex-column align-items-center'><i class='mdi mdi-information-outline'></i> No Data to Display</div>";
    return false;
  }

  var colors = ['#FF7722', '#26a0fc', '#32cd32']
  var markers =  { };

  data.series.forEach(series => {
    series.type = 'area';
    series.yAxisIndex = 0;
  });


  if (chart_id === '#cumulativeChart_order_summary' || chart_id === '#cumulativeChart_supply'){
    colors = ["#00b8d4"]
    markers = {size: 3, strokeWidth: 2}
  } else{
    colors = ['#FF7722', '#26a0fc', '#32cd32']
    markers = {}
  }

var yAxisOptions;

  yAxisOptions = {
    labels: {
      show: true,
      maxWidth: "auto",
      offsetX: -15,
    },
  };

  var topState = {
    series: data.series,
    chart: {
      height: 180,
      width:"100%",
      type: 'area',
      stacked: false,
      toolbar: {
        show: false,
        tools: {
          download: false
        }
    }
    },

    colors: colors,
    zoom: {
      enabled: false,
      type: 'x',
      resetIcon: {
          offsetX: -10,
          offsetY: 0,
          fillColor: '#fff',
          strokeColor: '#37474F'
      },
      selection: {
          background: '#90CAF9',
          border: '#0D47A1'
      }
  },
    stroke: {
      show: true,
      curve: 'smooth',
      width: [3, 3, 3, 0],
    },
    dataLabels: {
      enabled: false,
    },
    fill: {
      gradient: {
        enabled: true,
        opacityFrom: 0.6,
        opacityTo: 0
      }
    },
    markers: markers,
    grid: {
      show: true,
      borderColor: '#ececec',
      padding: { left: -10, right: 0, top: -20, bottom: -10 },
    },
    legend: {
      show:true,
    },
    xaxis: {
      labels: {
        show: false,
        offsetX: 10,
      },
      categories: data.categories
    },
    yaxis: yAxisOptions,
    tooltip: {
      show: true,
      y: {
        formatter: function (val) {
          if (chart_id === "#topStateChart_logistics" || chart_id === "#topDist_logistics") {
            return val + "%";
          }
          return val;
        },
        title: {
          formatter: (seriesName) => seriesName,
        },
      },
    },

  };

  var statechart1 = new ApexCharts(document.querySelector(chart_id), topState);
  statechart1.render();
  chartInstances[chart_id] = statechart1;

}


function exportPNG(statechart2) {
    statechart2.downloadPNG();
}

var chartSellerInstances = {};
function renderTopStateSellersChart(data, chart_id) {

  if (chartInstances[chart_id]) {
    chartInstances[chart_id].destroy();
  }


  if (!data.series || data.series.length === 0 || data.series.length === '' || data.series.length === 'undefined' || data.series.length === 'null' || data.series.length === 'NULL') {
    document.querySelector(chart_id).innerHTML = "<div class='nodata d-flex flex-column align-items-center'><i class='mdi mdi-information-outline'></i> No Data to Display</div>";
    return;
  }
  if (chartSellerInstances[chart_id]) {
    chartSellerInstances[chart_id].destroy();
  }

  var colors = ['#FF7722', '#26a0fc', '#32cd32']
  var markers =  { };

  data.series.forEach(series => {
    series.type = 'area';
    series.yAxisIndex = 0;
  });


  if (chart_id === '#cumulativeChart_order_summary' || chart_id === '#cumulativeChart_supply'){
    colors = ["#00b8d4"]
    markers = {size: 3, strokeWidth: 2}
  } else{
    colors = ['#FF7722', '#26a0fc', '#32cd32']
    markers = {}
  }

var yAxisOptions;
  yAxisOptions = {
    labels: {
      show: true,
      maxWidth: "auto",
      offsetX: -15,
    },
  };

  var topSellersState = {
    series: data.series,
    chart: {
      height: 180,
      width:"100%",
      type: 'area',
      stacked: false,
      toolbar: {
        show: false,
        tools: {
          download: false
        }
    }
    },

    colors: colors,
    zoom: {
      enabled: false,
      type: 'x',
      resetIcon: {
          offsetX: -10,
          offsetY: 0,
          fillColor: '#fff',
          strokeColor: '#37474F'
      },
      selection: {
          background: '#90CAF9',
          border: '#0D47A1'
      }
  },
  stroke: {
    show: true,
    curve: 'smooth',
    width: [3, 3, 3, 0],
  },
  dataLabels: {
    enabled: false,
  },
    noData: {
    text: 'No Data to Display'
  },
    fill: {
      gradient: {
        enabled: true,
        opacityFrom: 0.6,
        opacityTo: 0
      }
    },
    markers: markers,
    grid: {
      show: true,
      borderColor: '#ececec',
      padding: { left: -10, right: 0, top: -20, bottom: -10 },
    },
    legend: {
      show:true,
    },
    xaxis: {
      labels: {
        show: false,
        offsetX: 10,
      },
      categories: data.categories
    },
    yaxis: yAxisOptions,
    tooltip: {
      show: true,
      y: {
        formatter: function (val) {
          if (chart_id === "#topStateChart_logistics" || chart_id === "#topDist_logistics") {
            return val + "%";
          }
          return val;
        },
        title: {
          formatter: (seriesName) => seriesName,
        },
      },
    },

  };

  var statechart2 = new ApexCharts(document.querySelector(chart_id), topSellersState);
  statechart2.render();
  chartSellerInstances[chart_id] = statechart2;

  
}


var chartLogisticsInstances = {};
function renderTopStateLogisticsChart(data, chart_id) {

  if (chartInstances[chart_id]) {
    chartInstances[chart_id].destroy();
  }

  if (!data.series || data.series.length === 0 || data.series.length === '' || data.series.length === 'undefined' || data.series.length === 'null' || data.series.length === 'NULL') {
    document.querySelector(chart_id).innerHTML = "<div class='nodata d-flex flex-column align-items-center'><i class='mdi mdi-information-outline'></i> No Data to Display</div>";
    return;
  }
  if (chartLogisticsInstances[chart_id]) {
    chartLogisticsInstances[chart_id].destroy();
  }

  var colors = ['#FF7722', '#26a0fc', '#32cd32']
  var markers =  { };

  data.series.forEach(series => {
    series.type = 'area';
    series.yAxisIndex = 0;
  });


  if (chart_id === '#cumulativeChart_order_summary' || chart_id === '#cumulativeChart_supply'){
    colors = ["#00b8d4"]
    markers = {size: 3, strokeWidth: 2}
  } else{
    colors = ['#FF7722', '#26a0fc', '#32cd32']
    markers = {}
  }

var yAxisOptions;
  yAxisOptions = {
    labels: {
      show: true,
      maxWidth: "auto",
      offsetX: -15,
    },
  };

  var topLogisticsState = {
    series: data.series,
    chart: {
      height: 180,
      width:"100%",
      type: 'area',
      stacked: false,
      toolbar: {
        show: false,
        tools: {
          download: false
        }
    }
    },

    colors: colors,
    zoom: {
      enabled: false,
      type: 'x',
      resetIcon: {
          offsetX: -10,
          offsetY: 0,
          fillColor: '#fff',
          strokeColor: '#37474F'
      },
      selection: {
          background: '#90CAF9',
          border: '#0D47A1'
      }
  },
    stroke: {
      show: true,
      curve: 'smooth',
      width: [3, 3, 3, 0],
    },
    dataLabels: {
      enabled: false,
    },
    fill: {
      gradient: {
        enabled: true,
        opacityFrom: 0.6,
        opacityTo: 0
      }
    },
    markers: markers,
    grid: {
      show: true,
      borderColor: '#ececec',
      padding: { left: -10, right: 0, top: -20, bottom: -10 },
    },
    legend: {
      show:true,
    },
    xaxis: {
      labels: {
        show: false,
        offsetX: 10,
      },
      categories: data.categories
    },
    yaxis: yAxisOptions,
    tooltip: {
      show: true,
      y: {
        formatter: function (val) {
          if (chart_id === "#topStateChart_logistics" || chart_id === "#topDist_logistics") {
            return val + "%";
          }
          return val;
        },
        title: {
          formatter: (seriesName) => seriesName,
        },
      },
    },

  };

  var statechart3 = new ApexCharts(document.querySelector(chart_id), topLogisticsState);
  statechart3.render();
  chartLogisticsInstances[chart_id] = statechart3;

}


let statesData = [];


//$(document).ready(function() {
//    let allData = [];
//    let defaultMaxDate;
//    let includeCategory = true; // Assuming includeCategory is a global variable set somewhere in your code
//    let category = '';
//    let subCategory = '';
//    let startDate, endDate;
//
//    function dateRangeFilter() {
//        const startDateString = $('#filterDaterange').data('daterangepicker').startDate.format('YYYY-MM-DD');
//        const endDateString = $('#filterDaterange').data('daterangepicker').endDate.format('YYYY-MM-DD');
//        main(startDateString, endDateString, category, subCategory);
//    }
//
//    function clearFilter() {
//        if (includeCategory) {
//            $("#categoryDropdown").val("all").change();
//            $("#subCategoryDropdown").val("all").change();
//        }
//    }
//
//    // Initialize date range picker
//    // initDateRangePicker(moment(defaultMaxDate)); // Uncomment and define initDateRangePicker if needed
//
//    $("#submitFilter").click(function() {
//        if (startDate && endDate) {
//            const startDateString = startDate.format('YYYY-MM-DD');
//            const endDateString = endDate.format('YYYY-MM-DD');
//            main(startDateString, endDateString, category, subCategory);
//        } else {
//            alert("Please select a date range.");
//        }
//    });
//
//    if (includeCategory) {
//        $('#clearFilterBtn').on('click', function() {
//            clearFilter();
//        });
//    }
//
//    $('#dateRange').datepicker({
//        format: "M, yyyy", // Set format to "Jan, 2024"
//        startView: "months",
//        minViewMode: "months",
//        autoclose: false, // Prevent the datepicker from closing after selection
//    }).on('changeDate', function(e) {
//        if (!startDate) {
//            startDate = e.date;
//        } else if (!endDate) {
//            endDate = e.date;
//            if (startDate > endDate) {
//                let temp = startDate;
//                startDate = endDate;
//                endDate = temp;
//            }
//            $('#dateRange').datepicker('setDate', [startDate, endDate]);
//
//            // Update input value with the selected range in the specified format
//            var startDateFormatted = $.fn.datepicker.DPGlobal.formatDate(startDate, "M, yyyy", "en");
//            var endDateFormatted = $.fn.datepicker.DPGlobal.formatDate(endDate, "M, yyyy", "en");
//            $('#dateRange').val(startDateFormatted + ' - ' + endDateFormatted);
//
//            // Collapse the datepicker
//            $('#collapseFilters').collapse('hide');
//        }
//    });
//
//    $('#clearRange').click(function() {
//        $('#dateRange').datepicker('clearDates');
//        startDate = null;
//        endDate = null;
//    });
//
//    $.ajax({
//        url: 'get-max-date/',
//        method: 'GET',
//        success: function(data) {
//            defaultMaxDate = moment(data.max_date);
//            const minDate = moment(data.min_date);
//            // initDateRangePicker(defaultMaxDate, minDate); // Uncomment and define initDateRangePicker if needed
//            $(".dateRangeTitle").html($("#filterDaterange span").text());
//            $(".db_updated_date").html(moment(data.max_date).format('MMM DD, YYYY'));
//        },
//        error: function(error) {
//            console.error("Error fetching maximum date:", error);
//            flashMessage("Error", "Error fetching maximum date", 'warning');
//        }
//    });
//});
//

//$(document).ready(function() {
//    let allData = [];
//    let defaultMaxDate;
//    let includeCategory = true; // Assuming includeCategory is a global variable set somewhere in your code
//    let category = '';
//    let subCategory = '';
//
//    function dateRangeFilter() {
//        const startDateString = $('#filterDaterange').data('daterangepicker').startDate.format('YYYY-MM-DD');
//        const endDateString = $('#filterDaterange').data('daterangepicker').endDate.format('YYYY-MM-DD');
//        main(startDateString, endDateString, category, subCategory);
//    }
//
//    function clearFilter() {
//        if (includeCategory) {
//            $("#categoryDropdown").val("all").change();
//            $("#subCategoryDropdown").val("all").change();
//        }
//    }
//
//    // Initialize date range picker
//    // initDateRangePicker(moment(defaultMaxDate)); // Uncomment and define initDateRangePicker if needed
//
//    $("#submitFilter").click(function() {
//        const startDateString = $('#dateRange').data('datepicker').startDate.format('YYYY-MM-DD');
//        const endDateString = $('#dateRange').data('datepicker').endDate.format('YYYY-MM-DD');
//        main(startDateString, endDateString, category, subCategory);
//    });
//
//    if (includeCategory) {
//        $('#clearFilterBtn').on('click', function() {
//            clearFilter();
//        });
//    }
//
//    $('#dateRange').datepicker({
//        format: "M, yyyy", // Set format to "Jan, 2024"
//        startView: "months",
//        minViewMode: "months",
//        autoclose: false, // Prevent the datepicker from closing after selection
//        ranges: {
//            'Last 7 Days': [moment().subtract(6, 'days'), moment()],
//            'Last 30 Days': [moment().subtract(29, 'days'), moment()],
//            'This Month': [moment().startOf('month'), moment().endOf('month')],
//            'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
//        }
//    });
//
//    var startDate, endDate;
//    $('#dateRange').on('changeDate', function(e) {
//        if (!startDate) {
//            startDate = e.date;
//        } else if (!endDate) {
//            endDate = e.date;
//            if (startDate > endDate) {
//                var temp = startDate;
//                startDate = endDate;
//                endDate = temp;
//            }
//            $('#dateRange').datepicker('setDate', [startDate, endDate]);
//            startDate = null;
//            endDate = null;
//        }
//        // Update input value with the selected range in the specified format
//        if (startDate && endDate) {
//            var startDateFormatted = $.fn.datepicker.DPGlobal.formatDate(startDate, "M, yyyy", "en");
//            var endDateFormatted = $.fn.datepicker.DPGlobal.formatDate(endDate, "M, yyyy", "en");
//            $('#dateRange').val(startDateFormatted + ' - ' + endDateFormatted);
//        }
//    });
//
//    $('#clearRange').click(function() {
//        $('#dateRange').datepicker('clearDates');
//    });
//
//    $.ajax({
//        url: 'get-max-date/',
//        method: 'GET',
//        success: function(data) {
//            defaultMaxDate = moment(data.max_date);
//            const minDate = moment(data.min_date);
//            // initDateRangePicker(defaultMaxDate, minDate); // Uncomment and define initDateRangePicker if needed
//            $(".dateRangeTitle").html($("#filterDaterange span").text());
//            $(".db_updated_date").html(moment(data.max_date).format('MMM DD, YYYY'));
//        },
//        error: function(error) {
//            console.error("Error fetching maximum date:", error);
//            flashMessage("Error", "Error fetching maximum date", 'warning');
//        }
//    });
//});


//$(document).ready(function() {
//    let allData = [];
//    let defaultMaxDate;
//
//    function dateRangeFilter() {
//        const startDateString = $('#filterDaterange').data('daterangepicker').startDate.format('YYYY-MM-DD');
//        const endDateString = $('#filterDaterange').data('daterangepicker').endDate.format('YYYY-MM-DD');
//
//        main(startDateString, endDateString, category, subCategory);
//    }
//
//    function clearFilter() {
//        if (includeCategory){
//            $("#categoryDropdown").val("all").change();
//            $("#subCategoryDropdown").val("all").change();
//        }
//    }
////            initDateRangePicker(moment(defaultMaxDate));
//    $("#submitFilter").click();{
//        const startDateString = $('#dateRange').data('datepicker').startDate.format('YYYY-MM-DD');
//        const endDateString = $('#dateRange').data('datepicker').endDate.format('YYYY-MM-DD');
////        const category = $('#categoryDropdown').val();
////        const subCategory = $('#subCategoryDropdown').val();
//        main(startDateString, endDateString, category, subCategory)
//
//    }
//
//    if (includeCategory){
//        $('#clearFilterBtn').on('click', function() {
//            clearFilter();
//        });
//
//    }
//
//
//$('#dateRange').datepicker({
//    format: "M, yyyy", // Set format to "Jan, 2024"
//    startView: "months",
//    minViewMode: "months",
//    autoclose: false, // Prevent the datepicker from closing after selection
//    ranges: {
//        'Last 7 Days': [moment().subtract(6, 'days'), moment()],
//        'Last 30 Days': [moment().subtract(29, 'days'), moment()],
//        'This Month': [moment().startOf('month'), moment().endOf('month')],
//        'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
//    }
//});
//
//var startDate, endDate;
//      $('#dateRange').on('changeDate', function(e) {
//        if (!startDate) {
//          startDate = e.date;
//        } else if (!endDate) {
//          endDate = e.date;
//          if (startDate > endDate) {
//            var temp = startDate;
//            startDate = endDate;
//            endDate = temp;
//          }
//          $('#dateRange').datepicker('setDate', [startDate, endDate]);
//          startDate = null;
//          endDate = null;
//        }
//        // Update input value with the selected range in the specified format
//        if (startDate && endDate) {
//          var startDateFormatted = $.fn.datepicker.DPGlobal.formatDate(startDate, "M, yyyy", "en");
//          var endDateFormatted = $.fn.datepicker.DPGlobal.formatDate(endDate, "M, yyyy", "en");
//          $('#dateRange').val(startDateFormatted + ' - ' + endDateFormatted);
//        }
//      });
//
//      $('#clearRange').click(function() {
//        $('#dateRange').datepicker('clearDates');
//      });
////              cb(startOfMonth, maxDate);
////        main(startOfMonth.format('YYYY-MM-DD'), maxDate.format('YYYY-MM-DD'));
////    });
//
//    $.ajax({
//        url: 'get-max-date/',
//        method: 'GET',
//        success: function(data) {
//            defaultMaxDate = moment(data.max_date);
//            const minDate = moment(data.min_date);
////            initDateRangePicker(defaultMaxDate, minDate);
//            $(".dateRangeTitle").html($("#filterDaterange span").text());
//            $(".db_updated_date").html(moment(data.max_date).format('MMM DD, YYYY'));
//
//        },
//        error: function(error) {
//            console.error("Error fetching maximum date:", error);
//            flashMessage("Error", "Error fetching maximum date", 'warning');
//        }
//    });
//});
$(document).ready(function() {
    let allData = [];
    let defaultMaxDate;
    if (includeCategory){
        function fetchAndUpdateCategoryList() {
            fetch('/categories')
                .then(response => response.json())
                .then(data => {
                    allData = data;
                    updateDropdown('categoryDropdown', data, 'category');
                    updateDropdown('subCategoryDropdown', data, 'sub_category');
                })
                .catch(error => console.error('Error fetching category list:', error));
        }

        function updateDropdown(dropdownId, data, key) {
            const dropdown = document.getElementById(dropdownId);
            dropdown.innerHTML = '<option value="all">ALL</option>';
            let options = new Set();

            data.forEach(item => {
                if (item[key] && !options.has(item[key])) {
                    options.add(item[key]);
                    const optionElement = document.createElement('option');
                    optionElement.value = item[key];
                    optionElement.textContent = item[key];
                    dropdown.appendChild(optionElement);
                }
            });

            $(`#${dropdownId}`).select2();
        }

        fetchAndUpdateCategoryList();

        $('#categoryDropdown').on('change', function() {
            const selectedCategory = this.value;
            updateSubCategories(selectedCategory);
        });

        function updateSubCategories(selectedCategory) {
            const filteredData = allData.filter(item => item.category === selectedCategory || selectedCategory === 'all');
            updateDropdown('subCategoryDropdown', filteredData, 'sub_category');
        }

        updateSubCategories('all');

        $('#submitFilter').on('click', function() {
            dateRangeFilter();
        });
    }


    function dateRangeFilter() {
        const startDateString = $('#filterDaterange').data('daterangepicker').startDate.format('YYYY-MM-DD');
        const endDateString = $('#filterDaterange').data('daterangepicker').endDate.format('YYYY-MM-DD');
        const category = $('#categoryDropdown').val();
        const subCategory = $('#subCategoryDropdown').val();

        main(startDateString, endDateString, category, subCategory);
    }

    function clearFilter() {
        try {
        if (includeCategory){
            $("#categoryDropdown").val("all").change();
            $("#subCategoryDropdown").val("all").change();
        }

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

    function initDateRangePicker(maxDate, minDate) {
        var endOfMonth = maxDate.clone().endOf('month');
        var startOfMonth = endOfMonth.clone().startOf('month');

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
            var formattedStartDate = picker.startDate.format('YYYY-MM-DD');
            var formattedEndDate = picker.endDate.format('YYYY-MM-DD');
            dateRangeFilter();
            $(".dateRangeTitle").html($("#filterDaterange span").text());

        });

        cb(startOfMonth, maxDate);
        main(startOfMonth.format('YYYY-MM-DD'), maxDate.format('YYYY-MM-DD'));
    }

    $.ajax({
        url: 'get-max-date/',
        method: 'GET',
        success: function(data) {
            defaultMaxDate = moment(data.max_date);
            const minDate = moment(data.min_date);
            initDateRangePicker(defaultMaxDate, minDate);
            $(".dateRangeTitle").html($("#filterDaterange span").text());
            $(".db_updated_date").html(moment(data.max_date).format('MMM DD, YYYY'));

        },
        error: function(error) {
            console.error("Error fetching maximum date:", error);
            flashMessage("Error", "Error fetching maximum date", 'warning');
        }
    });
});


$('.text-truncate').tooltipOnOverflow();

