import { statenametostatecode } from './fetchlatest_statejson.js';
import { indiamapdataprocessed } from './indiamap.js';
import { plotStateMap } from './state_map_script.js';
import {
    populateStateAndDist, loadTopStateOrdersChart, loadTopDistrictOrdersChart,
    loadTopStateLogisticsChart, loadTopStateSellersChart,loadTopDistrictSellersChart, loadTopDistrictLogisticsChart,
    createSunburstChart, createSunburstChartsellers, fetchDonutChartData, fetchDonutChartData2, loadAndCreateTreeChart
} from './custom-chart.js';

const width = 1200;
const height = 1200;
const hide_seller = true

let SessionStatename = "Karnataka";
let SessionStatecode = "KA";
localStorage.setItem('statename',SessionStatename);
localStorage.setItem('statecode',SessionStatecode);

// set Date T-1
d3.select("#state-todaydate")
    .text(formattedDate)

var loaders = `<div id="loaders" class="overlay-white""><span class="loader-dot"></span></div>`
const loaderCont = `<div class="loaderBox">
            <div class='loaderMix'>
                <div class='loader--dot'></div>
                <div class='loader--dot'></div>
                <div class='loader--dot'></div>
                <div class='loader--dot'></div>
                <div class='loader--dot'></div>
                <div class='loader--dot'></div>
                <div class='loader--text'></div>
            </div>
            <div class="overlay-white"></div>
        </div>`

const svg = d3.select('#indiamap')
    svg.attr("preserveAspectRatio", "xMinYMin meet")

localStorage.clear()
localStorage.setItem('chart-st-code', 'TT')

let a = new Date()
d3.select("#todaydate")
    .text(`${a.getDate()}/${a.getMonth() + 1}/${a.getFullYear()}`)


let map_state_data = null;
let map_statewise_data = null;
let top_cards_data = null;
let datajson = null;


const months = {
    'January': 0, 'February': 1, 'March': 2, 'April': 3, 'May': 4, 'June': 5, 'July': 6,
    'August': 7, 'September': 8, 'October': 9, 'November': 10, 'December': 11
}
function formatDate(date) {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2) 
        month = '0' + month;
    if (day.length < 2) 
        day = '0' + day;

    return [year, month, day].join('-');
}



function formatDateStringDB(inputDateStr) {
    let dateObj = new Date(inputDateStr);

    let year = dateObj.getFullYear();
    let month = (dateObj.getMonth() + 1).toString().padStart(2, '0'); // Adding 1 because getMonth() returns 0-11
    let day = dateObj.getDate().toString().padStart(2, '0');

    return `${year}-${month}-${day}`;
}

function mapprojection(data) {
    const el = document.getElementById("indiamap")
    const height = el.clientHeight
    const width = el.clientWidth
    const projection = d3.geoMercator();
    const pathGenerator = d3.geoPath().projection(projection);

    projection.scale(1).translate([0, 0])

    const b = pathGenerator.bounds(data),
        s = 0.95 / Math.max((b[1][0] - b[0][0]) / width, (b[1][1] - b[0][1]) / height),
        t = [(width - s * (b[1][0] + b[0][0])) / 2, (height - s * (b[1][1] + b[0][1])) / 2];
    
    projection.scale(s).translate(t);
    return [projection, pathGenerator]
}



const bubblecolormapper = {
    map_total_active_sellers_metrics: ["rgba(0,123,255,0.8)", "rgba(0,123,255,0.5)", "rgba(0,123,255,0.5)"],
    map_total_orders_metrics: ["rgba(227, 87, 10,0.8)", "rgba(227, 87, 10,0.4)", "rgba(227, 87, 10,0.4)"],
    map_total_zonal_commerce_metrics: ["rgba(16,183,89,0.8)", "rgba(16,183,89,0.5)", "rgba(16,183,89,0.5)"],
}

$(document).on('change', '.statelist', function() {
    updateStateData();
  });
  $('#switchDistricts').prop('disabled',true);



async function showIndiaMap(statemap_geojson, maxdata, metric_selected){

    var category = 'None'
    var sub_category = 'None'
    $(".changeStbtn").hide();
    $(".indiaMaps").show();
    $(".stateMaps").hide();
    $(".mapTitle").hide();
    $(".mapStyles").show();
    $(".order-range").show();
    $("#statemap-viz").hide();
    $("#indiaMapTitle").html("INDIA");
    $(".topstates").html("Top 3 States");
    $(".topdistricts").html("Top 3 Districts");
    $("#india-state-map-btn").trigger("click");
    $("#chloro-viz-btn").trigger("click");
    localStorage.clear();
    localStorage.setItem('chart-st-code', 'TT');
    $('#switchDistricts').prop('disabled', true);
    $('#switchState').prop('disabled', false);
    $('#switchState').trigger("click");

    populateStateAndDist();
    $('#filtersByRegion').attr('disabled', false);
    if (hide_seller==true){

        $('#active-sellers-metrics-btn').prop("disabled", false);
        $('#active-sellers-metrics-btn').removeClass("op-3");

        $('#supply-tab').prop("disabled", false);
        $('#supply-tab').removeClass("op-3");
    }

    var dateRangeString = document.getElementById('filterDaterange').textContent;
    var dates = dateRangeString.split(' - ');
    var startDateString = dates[0];
    var endDateString = dates[1];

    var startDate = new Date(startDateString);
    var endDate = new Date(endDateString);
    if (includeCategory){
        category = document.getElementById('categoryDropdown').value;
        sub_category = document.getElementById('subCategoryDropdown').value;
    }
    $(".dateRangeTitle").html(dateRangeString);

    var start_date = formatDate(startDate);
    var end_date = formatDate(endDate);

    let selected_metric = $('.metric-option.active').attr('value');
    updateTopCardsDelta(top_cards_data['top_card_data']['TT'], top_cards_data['prev_date_range'] )

    if (selected_metric === 'map_total_orders_metrics') {
    if (includeCategory) {
            await Promise.all([
                loadTopStateOrdersChart('Retail', start_date, end_date, category, sub_category, 'None'),
                loadTopDistrictOrdersChart('None', start_date, end_date, category, sub_category, 'None'),
                createSunburstChart('Retail', start_date, end_date, category, sub_category, 'None'),
                fetchDonutChartData('Retail', start_date, end_date, category, sub_category, 'None'),
                loadMaxOrders('Retail', start_date, end_date, category, sub_category),
            ]);
        }else{
            await Promise.all([
                loadTopStateOrdersChart('Retail', start_date, end_date, category, sub_category, 'None'),
                loadTopDistrictOrdersChart('None', start_date, end_date, category, sub_category, 'None'),
                fetchDonutChartData('Retail', start_date, end_date, category, sub_category, 'None'),
                loadMaxOrders('Retail', start_date, end_date, category, sub_category),
            ]);
        }
        
    } else if (selected_metric === 'map_total_active_sellers_metrics') {
        if (includeCategory) {
            await Promise.all([
                loadTopStateSellersChart('Retail', start_date, end_date, category, sub_category, 'None'),
                loadTopDistrictSellersChart('None', start_date, end_date, category, sub_category, 'None'),
                createSunburstChartsellers('Retail', start_date, end_date, category, sub_category, 'None'),
                fetchDonutChartData2('Retail', start_date, end_date, category, sub_category, 'None'),
                loadMaxSellers('Retail', start_date, end_date, category, sub_category)
            ]);
        }else{
            await Promise.all([
                loadTopStateSellersChart('Retail', start_date, end_date, category, sub_category, 'None'),
                loadTopDistrictSellersChart('None', start_date, end_date, category, sub_category, 'None'),
                fetchDonutChartData2('Retail', start_date, end_date, category, sub_category, 'None'),
                loadMaxSellers('Retail', start_date, end_date, category, sub_category)
            ]);
        }
    } else if (selected_metric === 'map_total_zonal_commerce_metrics') {
        await Promise.all([
            loadTopStateLogisticsChart('Retail', start_date, end_date, category, sub_category, 'None'),
            loadTopDistrictLogisticsChart('None', start_date, end_date, category, sub_category, 'None'),
            loadAndCreateTreeChart('Retail', start_date, end_date, category, sub_category, 'MAHARASHTRA'),
        ]);
        
    }
    negativeValue();

}


