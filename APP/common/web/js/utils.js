
const nocasedata = {
st_data:0,
map_order_demand: 0,
map_total_orders_metrics: 0,
map_total_orders_met: 0,

map_tot_item_delivered: 0,
map_total_active_sellers_metrics: 0,
map_total_hyperlocal_delivered: 0,
map_percentage_hyperlocal: 0,
map_total_products_sellers: 0,
map_total_zonal_commerce_metrics: 0,
map_act_pincodes: 0,
}

const metricKeyMap = {
"sellers":[
    {"key":"Total Active Sellers","id":"map_total_active_sellers_metrics"}
],
"orders":[
    {"key":"Total Confirmed Orders ","id":"map_total_orders_metrics"},
],
"pincode":[
    {"key":"Intrastate Percentage","id":"map_total_zonal_commerce_metrics"}
],
}

function getMetricKey(kid){
let metricName = 'Metric';
$.each(metricKeyMap,function(m,lst){
    let findKey = lst.filter(x=>{return x.id==kid});
    if (findKey.length){
        metricName = findKey[0].key

        return metricName
    }

})

return metricName

}

function formatDate(date) {
const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

let day = date.getDate();
let month = months[date.getMonth()];
let year = date.getFullYear();

// Pad day with leading zero if needed
day = day < 10 ? `0${day}` : day;

return `${day}-${month}-${year}`;
}

let currentDate = new Date();
currentDate.setDate(currentDate.getDate() - 1);
let formattedDate = formatDate(currentDate);

$(document).ready(function() {
let allData = [];

function fetchAndUpdateCategoryList() {
    fetch('categories')
        .then(response => response.json())
        .then(data => {
            allData = data;
            updateDropdown('categoryDropdown', data, 'category');
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

function updateSubCategories(selectedCategory) {
    const filteredData = allData.filter(item => item.category === selectedCategory || selectedCategory === 'all');
    updateDropdown('subCategoryDropdown', filteredData, 'sub_category');
}

$('#categoryDropdown').on('change', function() {
    const selectedCategory = this.value;
    updateSubCategories(selectedCategory);
});
//fetchAndUpdateCategoryList();
});


function handleNegativeValue(elementId) {
    var $element = $(elementId + '.negPosValue');
    var content = $element.text().trim();

    if (content.charAt(0) === '-') {
          $element.addClass('tx-danger');
          $element.siblings('span').find('.mdi-arrow-up-bold').removeClass('mdi-arrow-up-bold tx-success').addClass('mdi-arrow-down-bold tx-danger');
          $element.next('.negPosValue').removeClass('tx-success').addClass('tx-danger');
        } else {
          $element.removeClass('tx-danger');
          $element.siblings('span').find('.mdi-arrow-down-bold').removeClass('mdi-arrow-down-bold tx-danger').addClass('mdi-arrow-up-bold tx-success');
          $element.next('.negPosValue').removeClass('tx-danger').addClass('tx-success');
        }
    }

function negativeValue() {
    handleNegativeValue('#items-per-order-change');
    handleNegativeValue('#active-pincodes-change');
    handleNegativeValue('#india-activesellers-change');
    handleNegativeValue('#confirmed-orders-change');
    };


$(document).ready(function () {

async function populateTable(tabId, data, tab_id) {
    var table = $(tabId + " #" + tab_id +" tbody");
    var tableHead = $(tabId + " #" + tab_id +" thead tr");

    table.empty();
    tableHead.empty();

    tabData = JSON.parse(data);

    if (Array.isArray(tabData) && tabData.length > 0) {
        tabData.forEach(function (item, index) {
        var row = "<tr>";
        for (var key in item) {
            if (index === 0) {
            tableHead.append("<th>" + key + "</th>");
            }
            row += "<td class='td-wrap'>" + item[key] + "</td>";
        }
        row += "</tr>";
        table.append(row);
        });
    } else {
        console.error("Data is not an array or is empty.");
    }
}


async function fetchTableData(tabName, startDate, endDate) {

  const fetchTableloader = $('#tableLoader');
  fetchTableloader.html('<div class="innerLoader-dot"></div>')
  fetchTableloader.show()

  var tab_id = $('.table').attr("id")
    if (tab_id === "data-table"){
      const previewLimit = 5;
        const url = `/api/fetch_downloadable_data/?tabName=${encodeURIComponent(
            tabName
        )}&startDate=${encodeURIComponent(startDate)}&endDate=${encodeURIComponent(
            endDate
        )}&previewLimit=${encodeURIComponent(
          previewLimit
      )}`;
        try {
            const response = await fetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
            });
            if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
            }
            $(".innerLoader-dot").remove()
            return await response.json();
        } catch (error) {
            console.error("Error fetching data:", error);
            return [];
        }
    }
    else if (tab_id === 'data-table-b2b'){
      const previewLimit = 5;
        let pathname = window.location.pathname;
        const baseUrl = `${window.location.origin}${window.location.pathname.replace(/\/$/, '')}`;

        const url = `${baseUrl}/fetch_downloadable_data/?tabName=${encodeURIComponent(
            tabName
        )}&startDate=${encodeURIComponent(startDate)}&endDate=${encodeURIComponent(
            endDate
        )}&previewLimit=${encodeURIComponent(
          previewLimit
      )}`;
        try {
            const response = await fetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
            });
            if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
            }
            $(".innerLoader-dot").remove()
            return await response.json();
        } catch (error) {
            console.error("Error fetching data:", error);
            return [];
        }
    }
}


