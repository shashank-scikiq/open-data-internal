import { main } from './india_map_script.js';


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
    const queryParams = new URLSearchParams({ domainName, startDate, endDate, category, subCategory, state });
    const response = await fetchFromApi(`/api/top_cummulative_orders/?${queryParams}`);
    return response;
  } catch (error) {
    console.error('Error fetching data:', error);
  }
}

async function fetchCummulativeSellers(domainName, startDate, endDate, category, subCategory, state) {
  try {
    const queryParams = new URLSearchParams({ domainName, startDate, endDate, category, subCategory, state });
    const response = fetchFromApi(`/api/top_cummulative_sellers/?${queryParams}`);
    return response;
  } catch (error) {
    console.error('Error fetching data:', error);
  }
}



async function fetchTopStateOrders(domainName, startDate, endDate, category, subCategory, state) {
  try {
    const queryParams = new URLSearchParams({ domainName, startDate, endDate, category, subCategory, state });
    const response = fetchFromApi(`/api/top_state_orders/?${queryParams}`);
    return response;

  } catch (error) {
    console.error('Error fetching data:', error);
  }

}

async function fetchTopStateSellers(domainName, startDate, endDate, category, subCategory, state) {
  try {
      const queryParams = new URLSearchParams({ domainName, startDate, endDate, category, subCategory, state });
    const response = fetchFromApi(`/api/top_state_sellers/?${queryParams}`);
    return response;
  } catch (error) {
    console.error('Error fetching data:', error);
  }

}

async function fetchTopStateLogistics(domainName, startDate, endDate, category, subCategory, state) {
  try {
    const queryParams = new URLSearchParams({ domainName, startDate, endDate, category, subCategory, state });
    const response = fetchFromApi(`/api/top_state_hyperlocal/?${queryParams}`);
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
  const queryParams = new URLSearchParams({ domainName, startDate, endDate });
  if (category) queryParams.append('category', category);
  if (subCategory) queryParams.append('subCategory', subCategory);
  if (state) queryParams.append('state', state);
  
  const url = `/api/top_district_orders/?${queryParams.toString()}`;
  
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
  const queryParams = new URLSearchParams({ domainName, startDate, endDate });

  if (category) queryParams.append('category', category);
  if (subCategory) queryParams.append('subCategory', subCategory);
  if (state) queryParams.append('state', state);
  
  const url = `/api/top_district_sellers/?${queryParams.toString()}`;
  
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
  const queryParams = new URLSearchParams({ domainName, startDate, endDate });

  if (category) queryParams.append('category', category);
  if (subCategory) queryParams.append('subCategory', subCategory);
  if (state) queryParams.append('state', state);
  
  const url = `/api/top_district_hyperlocal/?${queryParams.toString()}`;
  
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
  console.log(topState, "topState")
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


async function fetchCategoryMetrics(startDate, endDate, category, subCategory, domainName, state) {
  const queryParams = new URLSearchParams({ domainName, startDate, endDate });

  if (category) queryParams.append('category', category);
  if (subCategory) queryParams.append('subCategory', subCategory);
  if (state) queryParams.append('state', state);

  const url = `/api/category_penetration_orders/?${queryParams.toString()}`;

  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.info('Error fetching category metrics:', error);
    throw error;
  }
}

async function fetchCategorySellersMetrics(startDate, endDate, category, subCategory, domainName, state) {
  const queryParams = new URLSearchParams({ domainName, startDate, endDate });

  if (category) queryParams.append('category', category);
  if (subCategory) queryParams.append('subCategory', subCategory);
  if (state) queryParams.append('state', state);

  const url = `/api/category_penetration_sellers/?${queryParams.toString()}`;

  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.info('Error fetching category metrics:', error);
    throw error;
  }
}