async function hideIndiaMap(statename){

    var category = 'None'
    var sub_category = 'None'
    $(".changeStbtn").show();
    $(".indiaMaps").hide();
    $(".stateMaps").show();
    $(".mapTitle").show();
    $(".mapStyles").hide();
    $(".order-range").hide();
    $("#statemap-viz").show();
    $("#indiaMapTitle").html(statename);
    $(".topstates").html(statename);
    $(".topdistricts").html("Top 3 Districts of "+ statename);
    $(".tooltip").tooltip("hide");
    var dateRangeString = document.getElementById('filterDaterange').textContent;
    var dates = dateRangeString.split(' - ');
    var startDateString = dates[0];
    var endDateString = dates[1];
    if (includeCategory){
        category = document.getElementById('categoryDropdown').value;
        sub_category = document.getElementById('subCategoryDropdown').value;
    }
    $(".dateRangeTitle").html(dateRangeString);

    var startDate = new Date(startDateString);
    var endDate = new Date(endDateString);

    var start_date = formatDate(startDate);
    var end_date = formatDate(endDate);

    let metric_selected = $('.metric-option.active').attr('value');
    const SessionStatecode = localStorage.getItem('statecode');
    if (SessionStatecode) {
        updateTopCardsDelta(top_cards_data['top_card_data'][SessionStatecode], top_cards_data['prev_date_range'])
        }
    if (metric_selected === 'map_total_orders_metrics') {
        if (includeCategory){
            await Promise.all([
                    loadTopStateOrdersChart('Retail', start_date, end_date, category, sub_category, statename),
                    loadTopDistrictOrdersChart('None', start_date, end_date, category, sub_category, statename),
                    createSunburstChart('Retail', start_date, end_date, category, sub_category, statename),
                    loadMaxOrders('Retail', start_date, end_date, category, sub_category),
                ]);
        }else{
            await Promise.all([
                    loadTopStateOrdersChart('Retail', start_date, end_date, category, sub_category, statename),
                    loadTopDistrictOrdersChart('None', start_date, end_date, category, sub_category, statename),
                    loadMaxOrders('Retail', start_date, end_date, category, sub_category),
                ]);
        }

        
    } else if (metric_selected === 'map_total_active_sellers_metrics') {
        if (includeCategory){
            await Promise.all([
                loadTopStateSellersChart('Retail', start_date, end_date, category, sub_category, statename),
                loadTopDistrictSellersChart('None', start_date, end_date, category, sub_category, statename),
                createSunburstChartsellers('Retail', start_date, end_date, category, sub_category, statename),
                loadMaxSellers('Retail', start_date, end_date, category, sub_category)
            ]);
        }else{
            await Promise.all([
                    loadTopStateSellersChart('Retail', start_date, end_date, category, sub_category, statename),
                    loadTopDistrictSellersChart('None', start_date, end_date, category, sub_category, statename),
                    loadMaxSellers('Retail', start_date, end_date, category, sub_category)
                ]);
        }

    } else if (metric_selected === 'map_total_zonal_commerce_metrics') {
        await Promise.all([
            loadTopStateLogisticsChart('Retail', start_date, end_date, category, sub_category, statename),
            loadTopDistrictLogisticsChart('None', start_date, end_date, category, sub_category, statename),
            loadAndCreateTreeChart('Retail', start_date, end_date, category, sub_category, statename),
        ]);
        
    }
    negativeValue();

    $('#switchDistricts').prop('disabled',false);
    populateStateAndDist()
    setTimeout(function(){
    },1000)
}

$("body").on("click",".changeStbtn",function(){
    showIndiaMap();
    $(".tooltip").tooltip("hide");
})

function setstatename(d, i) {
    let metric_selected = $('.metric-option.active').attr('value');
    if (metric_selected === 'map_total_orders_metrics' || metric_selected === 'map_total_zonal_commerce_metrics') { 
        localStorage.setItem('statename', i.properties.st_nm)
        localStorage.setItem('statecode', statenametostatecode[i.properties.st_nm])
        updateStateData( i.properties.st_nm,statenametostatecode[i.properties.st_nm])

        if (hide_seller==true){
            $('#active-sellers-metrics-btn').prop("disabled", true);
            $('#active-sellers-metrics-btn').addClass("op-3");
            $('#supply-tab').prop("disabled", true);
            $('#supply-tab').addClass("op-3");
        }
        hideIndiaMap( i.properties.st_nm)

    } else {
        $(".clickinfo").remove();
        $("#indiamap-casetype").append("<p class='clickinfo mg-t-10 tx-10 tx-danger'>**State click is not available on Active Seller</p>")
    }
}

function statebubblemap(statemap_geojson, maxdata, casetype) {
    const mapprojectionresult = mapprojection(statemap_geojson);

    const color = d3.scaleSequentialLog(chloroplethcolormapper2[casetype]).domain([1, maxdata[casetype]]);

    const iconWidth = 35
    const iconHeight = 35

    const bubbleradius = d3.scaleSqrt()
        .domain([0, maxdata[casetype]])
        .range([3, 40]);

    const sorteddata = statemap_geojson.features.sort((a, b) => b.properties.totalcasedata[casetype]);
    const top3Data = sorteddata.slice(0, 3);

    const g = d3.select('#india-bubble');
    
    // Append circles for the bubble map
    g.selectAll('circle')
        .data(sorteddata)
        .enter()
        .append('circle')
        .attr('cx', (el) => mapprojectionresult[0](d3.geoCentroid(el))[0])
        .attr('cy', (el) => mapprojectionresult[0](d3.geoCentroid(el))[1])
        // .attr('r', (el) => bubbleradius(el.properties.totalcasedata[casetype]))
        .attr('r', (el) => {
            const value = el.properties.totalcasedata[casetype];
            return value ? Math.min(40, Math.max(3, bubbleradius(value))) : 3;
        })
        .attr('stroke', bubblecolormapper[casetype][0])
        .attr('fill', bubblecolormapper[casetype][0])
        .attr('fill-opacity', 0.25)
        .attr('stroke-width', 2)
        .attr("data-title", (i) => {
            const value = i.properties.totalcasedata[casetype];
            return `State: ${i.id}<br/> ${getMetricKey(casetype)} : ${
                (getMetricKey(casetype) === "Total Active Sellers" && (value <= 0 || value < 3)) ? 'No data available' :
                    (getMetricKey(casetype) === "Intrastate Percentage" ?
                        `${value}%` :
                        `${value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")}`
                    )
            }`;
        })
        .on('mouseover', function (event, d) {
            d3.select(this)
                .attr("fill-opacity", 1)
                .attr('stroke', bubblecolormapper[casetype][1])
            handleMouseover.call(this, event, d, casetype, color, top3Data);
        })
        .on('mouseout', function (d, i) {
            d3.select(this).attr("fill-opacity", 0.25).attr('stroke', bubblecolormapper[casetype][0]);
            // hideTooltip();
            // $(".tooltip").tooltip("hide");
        })
        .on('click', setstatename);


    d3.select('#india-chloro').select('.icon-container').remove();
    d3.select('#india-bubble').select('.icon-container').remove();
    const iconContainer = d3.select('#india-bubble').append('g');
    iconContainer.html('');

    iconContainer
        .attr('class', 'icon-container')
        .style('fill', 'transparent')

    iconContainer.selectAll('.topstMapIcon')
        .data(top3Data)
        .enter()
        .filter((i) => i.properties.totalcasedata[casetype] > 0)
        .append('foreignObject')
        .attr('x', (el) => mapprojectionresult[0](d3.geoCentroid(el))[0] - iconWidth / 2)
        .attr('y', (el) => mapprojectionresult[0](d3.geoCentroid(el))[1] - 40)
        .attr('width', iconWidth)
        .attr('height', iconHeight)
        .attr('overflow', 'visible')
        .html((i) => {
            const metricText = getMetricKey(casetype);
            let iconClass;
            let metricValue;
        
            if (metricText === "Total Active Sellers") {
                iconClass = "mdi mdi-account";
                metricValue = i.properties.totalcasedata[casetype];
            } else if (metricText === "Intrastate Percentage") {
                iconClass = "mdi mdi-truck-delivery";
                metricValue = `${i.properties.totalcasedata[casetype]}%`;
            } else {
                iconClass = "mdi mdi-cart-variant";
                metricValue = i.properties.totalcasedata[casetype];
            }
            return `<div class="pointer" data-toggle="tooltip" data-placement="top" data-html="true" title="State: ${i.id}<br/>${metricText}: ${metricValue.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")}"><i class="${iconClass}"></i></div><div class="pulse"></div>`;
        });
    // Tooltip initialization
    $("circle").tooltip({
        container: 'body',
        html: true,
        placement: 'top'
    });

    bubbleLegend(casetype, maxdata[casetype], bubbleradius);
    d3.select('#india-chloro').select('.icon-container').remove();
    $('[data-toggle="tooltip"]').tooltip();

}