async function fetchTableDataB2B(tabName, startDate, endDate) {

  const fetchTableloader = $('#tableLoader');
  fetchTableloader.html('<div class="innerLoader-dot"></div>')
  fetchTableloader.show()

  var tab_id = $('.table').attr("id")
    if (tab_id === "data-table"){
      const previewLimit = 5;
      let pathname = window.location.pathname;
        const baseUrl = `${window.location.origin}${window.location.pathname.replace(/\/$/, '')}`;
        const url = `${baseUrl}/fetch_downloadable_data/?tabName=${encodeURIComponent(
            tabName
        )}&startDate=${encodeURIComponent(startDate)}&endDate=${encodeURIComponent(
            endDate
        )}&previewLimit=${encodeURIComponent(
          previewLimit
      )}`;
        try {
            const response = await fetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
            });
            if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
            }
            $(".innerLoader-dot").remove()
            return await response.json();
        } catch (error) {
            console.error("Error fetching data:", error);
            return [];
        }
    }
    else if (tab_id === 'data-table-b2b'){
      const previewLimit = 5;
      let pathname = window.location.pathname;
        const baseUrl = `${window.location.origin}${window.location.pathname.replace(/\/$/, '')}`;
        const url = `${baseUrl}/fetch_downloadable_data/?tabName=${encodeURIComponent(
            tabName
        )}&startDate=${encodeURIComponent(startDate)}&endDate=${encodeURIComponent(
            endDate
        )}&previewLimit=${encodeURIComponent(
          previewLimit
      )}`;
        try {
            const response = await fetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
            });
            if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
            }
            $(".innerLoader-dot").remove()
            return await response.json();
        } catch (error) {
            console.error("Error fetching data:", error);
            return [];
        }
    }


}