createSunburstChart('Retail', '2023-11-01', '2024-03-01', null, 'Frozen Snacks');
export async function createSunburstChart(domainName, startDate, endDate, category, subCategory) {
  const SessionStatename = localStorage.getItem('statename');
  let itemMetricsData;

  if (SessionStatename) {
    itemMetricsData = await fetchCategoryMetrics(startDate, endDate, category, subCategory, domainName, SessionStatename);
  } else {
    itemMetricsData = await fetchCategoryMetrics(startDate, endDate, category, subCategory, domainName);
  }
  let filtered = 0
  const { ids, labels, parents, values, percent } = itemMetricsData;

  if (!labels || labels.length === 0) {
    $("#catSubburst_order_summary").html(`
      <div class='nodata d-flex flex-column align-items-center'>
        <i class='mdi mdi-information-outline'></i> 
        No Data to Display
      </div>`);
    return;
  }else {
    $("#catSubburst_order_summary .nodata").remove();
  }
  var data = [{
    type: "sunburst",
    ids: ids,
    labels: labels,
    parents: parents,
    values: values,
    hoverlabel: {
      namelength: 0
    },
    hovertemplate: 'Percent: %{customdata}%<br><span style="font-weight:bold;">Category: %{label}</span>',
    customdata: percent,
    insidetextorientation: 'radial',
    outsidetextfont: { size: 20, color: "#377eb8" },
    textposition: 'inside',
    marker: { line: { width: 2 } },
    'branchvalues': 'total',
    leaf: { opacity: 0.4 },

  }];

  var wds = $("#summary").width() - 50;
  var layout = {
      margin: { l: 0, r: 0, b: 0, t: 0 },
      sunburstcolorway: ["#42b0d8", "#0260A8", "#ffc107", "#19486D", "#00AEEF", "#FF9E40", "#24CD7E"],
      width:  wds,
  };

  var config = {
      displayModeBar: false,
      responsive: true
  };

  Plotly.newPlot('catSubburst_order_summary', data, layout, config).then(() => {
    attachSunburstClickListener('orders');
  });
}

createSunburstChartsellers('Retail', '2023-11-01', '2024-03-01', null, null);
export async function createSunburstChartsellers(domainName, startDate, endDate, category, subCategory) {
  const SessionStatename = localStorage.getItem('statename');
  let itemMetricsData;

  if (SessionStatename) {
    itemMetricsData = await fetchCategorySellersMetrics(startDate, endDate, category, subCategory, domainName, SessionStatename);
  } else {
    itemMetricsData = await fetchCategorySellersMetrics(startDate, endDate, category, subCategory, domainName);
  }

  const { ids, labels, parents, values, percent } = itemMetricsData;

  if (!labels || labels.length === 0) {
    $("#catSubburst_order_summary2").html("<div class='nodata d-flex flex-column align-items-center'><i class='mdi mdi-information-outline'></i> No Data to Display</div>");
    return;
  }else {
    $("#catSubburst_order_summary2 .nodata").remove();
  }

  var data = [{
      type: "sunburst",
      maxdepth: 3,
      ids: ids,
      labels: labels,
      parents: parents,
      values: values,
      hoverlabel: {
        namelength: 0
      },
      hovertemplate: 'Percent: %{customdata}%<br><span style="font-weight:bold;">Category: %{label}</span>',
      customdata: percent,
      insidetextorientation: 'radial',
      outsidetextfont: { size: 20, color: "#377eb8" },
      textposition: 'outside',
      marker: { line: { width: 1 } },
      'branchvalues': 'total',
      leaf: { opacity: 0.4 },
    
  }];
  var wds = $("#summary").width() - 50;

  var layout = {
      margin: { l: 0, r: 0, b: 0, t: 0 },
      sunburstcolorway: ["#42b0d8", "#0260A8", "#ffc107", "#19486D", "#00AEEF", "#FF9E40", "#24CD7E"],
      width: wds,
      // height: "100%"
  };

  var config = {
      displayModeBar: false,
      responsive: true
  };

  Plotly.newPlot('catSubburst_order_summary2', data, layout, config).then(() => {
    attachSunburstClickListener('supply');
  });
}

// window.onresize = function() {
//   Plotly.Plots.resize('catSubburst_order_summary');
//   Plotly.Plots.resize('catSubburst_order_summary2');
// };