function bubbleLegend(casetype, maxdata, bubbleradius) {
    const legendContainer = d3.select('#mapLegends');
    legendContainer.html('');

    const legendData = [
        { label: 'Low', radius: bubbleradius(0), value: 0, color: bubblecolormapper[casetype][0] },
        { label: 'Medium', radius: bubbleradius(maxdata * 0.5), value: Math.floor(maxdata * 0.5), color: bubblecolormapper[casetype][0] },
        { label: 'High', radius: bubbleradius(maxdata), value: Math.floor(maxdata), color: bubblecolormapper[casetype][1] }
    ];

    const newLegendContainer = legendContainer.append('svg')
        .attr('class', 'legend')
        .attr('width', 150)
        .attr('height', 120)

    const legendItems = newLegendContainer.selectAll('g')
        .data(legendData)
        .enter().append('g')
        .attr('class', 'legend-item')
        .attr('transform',`translate(20, 80)`); 

    legendItems.append('circle')
        .attr('cx', 30)
        .attr('cy', (d, i) => `${30 - (i * 15)}`)
        .attr('r', (d, i) => `${i * (1 * 15) + 5}`)
        .attr('fill', 'transparent')
        .attr('stroke', d => d.color)
        .attr('stroke-width', 2);

    legendItems.append('line')
        .attr('x1', (d, i) => `${35 + (i * 15)}`)
        .attr('x2', 90)
        .attr('y1', (d, i) => `${30 - (i * 15)}`)
        .attr('y2', (d, i) => `${30 - (i * 15)}`)
        .attr('stroke', 'black')
        .style('stroke-dasharray', '2,2');

    legendItems.append('text')
        .attr('x', 95)
        .attr('y', (d, i) => `${30 - (i * 15)}`)
        .attr('dy', '.35em')
        .style('text-anchor', 'start')
        .text(d => {
            if (casetype === 'map_total_zonal_commerce_metrics') {
                return `${d.label}: ${d.value.toLocaleString()}%`;
            } else if (casetype === 'map_total_active_sellers_metrics' && d.value < 3) {
                return `${d.label}: No Data`;
            } else {
                return `${d.label}: ${d.value.toLocaleString()}`;
            }
        });
}


function districtbubblemap(districtmap_geojson, maxdata, casetype) {

    const mapprojectionresult = mapprojection(districtmap_geojson)
    const color = d3.scaleSequentialLog(chloroplethcolormapper3[casetype]).domain([1, maxdata[casetype]]);

    const iconWidth = 35
    const iconHeight = 35

    const bubbleradius = d3.scaleSqrt()
        .domain([0, maxdata[casetype]])
        .range([3, 40]);

    const sorteddata = districtmap_geojson.features.sort((a, b) => b.properties.totalcasedata[casetype] - a.properties.totalcasedata[casetype]);
    const top3Data = sorteddata.slice(0, 3);


    const g = d3.select('#india-bubble')
    g.selectAll('circle')
        .data(sorteddata)
        .enter()
        .append('circle')
        .attr('cx', (el) => mapprojectionresult[0](d3.geoCentroid(el))[0])
        .attr('cy', (el) => mapprojectionresult[0](d3.geoCentroid(el))[1])
        // .attr('r', (el) => bubbleradius(el.properties.totalcasedata[casetype]))
        .attr('r', (el) => {
            const value = el.properties.totalcasedata[casetype];
            return value ? Math.min(40, Math.max(3, bubbleradius(value))) : 3;
        })
        .attr('stroke', bubblecolormapper[casetype][0])
        .attr('fill', bubblecolormapper[casetype][0])
        .attr('fill-opacity', 0.15)
        .attr('stroke-width', 1)
        .attr("data-title", (i) => {
            const value = i.properties.totalcasedata[casetype];
            return `State: ${i.properties.st_nm}<br/> District : ${i.properties.district}<br/> ${getMetricKey(casetype)} : ${
                (getMetricKey(casetype) === "Total Active Sellers" && (value <= 0 || value < 3)) ? 'No data available' :
                    (getMetricKey(casetype) === "Intrastate Percentage" ?
                        `${value}%` :
                        `${value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")}`
                    )
            }`;
        })
        .on('mouseover', function (event, d) {
            d3.select(this)
                .attr("fill-opacity", 1)
                .attr('stroke', bubblecolormapper[casetype][1])
            handleMouseover2.call(this, event, d, casetype, color, top3Data);
        })
        .on('mouseout', function (d, i) {
            d3.select(this).attr("fill-opacity", 0.25).attr('stroke', bubblecolormapper[casetype][0]);
            hideTooltip();
            $(".tooltip").tooltip("hide");
        })
        .on('click', setstatename);

        
    d3.select('#india-bubble').select('.icon-container').remove();
    const iconContainer = d3.select('#india-bubble').append('g');
    iconContainer.html('');

    iconContainer
        .attr('class', 'icon-container')
        .style('fill', 'transparent')

    iconContainer.selectAll('.topstMapIcon')
        .data(top3Data)
        .enter()
        .filter((i) => i.properties.totalcasedata[casetype] > 0) // Filter out data points with values <= 0
        .append('foreignObject')
        .attr('x', (el) => mapprojectionresult[0](d3.geoCentroid(el))[0] - iconWidth / 2)
        .attr('y', (el) => mapprojectionresult[0](d3.geoCentroid(el))[1] - 40)
        .attr('width', iconWidth)
        .attr('height', iconHeight)
        .attr('overflow', 'visible')
        .html((i) => {
            const metricText = getMetricKey(casetype);
            let iconClass;
            let metricValue;
        
            if (metricText === "Total Active Sellers") {
                iconClass = "mdi mdi-account";
                metricValue = i.properties.totalcasedata[casetype];
            } else if (metricText === "Intrastate Percentage") {
                iconClass = "mdi mdi-truck-delivery";
                metricValue = `${i.properties.totalcasedata[casetype]}%`;
            } else {
                iconClass = "mdi mdi-cart-variant";
                metricValue = i.properties.totalcasedata[casetype];
            }
            return `<div class="pointer" data-toggle="tooltip" data-placement="top" data-html="true" title="State: ${i.properties.st_nm}</br>Districts: ${i.properties.district}</br>${metricText}: ${metricValue.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")}"><i class="${iconClass}"></i></div><div class="pulse"></div>`;
        });

    $("circle").tooltip({
        container: 'body',
        html: true,
        placement: 'top'
    });
    
    bubbleLegend(casetype, maxdata[casetype], bubbleradius);
    d3.select('#india-chloro').select('.icon-container').remove();
    $('[data-toggle="tooltip"]').tooltip();
}


const chloroplethcolormapper = {
    map_total_orders_metrics: [d3.interpolateOranges, "rgba(255,7,58,0.5)"],
    map_total_active_sellers_metrics: [d3.interpolateBlues, "rgba(0,123,255,0.5)"], 
    map_total_zonal_commerce_metrics: [d3.interpolateGreens, "rgba(255,7,58,0.5)"],
}

var chloroplethcolormapper2 = {
    map_total_orders_metrics:["#ffffff", "#f9f0e9", "#FF7722"],
    map_total_active_sellers_metrics: ["#ffffff", "#dfebf5", "#1c75bc"], 
    map_total_zonal_commerce_metrics: ["#ffffff", "#eefaf3", "#10b759"],
}
var chloroplethcolormapper3 = {
    map_total_orders_metrics:["#ffffff", "#FF7722"],
    map_total_active_sellers_metrics: ["#ffffff", "#1c75bc"], 
    map_total_zonal_commerce_metrics: ["#ffffff", "#10b759"],
}

// Define custom color range function
// function customColorRange(value, max) {
//     const step = max / 4;
//     let selectedMetric = $('.metric-option.active').attr('value');
//     if (value === 0) return "#ffffff";
//     switch (selectedMetric) {
//         case "map_total_orders_metrics":
//             return value <= step ? "#fffdda" :
//                    value <= 2 * step ? "#ffce96" :
//                    value <= 3 * step ? "#fe9c53" :
//                    "#ff6c12";
//         case "map_total_active_sellers_metrics":
//             return value <= step ? "#e9f8ff" :
//                     value <= 2 * step ? "#a6d8ff" :
//                     value <= 3 * step ? "#d0d1e6" :
//                     value <= 4 * step ? "#42b7c5" :
//                     value <= 5 * step ? "#01acc8" :
//                     value <= 6 * step ? "#036f93" :
//                    "#2171b5";
//         case "map_total_zonal_commerce_metrics":
//             return value <= step ? "#d1eb8d" :
//                    value <= 2 * step ? "#c0e481" :
//                    value <= 3 * step ? "#afe176" :
//                    value <= 4 * step ? "#70aa5c" :
//                    value <= 5 * step ? "#90b571" :
//                    value <= 6 * step ? "#b0c086" :
//                    "#eaf598";
//         default:
//             return "#ffffff";
//     }
// }