$('#downloadDataTable a[data-toggle="tab"]').on("shown.bs.tab", async function (e) {
    var tab_id = $('.table').attr("id")
    if (tab_id === "data-table"){
      $("#data-table tbody").html("");

        var tabId = $(e.target).attr("href");
        var tabName = $(e.target).attr("cat").trim();
        var dateRangeString = document.getElementById('filterDaterange').textContent;
        var dates = dateRangeString.split(' - ');
        var startDateString = dates[0];
        var endDateString = dates[1];

        var startDate = new Date(startDateString);
        var endDate = new Date(endDateString);

        startDate = formatDate(startDate);
        endDate = formatDate(endDate);


        var data = await fetchTableData(tabName, startDate, endDate);
        populateTable(tabId, data, tab_id);
    }
    else if (tab_id === "data-table-b2b"){
      $("#data-table-b2b tbody").html("");

        var tabId = $(e.target).attr("href");
        var tabName = $(e.target).attr("cat").trim();
        var dateRangeString = document.getElementById('filterDaterange').textContent;
        var dates = dateRangeString.split(' - ');
        var startDateString = dates[0];
        var endDateString = dates[1];

        var startDate = new Date(startDateString);
        var endDate = new Date(endDateString);

        startDate = formatDate(startDate);
        endDate = formatDate(endDate);


        var data = await fetchTableDataB2B(tabName, startDate, endDate);
        populateTable(tabId, data, tab_id);
    }

});


$('#downloadDataTableB2B a[data-toggle="tab"]').on("shown.bs.tab", async function (e) {
    var tab_id = $('.table').attr("id")
    if (tab_id === "data-table"){
      $("#data-table tbody").html("");

        var tabId = $(e.target).attr("href");
        var tabName = $(e.target).attr("cat").trim();
        var dateRangeString = document.getElementById('filterDaterange').textContent;
        var dates = dateRangeString.split(' - ');
        var startDateString = dates[0];
        var endDateString = dates[1];

        var startDate = new Date(startDateString);
        var endDate = new Date(endDateString);

        startDate = formatDate(startDate);
        endDate = formatDate(endDate);


        var data = await fetchTableData(tabName, startDate, endDate);
        populateTable(tabId, data, tab_id);
    }
    else if (tab_id === "data-table-b2b"){
      $("#data-table-b2b tbody").html("");

        var tabId = $(e.target).attr("href");
        var tabName = $(e.target).attr("cat").trim();
        var dateRangeString = document.getElementById('filterDaterange').textContent;
        var dates = dateRangeString.split(' - ');
        var startDateString = dates[0];
        var endDateString = dates[1];

        startDate = new Date(startDateString);
        endDate = new Date(endDateString);

        startDate = formatDate(startDate);
        endDate = formatDate(endDate);


        var Dnlddata = await fetchTableDataB2B(tabName, startDate, endDate);
        populateTable(tabId, Dnlddata, tab_id);
    }

});


$('#downloadDataBtnModal').on('click', function() {
  var activeTab = $('#downloadDataTable .nav-link.active');
  activeTab.trigger('shown.bs.tab');
  $("#downloadTableData").modal("show")
});

$('#downloadDataBtnModalB2B').on('click', function() {
  var activeTab = $('#downloadDataTableB2B .nav-link.active');
  activeTab.trigger('shown.bs.tab');
  $("#downloadTableDatab2b").modal("show")
});