export async function fetchDonutChartData(domainName, startDate, endDate, category, subCategory, state) {
  let response;
  try {
      const queryParams = new URLSearchParams({ domainName, startDate, endDate });

      if (category) queryParams.append('category', category);
      if (subCategory) queryParams.append('subCategory', subCategory);
      if (state) queryParams.append('state', state);

      const url = `/api/order_per_state/?${queryParams.toString()}`;
      try {
        response = await fetch(url);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      } catch (error) {
        console.info('Error fetching category metrics:', error);
        throw error;
      }
      const data = await response.json();

      for (let i = 1; i <= 4; i++) {
          const chartElementId = `#stateOrderRang${i}`;
          let donut_data;
          if (i==1){
            donut_data = data['< 1,000'];
          }
          else if(i==2){
            donut_data = data['1,000 - 5,000'];
          }
          else if(i==3){
            donut_data = data['5,000 - 10,000'];
          }
          else{
            donut_data = data['> 10,000'];
          }
          renderOrderRangeChart(donut_data, chartElementId);
          // $('.innerLoader').remove();
      }
  
  } catch (error) {
      console.info('Error fetching data:', error);
  }
}


export async function fetchDonutChartData2(domainName, startDate, endDate, category, subCategory, state) {
  let response;
  try {
      const queryParams = new URLSearchParams({ domainName, startDate, endDate });

      if (category) queryParams.append('category', category);
      if (subCategory) queryParams.append('subCategory', subCategory);
      if (state) queryParams.append('state', state);

      const url = `/api/seller_per_state/?${queryParams.toString()}`;
      try {
        response = await fetch(url);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      } catch (error) {
        console.info('Error fetching category metrics:', error);
        throw error;
      }
      const data = await response.json();
      for (let i = 1; i <= 4; i++) {
          let donut_data;
          const chartElementId = `#stateSellerRang${i}`;
          if (i==1){
            donut_data = data['< 100']
          }
          else if(i==2){
            donut_data = data['100 - 500']

          }
          else if(i==3){
            donut_data = data['500 - 1,000']
          }
          else{
            donut_data = data['> 1,000']
          }
          renderOrderRangeChart(donut_data, chartElementId);
      }
  
  } catch (error) {
      console.info('Error fetching data:', error);
  }
}

function renderOrderRangeChart(data, chart_id) {

if ( document.querySelector(chart_id).hasChildNodes() ) {
      document.querySelector(chart_id).innerHTML = '';
  }
  const stcount = data.length;

  var opd_count = stcount;
  var opd = (opd_count / 36) * 100;

  var stateDonut = {
    series: [opd],
    chart: {
      height: 150,
      type: 'radialBar',
      toolbar: {
        show: false
      }
    },
    plotOptions: {
      radialBar: {
        startAngle: -135,
        endAngle: 225,
        hollow: {
          margin: 0,
          size: '60%',
          background: '#fff',
          position: 'front',
        },
        track: {
          background: '#e5e9f2',
          strokeWidth: '100px',
          margin: 0,
        },
        dataLabels: {
          show: true,
          name: {
            offsetY: 17,
            show: true,
            color: '#8392a5',
            fontSize: '11px'
          },
          value: {
            formatter: function () {
              return parseInt(stcount);
            },
            color: '#001737',
            fontSize: '26px',
            show: true,
            offsetY: -15,
          }
        }
      }
    },
    fill: {
      type: 'gradient',
      gradient: {
        shade: 'dark',
        type: 'horizontal',
        shadeIntensity: 0.5,
        gradientToColors: ['#ABE5A1'],
        inverseColors: true,
        opacityFrom: 1,
        opacityTo: 1,
        stops: [0, 100]
      }
    },
    stroke: {
      lineCap: 'round'
    },
    labels: ['STATES'],
    tooltip: {
      enabled: true,
      custom: function() {
        return `<div class="card bd-0-f tx-11-f">
        <div class="card-header pd-5">State: ${stcount}</div>
        <div class="card-body wd-200 pd-5 tx-11-f text-wrap">${data}</div>
        </div>`;
      },
    },

  
  };

  var chart = new ApexCharts(document.querySelector(chart_id), stateDonut);
  chart.render();
}

let statesData = [];