function statechloromap(statemap_geojson, maxdata, casetype) {

    const mapprojectionresult = mapprojection(statemap_geojson);
    const color = d3.scaleSequentialLog(chloroplethcolormapper3[casetype]).domain([1, maxdata[casetype]]);

    const iconWidth = 35
    const iconHeight = 35

    const g = d3.select('#india-chloro');

    const sortedData = statemap_geojson.features.sort((a, b) => b.properties.totalcasedata[casetype] - a.properties.totalcasedata[casetype]);
    const top3Data = sortedData.slice(0, 3);

    let customColorRange;
    const metricText = getMetricKey(casetype);
    if (metricText === "map_total_zonal_commerce_metrics") {
        if (maxdata[casetype] === 0) {
        customColorRange = d3.scaleSequentialLog()
            .domain([0.1, 0.1])
            .range(["#ffffff", "#ffffff"]);
        } else {
            customColorRange = d3.scaleSequentialLog()
                .domain([0.1, maxdata[casetype]])
                .range(chloroplethcolormapper3[casetype]);
        }
    } else {
        customColorRange = d3.scaleLinear()
        .domain([0, 1, maxdata[casetype]])
        .range(chloroplethcolormapper2[casetype]);
    }
    // Append paths for the chloro map
    g.selectAll('path')
        .data(statemap_geojson.features)
        .enter()
        .append('path')
        .attr('d', (data) => mapprojectionresult[1](data))
        // .attr('fill', (el) => customColorRange(el.properties.totalcasedata[casetype]))
        .attr('fill', (el) => customColorRange(el.properties.totalcasedata[casetype], maxdata[casetype]))
        .attr('stroke-width', 0.5)
        .attr('stroke', 'black')
        .attr('class', 'country')
        .attr("data-title", (i) => {
            const value = i.properties.totalcasedata[casetype];
            return `State: ${i.id}<br/> ${getMetricKey(casetype)} : ${
                (getMetricKey(casetype) === "Total Active Sellers" && (value <= 0 || value < 3)) ? 'No data available' :
                    (getMetricKey(casetype) === "Intrastate Percentage" ?
                        `${value}%` :
                        `${value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")}`
                    )
            }`;
        })
        .on('mouseover', function (event, d) {
            handleMouseover.call(this, event, d, casetype, color, top3Data);
            d3.select(this).attr('stroke-width', 2);
        })
        .on('mouseout', function () {
            d3.select(this).attr('stroke-width', 0.5);
            hideTooltip();
            $(".tooltip").tooltip("hide");
        })
        .on('click', setstatename);

    d3.select('#india-bubble').select('.icon-container').remove();
    d3.select('#india-chloro').select('.icon-container').remove();
    const iconContainer = d3.select('#india-chloro').append('g');
    iconContainer.html('');

    iconContainer
        .attr('class', 'icon-container')
        .style('fill', 'transparent')

    iconContainer.selectAll('.topstMapIcon')
        .data(top3Data)
        .enter()
        .filter((i) => i.properties.totalcasedata[casetype] > 0) // Filter out data points with values <= 0
        .append('foreignObject')
        .attr('x', (el) => mapprojectionresult[0](d3.geoCentroid(el))[0] - iconWidth / 2 + 5)
        .attr('y', (el) => mapprojectionresult[0](d3.geoCentroid(el))[1] - 40)
        .attr('width', iconWidth)
        .attr('height', iconHeight)
        .attr('overflow', 'visible')
        .html((i) => {
            const metricText = getMetricKey(casetype);
            let iconClass;
            let metricValue;
        
            if (metricText === "Total Active Sellers") {
                iconClass = "mdi mdi-account";
                metricValue = i.properties.totalcasedata[casetype];
            } else if (metricText === "Intrastate Percentage") {
                iconClass = "mdi mdi-truck-delivery";
                metricValue = `${i.properties.totalcasedata[casetype]}%`;
            } else {
                iconClass = "mdi mdi-cart-variant";
                metricValue = i.properties.totalcasedata[casetype];
            }
        
            return `<div class="pointer" data-toggle="tooltip" data-placement="top" data-html="true" title="State: ${i.id}<br/>${metricText}: ${metricValue.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")}"><i class="${iconClass}"></i></div><div class="pulse"></div>`;
        });    
    $("path").tooltip({
        container: 'body',
        html: true,
        placement: 'top'
    });

    addLegend(customColorRange, casetype, maxdata[casetype]);
    $('[data-toggle="tooltip"]').tooltip();
}

function addLegend(customColorRange, casetype, maxdata) {
    const legendContainer = d3.select('#mapLegends');
    legendContainer.html('');

    const legendValues = [0, ...Array.from({ length: 4 }, (_, i) => (i + 1) * maxdata / 4)];

    const newLegendContainer = legendContainer.append('svg')
        .attr('class', 'legend')
        .attr('width', 20)
        // .attr('height', 200);

    newLegendContainer.append('text')
        .attr('x', 0)
        .attr('y', 10)
        .attr('transform', 'translate(0, 0)')
        .style('text-anchor', 'start')
        .style('fill', 'black')
        .text(`${getMetricKey(casetype)}`);

    const legend = newLegendContainer.selectAll('g')
        .data(legendValues)
        .enter()
        .append('g')
        .attr('class', 'legend')
        .attr('transform', (d, i) => `translate(0, ${i * (200 / 9) + 20})`);

    legend.append('rect')
        .attr('width', 18)
        .attr('height', 18)
        .style('stroke', 'black')
        .style('stroke-width', '1px')
        .style('fill', (d) => customColorRange(d, maxdata)); 

    legend.append('text')
        .attr('x', 25)
        .attr('y', 9)
        .attr('dy', '.35em')
        .style('text-anchor', 'start')
        .text((d, i) => {
            const startRange = i === 0 ? '0' : Math.floor(legendValues[i - 1]) + 1;
            const endRange = Math.floor(d);
    
            if (casetype === "map_total_zonal_commerce_metrics") {
                if (i === 0) {
                    return startRange.toLocaleString();
                } else if (i === 1) {
                    return `< ${endRange.toLocaleString()}%`;
                } else if (i === legendValues.length - 1) {
                    return `> ${endRange.toLocaleString()}%`;
                } else {
                    return `${startRange.toLocaleString()}%-${endRange.toLocaleString()}%`;
                }
            } else if (casetype === "map_total_active_sellers_metrics" && d === 0) {
                return 'No Data';
            } else {
                if (i === 0) {
                    return startRange.toLocaleString();
                } else if (i === 1) {
                    return `< ${endRange.toLocaleString()}`;
                } else if (i === legendValues.length - 1) {
                    return `> ${startRange.toLocaleString()}`;
                } else {
                    return `${startRange.toLocaleString()}-${endRange.toLocaleString()}`;
                }
            }
        });

    legend.attr('transform', (d, i) => `translate(0, ${i * (200 / 9) + 20})`);
    
    }


function districtchloromap(districtmap_geojson, maxdata, casetype) {
    let mapprojectionresult = mapprojection(districtmap_geojson)

    let color = d3.scaleSequentialLog(chloroplethcolormapper3[casetype]).domain([1, maxdata[casetype]])

    const iconWidth = 35
    const iconHeight = 35

    const sortedData = districtmap_geojson.features.sort((a, b) => b.properties.totalcasedata[casetype] - a.properties.totalcasedata[casetype]);
    const top3Data = sortedData.slice(0, 3);
    const customColorRange = d3.scaleLinear()
    .domain([0, 1, maxdata[casetype]])
    .range(chloroplethcolormapper2[casetype]); 
    const g = d3.select('#india-chloro')

    g.selectAll('path')
        .data(districtmap_geojson.features)
        .enter()
        .append('path')
        .attr('d', (data) => mapprojectionresult[1](data))
        .attr('fill', (el) => customColorRange(el.properties.totalcasedata[casetype]))
        .attr('stroke-width', 0.2)
        .attr('stroke', 'black')
        .attr('class', 'district')
        .attr("data-title", (i) => {
                const value = i.properties.totalcasedata[casetype];
                let metricValue;

                if (getMetricKey(casetype) === "Total Active Sellers" && (value <= 0 || value < 3)) {
                    metricValue = 'No data available';
                } else if (getMetricKey(casetype) === "Intrastate Percentage") {
                    metricValue = `${value}%`;
                } else {
                    metricValue = value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
                }

                return `State: ${i.properties.st_nm}<br/> District : ${i.properties.district}<br/> ${getMetricKey(casetype)} : ${metricValue}`;
            })

        .on('mouseover', function (event, d) {
            handleMouseover2.call(this, event, d, casetype, color, top3Data);
            d3.select(this).attr('stroke-width', 2);
        })
        .on('mouseout', function () {
            d3.select(this).attr('stroke-width', 0.2);
            hideTooltip();
            $(".tooltip").tooltip("hide");
        })
        .on('click', setstatename);

    const iconContainer = d3.select('#india-chloro').append('g');
    iconContainer.html('');

    iconContainer
        .attr('class', 'icon-container')
        .style('fill', 'transparent')

    iconContainer.selectAll('.topstMapIcon')
        .data(top3Data)
        .enter()
        .filter((i) => i.properties.totalcasedata[casetype] > 0) 
        .append('foreignObject')
        .attr('x', (el) => mapprojectionresult[0](d3.geoCentroid(el))[0] - iconWidth / 2)
        .attr('y', (el) => mapprojectionresult[0](d3.geoCentroid(el))[1] - 40)
        .attr('width', iconWidth)
        .attr('height', iconHeight)
        .attr('overflow', 'visible')
        .html((i) => {
            const metricText = getMetricKey(casetype);
            let iconClass;
            let metricValue;
          
            if (metricText === "Total Active Sellers") {
                iconClass = "mdi mdi-account";
                metricValue = i.properties.totalcasedata[casetype];
            } else if (metricText === "Intrastate Percentage") {
                iconClass = "mdi mdi-truck-delivery";
                metricValue = `${i.properties.totalcasedata[casetype]}%`;
            } else {
                iconClass = "mdi mdi-cart-variant";
                metricValue = i.properties.totalcasedata[casetype];
            }
          
            return `<div class="pointer" data-toggle="tooltip" data-placement="top" data-html="true" title="State: ${i.properties.st_nm}</br>Districts: ${i.properties.district}</br>${metricText}: ${metricValue.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")}"><i class="${iconClass}"></i></div><div class="pulse"></div>`;
          });
            

    $("path").tooltip({
        container: 'body',
        html: true,
        placement: 'top'
    });
    addLegend(customColorRange, casetype, maxdata[casetype]);
    d3.select('#india-chloro').select('.icon-container').remove();
    $('[data-toggle="tooltip"]').tooltip();

}