$("#downloadButton").click(function () {
    var url
    var tabName

  var dateRangeString = document.getElementById('filterDaterange').textContent;
  var dates = dateRangeString.split(' - ');
  var startDateString = dates[0];
  var endDateString = dates[1];

  var startDate = new Date(startDateString);
  var endDate = new Date(endDateString);


  startDate = formatDate(startDate);
  endDate = formatDate(endDate);


    const downloadTablesloader = $('#downloadButton');
    downloadTablesloader.html(`<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
      <span class="">Downloading Data...</span>`);
    $('#downloadButton').attr('disabled', 'disabled');

    controller = new AbortController();
    const signal = controller.signal;
    var tab_name = $('.table').attr("id")
    if (tab_name === "data-table"){
        url = '/api/fetch_downloadable_data'
          tabName = $("#downloadDataTable .nav-link.active").attr("cat").trim();

    }else if(tab_name === "data-table-b2b"){


        url = 'fetch_downloadable_data'
          tabName = $("#downloadDataTableB2B .nav-link.active").attr("cat").trim();

    }
    let pathname = window.location.pathname;
    let baseUrl = `${window.location.origin}${window.location.pathname.replace(/\/$/, '')}`;
    fetch(`${baseUrl}/${url}/?tabName=${encodeURIComponent(tabName)}&startDate=${encodeURIComponent(startDate)}&endDate=${encodeURIComponent(endDate)}`, {
            method: 'GET',
            headers: {
            'Content-Type': 'application/json',
          },
          signal: signal
        })
    .then(function(response) {
        if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(function(data) {
      data = JSON.parse(data);

      if (data.length === 0) {
          console.error('No data available for download.');
          return;
      }

      var columns = Object.keys(data[0]);

      var csv = columns.map(escapeCsvValue).join(',') + '\n';

      data.forEach(function(item) {
          csv += columns.map(function(column) {
              return escapeCsvValue(item[column]);
          }).join(',') + '\n';
      });

      var blob = new Blob([csv], { type: 'text/csv' });

      var url = window.URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `${tabName}_data.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      downloadTablesloader.html("Download Data");
      $('#downloadButton').removeAttr('disabled','disabled');


      function escapeCsvValue(value) {
          if (value && value.toString().includes(',')) {
              return `"${value}"`;
          }
          return value;
      }
  })

    .catch(function(error) {
        console.error('Error triggering download:', error);
    });
    });


});

let controller = null;

$('body').on('click', '#closeDownloadTable', function() {
    if (controller !== null) {
        controller.abort();
        controller = null;
    }
    $('#downloadButton').removeAttr('disabled','disabled');
    $("#downloadTableData").modal("hide")
  });


$('body').on('click', '#closeDownloadTableB2B', function() {
    if (controller !== null) {
        controller.abort();
        controller = null;
    }
    $('#downloadButton').removeAttr('disabled','disabled');
    $("#downloadTableDatab2b").modal("hide")
  });


async function downloadData() {
var tabId = $(e.target).attr("href");
var tabName = $(e.target).attr("cat").trim();

  var dateRangeString = document.getElementById('filterDaterange').textContent;
  var dates = dateRangeString.split(' - ');
  var startDateString = dates[0];
  var endDateString = dates[1];

  // Parse the dates
  var startDate = new Date(startDateString);
  var endDate = new Date(endDateString);

  startDate = formatDate(startDate);
  endDate = formatDate(endDate);
  var data = await fetchTableData(tabName, startDate, endDate);
  populateTable(tabId, data, tab_id);
}


  $(document).ready(function() {
    if ( $(window).width() < 480 ) {
      $('#card-owlCarousel').addClass("owl-carousel")
      $('#collapseFilters').addClass("collapse")
      startCarousel();
    } else {
      $('.owl-carousel').addClass('off');
      $('#collapseFilters').removeClass("collapse");
      $('.mapTitles').removeClass('sticky');
    }

    if ( $(window).width() < 992 ) {
      $('#collapseFilters').addClass("collapse");
    } else {
      $('#collapseFilters').removeClass("collapse");
      $('.mapTitles').removeClass('sticky');
    }

  });


$(window).resize(function () {
    window.resizeEvt;
    clearTimeout(window.resizeEvt);
    window.resizeEvt = setTimeout(function(){
    $('#indiamap-casetype .metric-option.active').trigger("click");
    }, 350);
    if ( $(window).width() < 992 ) {
      $('#collapseFilters').addClass("collapse");
      $('.mapTitles').removeClass('sticky');
      startCarousel();
    } else {
      $('#collapseFilters').removeClass("collapse");
      stopCarousel();
    }
    if ( $(window).width() < 480 ) {
      $('#card-owlCarousel').addClass("owl-carousel");
      startCarousel();
    } else {
      $('#card-owlCarousel').removeClass("owl-carousel");
      stopCarousel();
    }
});

  function startCarousel(){

    $("#card-owlCarousel").owlCarousel({
       navigation : false,
       margin:10,
       autoplay:false,
       items : 1,
       loop:true,
       nav:true,
       dots: false,
    });
  }
  function stopCarousel() {
    var owl = $('#card-owlCarousel');
    owl.trigger('destroy.owl.carousel');
    owl.addClass('off');
  }