document.addEventListener('DOMContentLoaded', function() {
    updateLogisticsStateDistricts();
});

function updateLogisticsStateDistricts() {
    fetchDataAndStore();

    document.getElementById('switchState').addEventListener('change', handleRadioChange);
    document.getElementById('switchDistricts').addEventListener('change', handleRadioChange);

};


$("body").on("change",'#filtersByRegion', function() {
  populateDistStateTree()
});

function populateDistStateTree(){
  if (document.getElementById('switchDistricts').checked) {
    let district = $("#filtersByRegion").val();
    let SessionStatename = localStorage.getItem('statename');
    var dateRangeString = document.getElementById('filterDaterange').textContent;

    var dates = dateRangeString.split(' - ');
    var startDateString = dates[0];
    var endDateString = dates[1];
    var category = 'None'
    var sub_category = 'None'
    if (includeCategory){
        category = document.getElementById('categoryDropdown').value;
        sub_category = document.getElementById('subCategoryDropdown').value;
    }

    var startDate = new Date(startDateString);
    var endDate = new Date(endDateString);
   
    var formattedStartDate = formatDateStringDB(startDate);
    var formattedEndDate = formatDateStringDB(endDate);
    loadAndCreateTreeChart('Retail', formattedStartDate, formattedEndDate, category, sub_category,SessionStatename, district);
    $('#filtersByRegion').attr('disabled', false);
}else{
    
    let state_name = $("#filtersByRegion").val();

    var dateRangeString = document.getElementById('filterDaterange').textContent;
    var dates = dateRangeString.split(' - ');
    var startDateString = dates[0];
    var endDateString = dates[1];

    var category = 'None'
    var sub_category = 'None'
    if (includeCategory){
        category = document.getElementById('categoryDropdown').value;
        sub_category = document.getElementById('subCategoryDropdown').value;
    }

    var startDate = new Date(startDateString);
    var endDate = new Date(endDateString);
   
    var formattedStartDate = formatDateStringDB(startDate);
    var formattedEndDate = formatDateStringDB(endDate);

    loadAndCreateTreeChart('Retail', formattedStartDate, formattedEndDate, category, sub_category,state_name);

}
}

function handleRadioChange() {
    if (document.getElementById('switchState').checked) {
        populateDropdownWithStates();
    } else {
        populateDropdownWithDistricts();
    }
}

export function populateStateAndDist(){
  if(document.getElementById('switchState').checked){
    if(localStorage.getItem('statename')){
      var regionValueLocal = localStorage.getItem('statename');
      $("#filtersByRegion").val(regionValueLocal.toLocaleUpperCase())
      $('#filtersByRegion').attr('disabled', true);
    }else{
      $("#filtersByRegion").val(default_state);
      $('#filtersByRegion').attr('disabled', false);
    }
  }else{
    let dist_ = $("#filtersByRegion").val();
    $("#filtersByRegion").val(dist_);
    
  }
}

function fetchDataAndStore() {
  const fetchTreeLoader = $('#treeLoader');
  fetchTreeLoader.html('<div class="innerLoader-dot"></div>')

    fetch('api/state_district_list/')
        .then(response => response.json())
        .then(data => {
            statesData = data;
            handleRadioChange();
            $(".innerLoader-dot").remove()
        })
        .catch(error => {
          console.info('Error fetching data:', error);
        });
}

function populateDropdownWithStates() {

  const dropdown = document.getElementById('filtersByRegion');
  dropdown.innerHTML = '';

  if (statesData.length === 0) {
      const defaultOption = document.createElement('option');
      defaultOption.value = '';
      defaultOption.textContent = 'Select State';
      dropdown.appendChild(defaultOption);
  } else {
      dropdown.innerHTML = `<option value="">Select State</option>` + 
      statesData.map(state => `<option value="${state.name}">${state.name}</option>`).join('');
  }

}