function renderstateborder(statemap_geojson, state_meshdata, casetype) {

    const mapprojectionresult = mapprojection(statemap_geojson)
    d3.select('#state-border')
        .append("path")
        .attr("stroke", bubblecolormapper[casetype][2])
        .attr("stroke-width", 1.5)
        .style('z-index', 5)
        .attr('fill', 'none')
        .attr("d", mapprojectionresult[1](state_meshdata));
}


function handleMouseover(event, d, casetype, color, top3Data) {
    const tooltipContent = generateTooltipContent(d, casetype, color, top3Data);
    showTooltip(tooltipContent);
}

function handleMouseover2(event, d, casetype, color, top3Data) {
    const tooltipContent = generateTooltipContent2(d, casetype, color, top3Data);
    showTooltip(tooltipContent);
}

function generateTooltipContent(d, casetype, color, top3Data) {
    const metricKey = getMetricKey(casetype);

    let colorValue = "";
    if (casetype === "map_total_zonal_commerce_metrics") {
        colorValue = "#10b759";
    } else if (casetype === "map_total_orders_metrics") {
        colorValue = "#e3570a";
    } else if (casetype === "map_total_active_sellers_metrics") {
        colorValue = "#1C75BC";
    } 


    return `
        <div class="">
            <div class="d-flex">
                <h6 class="tx-uppercase tx-11 tx-spacing-1 tx-color-03 tx-semibold mg-b-0">${metricKey}</h6>
                <h6 class="tx-uppercase tx-11 tx-spacing-1 tx-color-03 tx-semibold mg-b-0 mg-l-3">in</h6>
            </div>
            <h3 class="tx-normal tx-rubik mg-b-0 dist_desc"><i class="mdi mdi-map-marker-outline"></i>  ${d.id}</h3>
            <h3 class="tx-bold mg-b-5 total_count_txt ${metricKey === 'Total Active Sellers' && d.properties.totalcasedata[casetype] === 0
                ? 'tx-50' 
                : 'tx-70'
                }" style="line-height: ${metricKey === 'Total Active Sellers' && d.properties.totalcasedata[casetype] === 0
                ? '55px' 
                : '65px'
                }; color: ${colorValue};">
                ${metricKey === 'Total Active Sellers' && d.properties.totalcasedata[casetype] === 0
                    ? 'No Data'
                    : (metricKey === 'Intrastate Percentage'
                    ? new Intl.NumberFormat().format(d.properties.totalcasedata[casetype]) + '%'
                    : new Intl.NumberFormat().format(d.properties.totalcasedata[casetype]))
                }
            </h3>

            <div class="top-districts">
                <h6 class="tx-uppercase tx-12 tx-spacing-1 tx-color-02 tx-semibold mg-b-5">Top 3 States</h6>
                ${getTopStateHTML(top3Data, casetype)}
            </div>
        </div>
    `;
}
function generateTooltipContent2(d, casetype, color, top3Data) {
    const metricKey = getMetricKey(casetype);
    
    let colorValue = "";
    if (casetype === "map_total_zonal_commerce_metrics") {
        colorValue = "#10b759";
    } else if (casetype === "map_total_orders_metrics") {
        colorValue = "#e3570a";
    } else if (casetype === "map_total_active_sellers_metrics") {
        colorValue = "#1C75BC";
    } 


    const isNoData = metricKey === 'Total Active Sellers' && d.properties.totalcasedata[casetype] === 0;
    const fontSize = isNoData ? 'tx-50' : 'tx-70';
    const lineHeight = isNoData ? '55px' : '65px';
    const colorVal = colorValue;

    const metricValue = isNoData
        ? 'No Data'
        : (metricKey === 'Intrastate Percentage'
            ? new Intl.NumberFormat().format(d.properties.totalcasedata[casetype]) + '%'
            : new Intl.NumberFormat().format(d.properties.totalcasedata[casetype]));

    return `
        <div class="">
            <div class="d-flex">
                <h6 class="tx-uppercase tx-11 tx-spacing-1 tx-color-03 tx-semibold mg-b-0">${metricKey}</h6>
                <h6 class="tx-uppercase tx-11 tx-spacing-1 tx-color-03 tx-semibold mg-b-0 mg-l-3">in</h6>
            </div>
            <h3 class="tx-normal tx-rubik mg-b-0 dist_desc"><i class="mdi mdi-map-marker-outline"></i> ${d.properties.district}</h3>
            <h3 class="tx-bold mg-b-5 total_count_txt ${fontSize}" style="line-height: ${lineHeight}; color: ${colorVal};">
                ${metricValue}
            </h3>
            <div class="top-districts">
                <h6 class="tx-uppercase tx-12 tx-spacing-1 tx-color-02 tx-semibold mg-b-5">Top 3 Districts</h6>
                ${getTopDistrictsHTML(top3Data, casetype)}
            </div>
        </div>
    `;

}


function showTooltip(content) {
    const tooltipContainer = d3.select('#stHoverText');
    tooltipContainer.html(content);
    tooltipContainer.style('display', 'block');
}

function hideTooltip() {
    d3.select('#stHoverText').html("");
}

function getTopStateHTML(top3Data, casetype) {
    return top3Data.map((d) => {
        const metricValue = casetype === 'map_total_active_sellers_metrics' && d.properties.totalcasedata[casetype] === 0
            ? 'No Data'
            : (casetype === 'map_total_zonal_commerce_metrics'
                ? new Intl.NumberFormat().format(d.properties.totalcasedata[casetype]) + '%'
                : new Intl.NumberFormat().format(d.properties.totalcasedata[casetype]));

        return `
            <div class="media mg-b-6">
                <div class="crypto-icon crypto-icon-sm bg-primary op-8">
                    <i class="mdi mdi-map-marker-outline tx-22"></i>
                </div>
                <div class="media-body pd-l-8">
                    <h6 class="tx-11 tx-spacing-1 tx-color-03 tx-uppercase tx-semibold mg-0">${d.id}</h6>
                    <h4 class="tx-18 tx-rubik tx-bold tx-brand-01 mg-b-0 dist_title_text">${metricValue}</h4>
                </div>
            </div>
        `;
    }).join('');
}

function getTopDistrictsHTML(top3Data, casetype) {
    return top3Data.map((d) => {
        const metricValue = casetype === 'map_total_active_sellers_metrics' && d.properties.totalcasedata[casetype] === 0
            ? 'No Data'
            : (casetype === 'map_total_zonal_commerce_metrics'
                ? new Intl.NumberFormat().format(d.properties.totalcasedata[casetype]) + '%'
                : new Intl.NumberFormat().format(d.properties.totalcasedata[casetype]));

        return `
            <div class="media mg-b-6">
                <div class="crypto-icon crypto-icon-sm bg-primary op-8">
                    <i class="mdi mdi-map-marker-outline tx-22"></i>
                </div>
                <div class="media-body pd-l-8">
                    <h6 class="tx-11 tx-spacing-1 tx-color-03 tx-uppercase tx-semibold mg-0">${d.properties.district}</h6>
                    <h4 class="tx-18 tx-rubik tx-bold tx-brand-01 mg-b-0 dist_title_text">${metricValue}</h4>
                </div>
            </div>
        `;
    }).join('');
}


async function fetchOrderMetricsSummary(start_date, end_date, category, sub_category, state) {
    try {
        const domainName = 'None'
        const queryParams = new URLSearchParams({ domainName, start_date, end_date });

        if (category) queryParams.append('category', category);
        if (sub_category) queryParams.append('subCategory', sub_category);
        if (state) queryParams.append('state', state);

        const url = `/api/map_state_data/?${queryParams.toString()}`;

        const response = await fetch(url);
        map_state_data = await response.json();
    } catch (error) {
        console.error('Error fetching data:', error);
        map_state_data = null;
    }
}

async function fetchMapStateData(start_date, end_date, category, sub_category, state) {
    try {
        const domainName = 'None'
        const queryParams = new URLSearchParams({ domainName, start_date, end_date });
        if (category) queryParams.append('category', category);
        if (sub_category) queryParams.append('subCategory', sub_category);
        if (state) queryParams.append('state', state);

        const url = `/api/map_statewise_data/?${queryParams.toString()}`;

        const response = await fetch(url);
        map_statewise_data = await response.json();

    } catch (error) {
        console.error('Error fetching data:', error);
        map_statewise_data = null;
    }
}



async function fetchdatajson(map_statewise_data) {
    const resjson = map_statewise_data
    const allstate_list = resjson.statewise;
    const lst_order_demand = new Array();
    const lst_active_sellers = new Array();
    const lst_total_intradistrict_orders_percentage = new Array();
    const lst_total_intrastate_orders_percentage = new Array();

    allstate_list.forEach(element => {
        if(element.statecode !='TT'){

            if (element.active_sellers <= 3){
                element.active_sellers = 0
            }

            let order_demand = element.order_demand ? element.order_demand : 0
            let active_sellers = element.active_sellers ? element.active_sellers : 0
            let total_intradistrict_orders_percentage = element.intradistrict_orders_percentage ? element.intradistrict_orders_percentage : 0
            let total_intrastate_orders_percentage = element.intrastate_orders_percentage ? element.intrastate_orders_percentage : 0

            lst_order_demand.push(order_demand);
            lst_active_sellers.push(active_sellers);
            lst_total_intradistrict_orders_percentage.push(total_intradistrict_orders_percentage);
            lst_total_intrastate_orders_percentage.push(total_intrastate_orders_percentage);

        }
    });
    datajson= {
        cummulative:{
            od: lst_order_demand,
            as: lst_active_sellers,
            tiso: lst_total_intradistrict_orders_percentage ,
            tiso2: lst_total_intrastate_orders_percentage ,
        },
        statewise:resjson.statewise
    }
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

async function fetchTopCardsData(startDate, endDate, category, subCategory, domain, state) {
  const queryParams = new URLSearchParams({ startDate, endDate, category, subCategory, domain, state});
  top_cards_data = await fetchFromApi(`/api/top_card_delta/?${queryParams}`);
}

async function loadTopCardsDeltaData(start_date, end_date, category, sub_category,domain, state) {
    emptyTopCardMetrics()
  fetchTopCardsData(start_date, end_date, category, sub_category,domain, state)
    .then(data => updateTopCardsDelta(data))
    .catch(error => console.error('Error in fetchTopStateOrders:', error));

    }


async function loadMapDataAndVisualizations(start_date, end_date, category, sub_category, state) {
    const loader = $('body');
    loader.append(loaderCont)
    try {
            await Promise.all([
                fetchMapStateData(start_date, end_date, category, sub_category, state),
                fetchOrderMetricsSummary(start_date, end_date, category, sub_category, state)
            ]);
        } catch (error) {
            console.error("Error with Promise.all:", error);
        }
    await fetchTopCardsData(start_date, end_date, category, sub_category, 'None', 'None')


    if (!map_state_data || !map_statewise_data) {
        console.error("Failed to fetch map state data or map statewise data");
        return;
    }


    await fetchdatajson(map_statewise_data);
    top_cards_data = JSON.parse(top_cards_data)
    await update_cards(top_cards_data.top_card_data, top_cards_data.prev_date_range)
    const maxdata = {
        map_total_active_sellers_metrics: datajson.cummulative.as && datajson.cummulative.as.length > 0 ? d3.max(datajson.cummulative.as, d => +d) : 0,
        map_total_orders_metrics: datajson.cummulative.od && datajson.cummulative.od.length > 0 ? d3.max(datajson.cummulative.od, d => +d) : 0,
        map_total_zonal_commerce_metrics: datajson.cummulative.tiso && datajson.cummulative.tiso.length > 0 ? d3.max(datajson.cummulative.tiso, d => +d) : 0,
    };

    const indiamapdata = await indiamapdataprocessed(map_state_data);
    const statemap_geojson = topojson.feature(indiamapdata, indiamapdata.objects.states);
    const districtmap_geojson = topojson.feature(indiamapdata, indiamapdata.objects.districts);
    const state_meshdata = topojson.mesh(indiamapdata, indiamapdata.objects.states);
    let metric_selected = $('.metric-option.active').attr('value');

    await statechloromap(statemap_geojson, maxdata, metric_selected);
    buttonChange(statemap_geojson, districtmap_geojson, state_meshdata, maxdata, start_date, end_date, category, sub_category, state);

    const btn_india_district_map = d3.select('#india-district-map-btn')
    const btn_india_state_map = d3.select('#india-state-map-btn')

    const btn_chloro_map_style = d3.select('#chloro-viz-btn')
    const btn_bubble_map_style = d3.select('#bubble-viz-btn')

    const btn_active_sellers_metrics = d3.select('#active-sellers-metrics-btn')
    const btn_orders_metrics = d3.select('#orders-metrics-btn')
    const btn_zonal_commerce_metrics = d3.select('#zonal-commerce-metrics-btn')

    const btnarr = new Array(btn_india_district_map, btn_india_state_map, btn_chloro_map_style, btn_bubble_map_style, btn_active_sellers_metrics, btn_orders_metrics, btn_zonal_commerce_metrics);
    buttonvaluecheck(btnarr, statemap_geojson, districtmap_geojson, state_meshdata, maxdata);
    plotStateMap(map_state_data,metric_selected);

    if (metric_selected === 'map_total_orders_metrics') {
    $(".loaderBox").remove();
        if (includeCategory) {
            await Promise.all([
                    loadTopStateOrdersChart('Retail', start_date, end_date, category, sub_category, state),
                    loadTopDistrictOrdersChart('None', start_date, end_date, category, sub_category, state),
                    createSunburstChart('Retail', start_date, end_date, category, sub_category, state),
                    fetchDonutChartData('Retail', start_date, end_date, category, sub_category, state),
                    loadMaxOrders('Retail', start_date, end_date, category, sub_category),
                ]);
        }else{
            await Promise.all([
                    loadTopStateOrdersChart('Retail', start_date, end_date, category, sub_category, state),
                    loadTopDistrictOrdersChart('None', start_date, end_date, category, sub_category, state),
                    fetchDonutChartData('Retail', start_date, end_date, category, sub_category, state),
                    loadMaxOrders('Retail', start_date, end_date, category, sub_category),
                ]);
        }
        
    } else if (metric_selected === 'map_total_active_sellers_metrics') {
    $(".loaderBox").remove();
    if (includeCategory) {
            await Promise.all([
                loadTopStateSellersChart('Retail', start_date, end_date, category, sub_category, state),
                loadTopDistrictSellersChart('None', start_date, end_date, category, sub_category, state),
                createSunburstChartsellers('Retail', start_date, end_date, category, sub_category, state),
                fetchDonutChartData2('Retail', start_date, end_date, category, sub_category, state),
                loadMaxSellers('Retail', start_date, end_date, category, sub_category)
        ]);
        }else{
            await Promise.all([
                loadTopStateSellersChart('Retail', start_date, end_date, category, sub_category, state),
                loadTopDistrictSellersChart('None', start_date, end_date, category, sub_category, state),
                fetchDonutChartData2('Retail', start_date, end_date, category, sub_category, state),
                loadMaxSellers('Retail', start_date, end_date, category, sub_category)
        ]);
        }
    } else if (metric_selected === 'map_total_zonal_commerce_metrics') {
    $(".loaderBox").remove();
        await Promise.all([
                loadTopStateLogisticsChart('Retail', start_date, end_date, category, sub_category, state),
                loadTopDistrictLogisticsChart('None', start_date, end_date, category, sub_category, state),
                loadAndCreateTreeChart('Retail', start_date, end_date, category, sub_category),
        ]);
        
    }
    negativeValue();

}

function updateTopCardsDelta(data, prevDateRange) {
    try {
        updateTopCardMetrics("total-confirmed-orders", data.total_confirmed_orders, "confirmedPrevDate", prevDateRange);
        updateTopCardMetrics("confirmed-orders-change", data.cnf_delta, "india-items-per-order", data.avg_items);
        updateTopCardMetrics("india-activesellers", data.total_active_sellers, "max_orders_delivered_area", data.max_orders_delivered_area);
        updateTopCardMetrics("india-activesellers-change", data.sellers_delta, "activeSellersPrevDate", prevDateRange);
        updateTopCardMetrics("india-active-pincodes", data.total_districts, "districtsPrevDate", prevDateRange);
        updateTopCardMetrics("active-pincodes-change", data.district_delta);

        if (includeCategory) {
            updateTopCardMetrics("max_orders_delivered_category", data.most_ordering_district);
        }

        negativeValue();
    } catch (error) {
        updateTopCardMetrics("total-confirmed-orders", 0, "confirmedPrevDate", prev_date_range);
        updateTopCardMetrics("confirmed-orders-change", 0, "india-items-per-order", 0);

        updateTopCardMetrics("india-activesellers", 0, "max_orders_delivered_area", 'No Data to Display');
        updateTopCardMetrics("india-activesellers-change", 0, "activeSellersPrevDate", prev_date_range);

        updateTopCardMetrics("india-active-pincodes", 0, "districtsPrevDate", prev_date_range);
        updateTopCardMetrics("active-pincodes-change", 0);
        if (includeCategory) {
            updateTopCardMetrics("max_orders_delivered_category", 'No Data to Display');
        }
    }
}

function updateTopCardMetrics(id, data, changeId = null, dataChange = null) {
    const element = document.getElementById(id);

    if (element === null) {
        console.error(`Element with ID ${id} not found.`);
        return;
    }

    const numericData = Number(data);

    if (!isNaN(numericData)) {
        element.innerText = `${formatNumber(numericData)}`;
    } else {
        element.innerText = data;
    }

    if (changeId !== null && dataChange !== null) {
        const changeElement = document.getElementById(changeId);

        if (changeElement === null) {
            console.error(`Change element with ID ${changeId} not found.`);
            return;
        }

        const numericDataChange = Number(dataChange);

        if (!isNaN(numericDataChange)) {
            changeElement.innerText = `${formatNumber(numericDataChange)}`;
        } else {
            changeElement.innerText = dataChange;
        }
    }
}

function formatNumber(num) {
    var numParts = num.toString().split(".");
    numParts[0] = numParts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return numParts.join(".");
}

export async function main(start_date, end_date, category, sub_category, state, filter_flag=1) {
    await loadMapDataAndVisualizations(start_date, end_date, category, sub_category, state);
    }

function buttonvaluecheck(btnarray, statemap_geojson, districtmap_geojson, state_meshdata, maxdata) {
    d3.select('#state-border').selectAll('path').remove()
    d3.select('#district-border').selectAll('path').remove()
    d3.select('#india-chloro').selectAll('path').remove()
    d3.select('#india-bubble').selectAll('circle').remove()

    const nwbtnarry = btnarray.filter(a => a.classed('active'))
    const nwbtnarry2 = nwbtnarry.map(a => a.attr('value'))

    let metric_selected  = $('.metric-option.active').attr('value');

    if (nwbtnarry2.includes("district-border") && nwbtnarry2.includes("chloro")) {
        if (metric_selected == "map_total_active_sellers_metrics") {
            statechloromap(statemap_geojson, maxdata, metric_selected);
            $('#india-state-map-btn').trigger("click");
        } else {
            districtchloromap(districtmap_geojson, maxdata, metric_selected);
        }
    }
    else if (nwbtnarry2.includes("district-border") && nwbtnarry2.includes("bubble")) {

        renderstateborder(statemap_geojson, state_meshdata, metric_selected);
        districtbubblemap(districtmap_geojson, maxdata, metric_selected);
    }
    else if (nwbtnarry2.includes("state-border") && nwbtnarry2.includes("chloro")) {
        statechloromap(statemap_geojson, maxdata, metric_selected);
    }
    else {
        statebubblemap(statemap_geojson, maxdata, metric_selected);
        renderstateborder(statemap_geojson, state_meshdata, metric_selected);
    }
}

function buttonChange(statemap_geojson, districtmap_geojson, state_meshdata, maxdata, start_date, end_date, category, sub_category, state) {
    const btn_india_district_map = d3.select('#india-district-map-btn')
    const btn_india_state_map = d3.select('#india-state-map-btn')

    const btn_chloro_map_style = d3.select('#chloro-viz-btn')
    const btn_bubble_map_style = d3.select('#bubble-viz-btn')

    const btn_active_sellers_metrics = d3.select('#active-sellers-metrics-btn')
    const btn_orders_metrics = d3.select('#orders-metrics-btn')
    const btn_zonal_commerce_metrics = d3.select('#zonal-commerce-metrics-btn')

    const btnarr = new Array(btn_india_district_map, btn_india_state_map, btn_chloro_map_style, btn_bubble_map_style, btn_active_sellers_metrics, btn_orders_metrics, btn_zonal_commerce_metrics);

    btn_india_district_map.on('click', (e, i) => {
        if (!btn_india_district_map.classed('active')) {
            btn_india_district_map.classed('active', true)
            btn_india_state_map.classed('active', false)
            $("#indiamap-dist-data").show()
            $("#indiaTableContainer").hide()
        }
        buttonvaluecheck(btnarr, statemap_geojson, districtmap_geojson, state_meshdata, maxdata)

    })
    btn_india_state_map.on('click', () => {

        if (!btn_india_state_map.classed('active')) {
            btn_india_state_map.classed('active', true)
            btn_india_district_map.classed('active', false)
            $("#indiamap-dist-data").hide()
            $("#indiaTableContainer").show()


        }
        buttonvaluecheck(btnarr, statemap_geojson, districtmap_geojson, state_meshdata, maxdata)
    })

    btn_chloro_map_style.on('click', () => {
        if (!btn_chloro_map_style.classed('active')) {
            btn_chloro_map_style.classed('active', true)
            btn_bubble_map_style.classed('active', false)
            $("#indiamap-dist-data").show()
            $("#indiaTableContainer").hide()
        }

        buttonvaluecheck(btnarr, statemap_geojson, districtmap_geojson, state_meshdata, maxdata)
    })

    btn_bubble_map_style.on('click', () => {
        if (!btn_bubble_map_style.classed('active')) {
            btn_bubble_map_style.classed('active', true)
            btn_chloro_map_style.classed('active', false)
            $("#indiamap-dist-data").show()
            $("#indiaTableContainer").hide()
        }
        buttonvaluecheck(btnarr, statemap_geojson, districtmap_geojson, state_meshdata, maxdata)
    })
    btn_active_sellers_metrics.on('click', async () => {
        const loader = $('body');
        loader.append(loaderCont)
       
        if (!btn_active_sellers_metrics.classed('active')) {
            btn_active_sellers_metrics.classed('active', true)
            btn_orders_metrics.classed('active', false)
            btn_zonal_commerce_metrics.classed('active', false)

            if (hide_seller == true) {
                $('#india-district-map-btn').hide();
            }
        }
        $('.nav-item a[href="#supply"]').tab('show');

        buttonvaluecheck(btnarr, statemap_geojson, districtmap_geojson, state_meshdata, maxdata);
        let metric_selected  = $('.metric-option.active').attr('value');
        plotStateMap(map_state_data, metric_selected);

        const statenm = localStorage.getItem('statename');

        try {

        if (includeCategory) {
                await Promise.all([
                    loadTopStateSellersChart('Retail', start_date, end_date, category, sub_category, statenm),
                    loadTopDistrictSellersChart('None', start_date, end_date, category, sub_category, statenm),
                    createSunburstChartsellers('Retail', start_date, end_date, category, sub_category, statenm),
                    fetchDonutChartData2('Retail', start_date, end_date, category, sub_category, statenm),
                    loadMaxSellers('Retail', start_date, end_date, category, sub_category),
                ]);
            }else{
                await Promise.all([
                    loadTopStateSellersChart('Retail', start_date, end_date, category, sub_category, statenm),
                    loadTopDistrictSellersChart('None', start_date, end_date, category, sub_category, statenm),
                    fetchDonutChartData2('Retail', start_date, end_date, category, sub_category, statenm),
                    loadMaxSellers('Retail', start_date, end_date, category, sub_category),
                ]);
            }
        } catch (error) {
            console.error('Error occurred while loading data:', error);
        } finally {
            $(".loaderBox").remove();
        }

    })
  
    btn_orders_metrics.on('click', async () => {
        const loader = $('body');
        loader.append(loaderCont);

        if (!btn_orders_metrics.classed('active')) {
            btn_orders_metrics.classed('active', true);
            btn_active_sellers_metrics.classed('active', false);
            btn_zonal_commerce_metrics.classed('active', false);
            $('#india-district-map-btn').show();
        }
        $(".clickinfo").remove();
        buttonvaluecheck(btnarr, statemap_geojson, districtmap_geojson, state_meshdata, maxdata);
        let metric_selected  = $('.metric-option.active').attr('value');
        plotStateMap(map_state_data, metric_selected);
        const statenm = localStorage.getItem('statename');
        try {
        if (includeCategory) {
                await Promise.all([
                    loadTopStateOrdersChart('Retail', start_date, end_date, category, sub_category, statenm),
                    loadTopDistrictOrdersChart('None', start_date, end_date, category, sub_category, statenm),
                    createSunburstChart('Retail', start_date, end_date, category, sub_category, statenm),
                    fetchDonutChartData('Retail', start_date, end_date, category, sub_category, statenm),
                    loadMaxOrders('Retail', start_date, end_date, category, sub_category),
                ]);
            }else{
                await Promise.all([
                        loadTopStateOrdersChart('Retail', start_date, end_date, category, sub_category, statenm),
                        loadTopDistrictOrdersChart('None', start_date, end_date, category, sub_category, statenm),
                        fetchDonutChartData('Retail', start_date, end_date, category, sub_category, statenm),
                        loadMaxOrders('Retail', start_date, end_date, category, sub_category),
                    ]);
            }
        } catch (error) {
            console.error('Error occurred while loading data:', error);
        } finally {
            $(".loaderBox").remove();
        }
        $('.nav-item a[href="#summary"]').tab('show');
    })
    
    btn_zonal_commerce_metrics.on('click', async () => {
        const loader = $('body');
        loader.append(loaderCont);

        if (!btn_zonal_commerce_metrics.classed('active')) {
            btn_zonal_commerce_metrics.classed('active', true)
            btn_active_sellers_metrics.classed('active', false)
            btn_orders_metrics.classed('active', false)

            $('#india-district-map-btn').show();
        }

        $(".clickinfo").remove();
        buttonvaluecheck(btnarr, statemap_geojson, districtmap_geojson, state_meshdata, maxdata);
        let metric_selected  = $('.metric-option.active').attr('value');
        plotStateMap(map_state_data,metric_selected);

        const statenm = localStorage.getItem('statename');
        try {
            await Promise.all([
                loadTopStateLogisticsChart('None', start_date, end_date, category, sub_category, statenm),
                loadTopDistrictLogisticsChart('None', start_date, end_date, category, sub_category, statenm),
                loadAndCreateTreeChart('None', start_date, end_date, category, sub_category, statenm),
            ]);
        } catch (error) {
            console.error('Error occurred while loading data:', error);
        } finally {
            $(".loaderBox").remove();
        }
        $('.nav-item a[href="#logistics"]').tab('show');
        $("#filtersByRegion").val("MAHARASHTRA").change();
    })

}

async function updateStateData(selected_state_st, statecode_st) {
    if (statecode_st) {
        $('.state-name').text(selected_state_st);
    } else {
        console.log("No state code provided");
    }
    
    const selected_state = selected_state_st
    const statecode = statecode_st

    $('.state-name').text(selected_state);

    localStorage.setItem('statename', selected_state);
    localStorage.setItem('statecode', statecode);
    let metric_selected  = $('.metric-option.active').attr('value');
    
    plotStateMap(map_state_data,metric_selected);
}


function emptyTopCardMetrics() {
    $("#total-confirmed-orders").html('<span class="spinner-border spinner-border-sm bd-2" role="status" aria-hidden="true"></span>');
    $("#confirmed-orders-change").html('');
    $("#confirmedPrevDate").html('Loading...');

    $("#india-items-per-order").html('<span class="spinner-border spinner-border-sm bd-2" role="status" aria-hidden="true"></span>');

    $("#india-active-pincodes").html('<span class="spinner-border spinner-border-sm bd-2" role="status" aria-hidden="true"></span>');
    $("#active-pincodes-change").html('');
    $("#districtsPrevDate").html('Loading...');

    $("#india-activesellers").html('<span class="spinner-border spinner-border-sm bd-2" role="status" aria-hidden="true"></span>');
    $("#india-activesellers-change").html('');
    $("#activeSellersPrevDate").html('Loading...');

    $("#max_orders_delivered_area").html('<span class="spinner-border spinner-border-sm bd-2" role="status" aria-hidden="true"></span>');
    $("#max_orders_delivered_category").html('<span class="spinner-border spinner-border-sm bd-2" role="status" aria-hidden="true"></span>');

}


async function update_cards(topCardsData, prev_date) {
    try {
        const SessionStatename = localStorage.getItem('statename');
        const SessionStatecode = localStorage.getItem('statecode');
        if (SessionStatename) {
            emptyTopCardMetrics();
            updateTopCardsDelta(topCardsData[SessionStatecode],prev_date )

        } else if ('TT' in topCardsData)
        {
            emptyTopCardMetrics();
            updateTopCardsDelta(topCardsData['TT'], prev_date)
        }
        else{
        updateTopCardMetrics("total-confirmed-orders", 0, "confirmedPrevDate", prev_date);
        updateTopCardMetrics("confirmed-orders-change", 0, "india-items-per-order", 0);

        updateTopCardMetrics("india-activesellers", 0, "max_orders_delivered_area", 'No Data to Display');
        updateTopCardMetrics("india-activesellers-change", 0, "activeSellersPrevDate", prev_date);

        updateTopCardMetrics("india-active-pincodes", 0, "districtsPrevDate", prev_date);
        updateTopCardMetrics("max_orders_delivered_category", 'No Data to Display', "active-pincodes-change", 0);

        }
    } catch (error) {
        console.log('Error updating cards:', error);
        updateTopCardMetrics("total-confirmed-orders", 0, "confirmedPrevDate", prev_date);
        updateTopCardMetrics("confirmed-orders-change", 0, "india-items-per-order", 0);

        updateTopCardMetrics("india-activesellers", 0, "max_orders_delivered_area", 'No Data to Display');
        updateTopCardMetrics("india-activesellers-change", 0, "activeSellersPrevDate", prev_date);

        updateTopCardMetrics("india-active-pincodes", 0, "districtsPrevDate", prev_date);
        updateTopCardMetrics("max_orders_delivered_category", 'No Data to Display', "active-pincodes-change", 0);
    }
}

async function fetchMaxOrders(domainName, startDate, endDate, category, subCategory, state) {
    const queryParams = new URLSearchParams({ startDate, endDate, domainName });
    if (category) queryParams.append('category', category);
    if (subCategory) queryParams.append('subCategory', subCategory);
    if (state) queryParams.append('state', state);
  
    const url = `/api/max_orders/?${queryParams.toString()}`;
  
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching max orders data:', error);
      throw error;
    }
  }