function populateDropdownWithDistricts() {

  const dropdown = document.getElementById('filtersByRegion');
  const selectedStateName = localStorage.getItem('statename').toLocaleUpperCase();
  const selectedState = statesData.find(state => state.name === selectedStateName);
  dropdown.innerHTML = '';
    if (selectedState && selectedState.districts) {
        const uniqueDistricts = new Set();
        selectedState.districts.forEach(district => {
            if (!uniqueDistricts.has(district.name)) {
                uniqueDistricts.add(district.name);
                const option = document.createElement('option');
                option.value = district.name;
                option.textContent = district.name;
                dropdown.appendChild(option);
            }
        });
        populateDistStateTree()

    }

}

var treeData = null;

async function fetchTreeData(domainName, startDate, endDate, category, subCategory, state,district_name) {
  const fetchTreeLoader = $('#treeLoader');
  fetchTreeLoader.html('<div class="innerLoader-dot"></div>')
  fetchTreeLoader.show()

  const queryParams = new URLSearchParams({ startDate, endDate, domainName, category, subCategory, state,district_name });

  if (category) queryParams.append('category', category);
  if (subCategory) queryParams.append('subCategory', subCategory);
  if (state) queryParams.append('state', state.toUpperCase());
  let _url = "";
  if(district_name){
    if (district_name) queryParams.append('district', district_name);
    _url = `/api/top_seller_districts/?${queryParams.toString()}`;
  }else{
    _url = `/api/top_seller_states/?${queryParams.toString()}`;
  }
  
  try {
    const response = await fetch(_url);
    $(".innerLoader-dot").remove()
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.info('Error fetching tree data:', error);
    throw error;
  }
}


async function fetchTopSellerDistrictsData(domainName, startDate, endDate, category, subCategory, districtName) {
  $('#loadingData').html(loaderDiv);

  const queryParams = new URLSearchParams({ startDate, endDate, domainName, category, subCategory, district: districtName });
  const url = `/api/top_seller_districts/?${queryParams.toString()}`;

  try {
      const response = await fetch(url);
      $('#loadingData').remove();
      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
  } catch (error) {
      console.info('Error fetching district data:', error);
      throw error;
  }
}

async function loadTreeData(domainName, startDate, endDate, category, subCategory,state_name,district_name) {
  let SessionStatename = localStorage.getItem('statename');
  if(state_name)
    SessionStatename = state_name
  try {
    if (SessionStatename) {
      treeData = await fetchTreeData(domainName, startDate, endDate, category, subCategory, SessionStatename,district_name);
    } else {
      const state = default_state;
      treeData = await fetchTreeData(domainName, startDate, endDate, category, subCategory, state);

    }
    return treeData;
  } catch (error) {
    console.info('Error loading tree data:', error);
  }
}

export async function loadAndCreateTreeChart(domainName, startDate, endDate, category, subCategory,state_name,district_name) {
  try {
    let treeChartData = await loadTreeData(domainName, startDate, endDate, category, subCategory,state_name,district_name);
    create_chart(treeChartData);
  } catch (error) {
    console.info('Error in loading and creating tree chart:', error);
  }
}