async function loadMaxOrders(domainName, startDate, endDate, category, subCategory) {
  const SessionStatename = localStorage.getItem('statename');
  try {
    let maxOrdersData;
    if (SessionStatename) {
      maxOrdersData = await fetchMaxOrders(domainName, startDate, endDate, category, subCategory, SessionStatename);
    } else {
      maxOrdersData = await fetchMaxOrders(domainName, startDate, endDate, category, subCategory);
    }
    if (maxOrdersData) {
      if (maxOrdersData.length > 0) {
        const maxOrdersState = maxOrdersData[0];
        const maxOrdersDistrict = maxOrdersData[1];

        updateTopCardMetrics("demand_stMaxOrderDel", maxOrdersState.location, "demand_stMaxOrderDelValue", maxOrdersState.value);
        if (maxOrdersDistrict) {
          updateTopCardMetrics("demand_dtMaxOrderDel", maxOrdersDistrict.location, "demand_dtMaxOrderDelValue", maxOrdersDistrict.value);
        }
      } else {

        displayNoDataMessage();
      }
    } else {

      displayNoDataMessage();
    }
  } catch (error) {
    console.error('Error loading max orders data:', error);
    displayErrorMessage();
  }
}

function displayNoDataMessage() {
  updateTopCardMetrics("demand_stMaxOrderDel", "No data", "demand_stMaxOrderDelValue", "No data to display");
  updateTopCardMetrics("demand_dtMaxOrderDel", "No data", "demand_dtMaxOrderDelValue", "No data to display");
}


  async function fetchMaxSellers(domainName, startDate, endDate, category, subCategory, state) {
    const queryParams = new URLSearchParams({ startDate, endDate, domainName });
  
    if (category) queryParams.append('category', category);
    if (subCategory) queryParams.append('subCategory', subCategory);
    if (state) queryParams.append('state', state);
  
    const url = `/api/max_sellers/?${queryParams.toString()}`;
  
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching max sellers data:', error);
      throw error;
    }
  }
  