function create_chart(treeData){

  const width_wd = 500;
  d3.select("#inntraDistrictTree").selectAll("*").remove();
  var path = null;
  const margin_mr = { top: 0, right: 0, bottom: 0, left: 80 },
    width_w = width_wd - margin_mr.left - margin_mr.right,
    height_t = 250 - margin_mr.top - margin_mr.bottom;

    if (Object.values(treeData).length === 0) {
    document.querySelector("#inntraDistrictTree").innerHTML = "<div class='nodata d-flex flex-column align-items-center'><i class='mdi mdi-information-outline'></i> No Data to Display</div>";
    return;
  } else {
    $(".nodata").remove();
  }

  var svg_d3 = d3
    .select("#inntraDistrictTree")
    .append("svg")
    .attr("width", width_w + margin_mr.right + margin_mr.left)
    .attr("height", height_t + margin_mr.top + margin_mr.bottom)
    .append("g")
    .attr("class", "intd")
    .attr("transform", "translate(250," + margin_mr.top + ")");
  
    var i = 0,
     duration = 750,
     root;
  
  var treemap = d3.tree().size([height_t, width_w]);
  
  root = d3.hierarchy(treeData, function (d) {
    return d.children;
  });
  root.x0 = height_t / 2;
  root.y0 = 0;
  
  root.children.forEach(collapse);
  
  update(root);
  
  function collapse(d) {
    if (d.children) {
      d._children = d.children;
      d._children.forEach(collapse);
      d.children = null;
    }
  }
  
  function update(source) {
    var treeData = treemap(root);
  
    var nodes = treeData.descendants(),
      links = treeData.descendants().slice(1);
  
    nodes.forEach(function (d) {
      d.y = d.depth * -80;
    });
  
    var node = svg_d3.selectAll("g.node").data(nodes, function (d) {
      return d.id || (d.id = ++i);
    });
  
    var nodeEnter = node
      .enter()
      .append("g")
      .attr("class", "node")
      .attr("transform", function (d) {
        return "translate(" + source.y0 + "," + source.x0 + ")";
      })
      .on("click", click);
  
    nodeEnter
      .append("circle")
      .attr("class", "node")
      .attr("r", 1e-6)
      .style("fill", function (d) {
        return d._children ? "lightgreen" : "#fff";
      });

    nodeEnter
        .append("foreignObject")
        .attr("x", function (d) {
        return -12;
        })
        .attr("y", -12)
        .attr("width", 24)
        .attr("height", 24)
        .attr("class", "node-icon")
        .html(function (d) {
            if (d.depth === 0) {
              return '<i class="mdi mdi-home"></i>';
            } else {
              return '<i class="mdi mdi-truck-delivery-outline"></i>';
            }
          });

    nodeEnter
      .append("text")
      .attr("dy", ".35em")
      .attr("x", function (d) {
        return d.children || d._children ? 20 : -20;
      })
      .attr("text-anchor", function (d) {
        return d.children || d._children ? "start" : "end";
      })
      .text(function (d) {
        return d.data.name;
      });
  
    let nodeUpdate = nodeEnter.merge(node);
  
    nodeUpdate
      .transition()
      .duration(duration)
      .attr("transform", function (d) {
        return "translate(" + d.y + "," + d.x + ")";
      });
  
    nodeUpdate
      .select("circle.node")
      .attr("r", 12)
      .style("fill", function (d) {
        return d._children ? "lightgreen" : "#fff";
      })
      .attr("cursor", "pointer");
  
    let nodeExit = node.exit().transition().duration(duration).attr("transform", function (d) {
      return "translate(" + source.y + "," + source.x + ")";
    }).remove();
  
    nodeExit.select("circle").attr("r", 1e-6);
  
    nodeExit.select("text").style("fill-opacity", 1e-6);

    var link = svg_d3.selectAll("path.link").data(links, function (d) {
      return d.id;
    });
  
    var linkEnter = link
      .enter()
      .insert("path", "g")
      .attr("class", "link")
      .attr("d", function (d) {
        const o = { x: source.x0, y: source.y0 };
        return diagonal(o, o);
      });
  
    var linkUpdate = linkEnter.merge(link);
  
    linkUpdate
      .transition()
      .duration(duration)
      .attr("d", function (d) {
        return diagonal(d, d.parent);
      });
  
    let linkExit = link.exit().transition().duration(duration).attr("d", function (d) {
      const o = { x: source.x, y: source.y };
      return diagonal(o, o);
    }).remove();
  
    nodes.forEach(function (d) {
      d.x0 = d.x;
      d.y0 = d.y;
    });
  
    function diagonal(s, d) {
      path = `M ${s.y} ${s.x}
              C ${(s.y + d.y) / 2} ${s.x},
                ${(s.y + d.y) / 2} ${d.x},
                ${d.y} ${d.x}`;
  
      return path;
    }
  
    function click(d) {
      if (d.children) {
        d._children = d.children;
        d.children = null;
      } else {
        d.children = d._children;
        d._children = null;
      }
      update(d);
    }
  }

  
}

$(document).ready(function() {
    let allData = [];
    let defaultMaxDate;
    if (includeCategory){
        function fetchAndUpdateCategoryList() {
            fetch('/api/categories/')
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
        url: 'api/get-max-date/',
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

function attachSunburstClickListener(graphType) {
  let sunburstChartDiv;
  if (graphType === 'orders') {
    sunburstChartDiv = document.getElementById('catSubburst_order_summary');
  } else {
    sunburstChartDiv = document.getElementById('catSubburst_order_summary2');
  }

  sunburstChartDiv.addEventListener('plotly_sunburstclick', function(e) {
    let clickedSegmentId = e.points[0].id;
    let parentSegmentId = e.points[0].parent;
    const dateRangeString = document.getElementById('filterDaterange').textContent;
    const dates = dateRangeString.split(' - ');
    const startDateString = dates[0];
    const endDateString = dates[1];

    const startDate = new Date(startDateString);
    const endDate = new Date(endDateString);

    $(".dateRangeTitle").html(dateRangeString);

    const formattedStartDate = formatDateStringDB(startDate);
    const formattedEndDate = formatDateStringDB(endDate);
    if (parentSegmentId) {
      const parts = clickedSegmentId.split("-");
      parentSegmentId = parts[0];
      clickedSegmentId = parts[1];

      const catFromDropDown = document.getElementById('categoryDropdown').value;
      const subCatDropDown = document.getElementById('subCategoryDropdown').value;
      if (catFromDropDown === parentSegmentId && subCatDropDown === clickedSegmentId) {
        clickedSegmentId = 'all';

        setSelect2ToBestMatch('#categoryDropdown', parentSegmentId);
        setSelect2ToBestMatch('#subCategoryDropdown', clickedSegmentId);
        $('#categoryDropdown').val(clickedSegmentId).trigger('change');
      } else {
        setSelect2ToBestMatch('#categoryDropdown', parentSegmentId);
        setSelect2ToBestMatch('#subCategoryDropdown', clickedSegmentId);
      }

      main(formattedStartDate, formattedEndDate, parentSegmentId, clickedSegmentId, 'None', 1);
    } else {
      const catFromDropDown = document.getElementById('categoryDropdown').value;
      const subCatDropDown = document.getElementById('subCategoryDropdown').value;
      if (catFromDropDown === clickedSegmentId && subCatDropDown === 'all') {
        clickedSegmentId = 'all';
        $('#categoryDropdown').val('all').trigger('change');
      } else if (catFromDropDown === clickedSegmentId) {
        $('#subCategoryDropdown').val('all').trigger('change');
        $('#categoryDropdown').val(clickedSegmentId).trigger('change');
      } else {
        setSelect2ToBestMatch('#categoryDropdown', clickedSegmentId);
        $('#categoryDropdown').val(clickedSegmentId).trigger('change');
      }
      main(formattedStartDate, formattedEndDate, clickedSegmentId, 'None', 'None', 1);
    }
  });
}


function filterDataForCategory(categoryId, originalData) {
  let categoryData = {};
  categoryData[categoryId] = originalData[categoryId];

  return categoryData;
}

function filterDataForSubCategory(subCategoryId, categoryId, originalData) {
  let subCategoryData = {};
  subCategoryData[subCategoryId] = originalData[categoryId].children.find(child => child.name === subCategoryId);
  return subCategoryData;
}

function setSelect2ToBestMatch(dropdownSelector, searchString) {
  let directMatchValue = null;
  let bestMatch = null;
  let bestMatchValue = null;

  $(dropdownSelector + ' option').each(function() {
      let optionText = $(this).text();
      if (optionText === searchString) {
          directMatchValue = $(this).val();
          return false;
      }

      let match = optionText.match(/^(.*?)\s\(/);
      if (!directMatchValue && match && match[1] === searchString) {
          bestMatch = match[1];
          bestMatchValue = $(this).val();
          return false;
      } else if (!directMatchValue && match?.[1]?.startsWith(searchString) && !bestMatch) {
          bestMatch = match[1];
          bestMatchValue = $(this).val();
      }
  });

  if (directMatchValue !== null) {
      $(dropdownSelector).val(directMatchValue).trigger('change');
  } else if (bestMatchValue !== null) {
      $(dropdownSelector).val(bestMatchValue).trigger('change');
  } else {
      console.log("No matching option found for " + searchString);
  }
}

$('.text-truncate').tooltipOnOverflow();