async function loadMaxSellers(domainName, startDate, endDate, category, subCategory) {

  var dateRangeString = document.getElementById('filterDaterange').textContent;
  var dates = dateRangeString.split(' - ');
  var startDateString = dates[0];
  var endDateString = dates[1];

  var startDate = new Date(startDateString);
  var endDate = new Date(endDateString);

  $(".dateRangeTitle").html(dateRangeString);

  var formattedStartDate = formatDate(startDate);
  var formattedEndDate = formatDate(endDate);

  const SessionStatename = localStorage.getItem('statename');
  try {
    let maxSellersData;
    if (SessionStatename) {
      maxSellersData = await fetchMaxSellers(domainName, formattedStartDate, formattedEndDate, category, subCategory, SessionStatename);
    } else {
      maxSellersData = await fetchMaxSellers(domainName, formattedStartDate, formattedEndDate, category, subCategory);
    }

    if (maxSellersData) {
      const records = JSON.parse(maxSellersData);
      if (records.length > 0) {
        const maxSellersState = records[0];
        const maxSellersDistrict = records[1];

        updateTopCardMetrics("supply_stMaxOrderDel", maxSellersState.location, "supply_stMaxOrderDelValue", maxSellersState.seller_count);
        updateTopCardMetrics("supply_dtMaxOrderDel", maxSellersDistrict.location, "supply_dtMaxOrderDelValue", maxSellersDistrict.seller_count);
      } else {
        updateTopCardMetrics("supply_stMaxOrderDel", "No data", "supply_stMaxOrderDelValue", "No data");
        updateTopCardMetrics("supply_dtMaxOrderDel", "No data", "supply_dtMaxOrderDelValue", "No data");
      }
    } else {
      updateTopCardMetrics("supply_stMaxOrderDel", "No data", "supply_stMaxOrderDelValue", "No data");
      updateTopCardMetrics("supply_dtMaxOrderDel", "No data", "supply_dtMaxOrderDelValue", "No data");
    }

  } catch (error) {
    console.error('Error loading max orders data:', error);
    updateTopCardMetrics("supply_stMaxOrderDel", "Error", "supply_stMaxOrderDelValue", "Failed to load data");
    updateTopCardMetrics("supply_dtMaxOrderDel", "Error", "supply_dtMaxOrderDelValue", "Failed to load data");
  }
}

