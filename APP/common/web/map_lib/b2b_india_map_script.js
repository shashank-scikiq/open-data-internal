import { statenametostatecode } from './fetchlatest_statejson.js';
import { indiamapdataprocessed } from './indiamap.js';
import { plotStateMap } from './state_map_script.js';

const width = 1200;
const height = 1200;

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
let datajson = null;

const months = {
    'January': 0, 'February': 1, 'March': 2, 'April': 3, 'May': 4, 'June': 5, 'July': 6,
    'August': 7, 'September': 8, 'October': 9, 'November': 10, 'December': 11
}

const bubblecolormapper = {
    map_total_orders_metrics: ["rgba(227, 87, 10,0.8)", "rgba(227, 87, 10,0.4)", "rgba(227, 87, 10,0.4)"], // Seller
}

const chloroplethcolormapper = {
    map_total_orders_metrics: [d3.interpolateOranges, "rgba(255,7,58,0.5)"],
    map_total_active_sellers_metrics: [d3.interpolateBlues, "rgba(0,123,255,0.5)"],
    map_total_zonal_commerce_metrics: [d3.interpolateGreens, "rgba(255,7,58,0.5)"],
}

const chloroplethcolormapper2 = {
    map_total_orders_metrics:["#ffffff", "#f9f0e9", "#FF7722"],
    map_total_active_sellers_metrics: ["#ffffff", "#dfebf5", "#1c75bc"],
    map_total_zonal_commerce_metrics: ["#ffffff", "#eefaf3", "#10b759"],
}
const chloroplethcolormapper3 = {
    map_total_orders_metrics:["#ffffff", "#FF7722"],
    map_total_active_sellers_metrics: ["#ffffff", "#1c75bc"],
    map_total_zonal_commerce_metrics: ["#ffffff", "#10b759"],
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


$(document).on('change', '.statelist', function() {
    let statecode = $(this).val();
    updateStateData();
  });
  $('#switchDistricts').prop('disabled',true);



async function showIndiaMap(statemap_geojson, maxdata, metric_selected){
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

    $('#filtersByRegion').attr('disabled', false);

    var dateRangeString = document.getElementById('filterDaterange').textContent;
    var dates = dateRangeString.split(' - ');
    var startDateString = dates[0];
    var endDateString = dates[1];

    var startDate = new Date(startDateString);
    var endDate = new Date(endDateString);


    $(".dateRangeTitle").html(dateRangeString);

    let db_str_dt = formatDateStringDB(startDate);
    let db_end_dt = formatDateStringDB(endDate);
    var start_date = formatDate(startDate);
    var end_date = formatDate(endDate);
     await loadTopCardsDeltaData(start_date, end_date, 'None', 'None')

}

async function hideIndiaMap(statename){
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


    $(".dateRangeTitle").html(dateRangeString);

    var startDate = new Date(startDateString);
    var endDate = new Date(endDateString);

    var start_date = formatDate(startDate);
    var end_date = formatDate(endDate);
    let db_str_dt = formatDateStringDB(start_date)
    let db_end_dt = formatDateStringDB(end_date)

    let metric_selected = $('.metric-option.active').attr('value');
    await loadTopCardsDeltaData(start_date, end_date, 'None', 'None', 'None', statename)
}

$("body").on("click",".changeStbtn",function(){
    showIndiaMap();
    $(".tooltip").tooltip("hide");
})


function setstatename(d, i) {
    localStorage.setItem('statename', i.properties.st_nm)
    localStorage.setItem('statecode', statenametostatecode[i.properties.st_nm])
    updateStateData( i.properties.st_nm,statenametostatecode[i.properties.st_nm])
    hideIndiaMap( i.properties.st_nm)
}

function statebubblemap(statemap_geojson, maxdata, casetype) {
    const mapprojectionresult = mapprojection(statemap_geojson);

    const color = d3.scaleSequentialLog(chloroplethcolormapper2[casetype]).domain([1, maxdata[casetype]]);

    const iconWidth = 35;
    const iconHeight = 35;

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
                `${value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")}`
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
            hideTooltip();
            $(".tooltip").tooltip("hide");
        })
        .on('click', setstatename);


    d3.select('#india-chloro').select('.icon-container').remove();
    d3.select('#india-bubble').select('.icon-container').remove();
    const iconContainer = d3.select('#india-bubble').append('g');
    iconContainer.html('');

    iconContainer
        .attr('class', 'icon-container')
        .style('fill', 'transparent');

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

            if (metricText === "Total Orders Delivered") {
                iconClass = "mdi mdi-cart-variant";
                metricValue = i.properties.totalcasedata[casetype];
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
            return `State: ${i.properties.st_nm}<br/> District : ${i.properties.district}<br/> ${getMetricKey(casetype)} : ${value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")}`;
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

            if (metricText === "Total Orders Delivered") {
                iconClass = "mdi mdi-cart-variant";
                metricValue = i.properties.totalcasedata[casetype];
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


function statechloromap(statemap_geojson, maxdata, casetype) {

    const mapprojectionresult = mapprojection(statemap_geojson);
    const color = d3.scaleSequentialLog(chloroplethcolormapper3[casetype]).domain([1, maxdata[casetype]]);

    const iconWidth = 35;
    const iconHeight = 35;

    const g = d3.select('#india-chloro');

    const sortedData = statemap_geojson.features.sort((a, b) => b.properties.totalcasedata[casetype] - a.properties.totalcasedata[casetype]);
    const top3Data = sortedData.slice(0, 3);

    let customColorRange;
    const metricText = getMetricKey(casetype);
    if (metricText === "map_total_orders_metrics") {
            customColorRange = d3.scaleLinear()
            .domain([0, 1, maxdata[casetype]])
            .range(chloroplethcolormapper2[casetype]);
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
        .attr('fill', (el) => customColorRange(el.properties.totalcasedata[casetype], maxdata[casetype]))
        .attr('stroke-width', 0.5)
        .attr('stroke', 'black')
        .attr('class', 'country')
        .attr("data-title", (i) => {
            const value = i.properties.totalcasedata[casetype];
            return `State: ${i.id}<br/> ${getMetricKey(casetype)} : ${value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")}`;
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

            if (metricText === "Total Orderes Delivered") {
                iconClass = "mdi mdi-cart-variant";
                metricValue = i.properties.totalcasedata[casetype];
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

    // addLegend(color, casetype, maxdata[casetype]);
    addLegend(customColorRange, casetype, maxdata[casetype]);
    $('[data-toggle="tooltip"]').tooltip();
}


function addLegend(customColorRange, casetype, maxdata) {
    const legendContainer = d3.select('#mapLegends');
    legendContainer.html('');

    // Define legend values for 8 sections
    const legendValues = [0, ...Array.from({ length: 4 }, (_, i) => (i + 1) * maxdata / 4)];

    const newLegendContainer = legendContainer.append('svg')
        .attr('class', 'legend')
        .attr('width', 20)

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
        .attr('transform', (d, i) => `translate(0, ${i * (200 / 9) + 20})`); // Adjust vertical positioning

    legend.append('rect')
        .attr('width', 18)
        .attr('height', 18)
        .style('stroke', 'black')
        .style('stroke-width', '1px')
        .style('fill', (d) => customColorRange(d)); // Use customColorRange here

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
    let mapprojectionresult = mapprojection(districtmap_geojson);

    let color = d3.scaleSequentialLog(chloroplethcolormapper3[casetype]).domain([1, maxdata[casetype]]);

    const iconWidth = 35;
    const iconHeight = 35;

    const sortedData = districtmap_geojson.features.sort((a, b) => b.properties.totalcasedata[casetype] - a.properties.totalcasedata[casetype]);
    const top3Data = sortedData.slice(0, 3);
    const customColorRange = d3.scaleLinear()
        .domain([0, 1, maxdata[casetype]])
        .range(chloroplethcolormapper2[casetype]);
    const g = d3.select('#india-chloro');

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
            return `State: ${i.properties.st_nm}<br/> District : ${i.properties.district}<br/> ${getMetricKey(casetype)} : ${value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")}`;
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
        .style('fill', 'transparent');

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

            if (metricText === "Total Orderes Delivered") {
                iconClass = "mdi mdi-cart-variant";
                metricValue = i.properties.totalcasedata[casetype];
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
    if (casetype === "map_total_orders_metrics") {
        colorValue = "#e3570a";
    }

    return `
        <div class="">
            <div class="d-flex">
                <h6 class="tx-uppercase tx-11 tx-spacing-1 tx-color-03 tx-semibold mg-b-0">${metricKey}</h6>
                <h6 class="tx-uppercase tx-11 tx-spacing-1 tx-color-03 tx-semibold mg-b-0 mg-l-3">in</h6>
            </div>
            <h3 class="tx-normal tx-rubik mg-b-0 dist_desc"><i class="mdi mdi-map-marker-outline"></i>  ${d.id}</h3>
            <h3 class="tx-bold mg-b-5 total_count_txt tx-70" style="line-height: 65px; color: ${colorValue};">
                ${new Intl.NumberFormat().format(d.properties.totalcasedata[casetype])}
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
    if (casetype === "map_total_orders_metrics") {
        colorValue = "#e3570a";
    }

    return `
        <div class="">
            <div class="d-flex">
                <h6 class="tx-uppercase tx-11 tx-spacing-1 tx-color-03 tx-semibold mg-b-0">${metricKey}</h6>
                <h6 class="tx-uppercase tx-11 tx-spacing-1 tx-color-03 tx-semibold mg-b-0 mg-l-3">in</h6>
            </div>
            <h3 class="tx-normal tx-rubik mg-b-0 dist_desc"><i class="mdi mdi-map-marker-outline"></i> ${d.properties.district}</h3>
            <h3 class="tx-bold mg-b-5 total_count_txt tx-70" style="line-height: 65px; color: ${colorValue};">
                ${new Intl.NumberFormat().format(d.properties.totalcasedata[casetype])}
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
    return top3Data.map((d) => `
        <div class="media mg-b-6">
            <div class="crypto-icon crypto-icon-sm bg-primary op-8">
                <i class="mdi mdi-map-marker-outline tx-22"></i>
            </div>
            <div class="media-body pd-l-8">
                <h6 class="tx-11 tx-spacing-1 tx-color-03 tx-uppercase tx-semibold mg-0">${d.id}</h6>
                <h4 class="tx-18 tx-rubik tx-bold tx-brand-01 mg-b-0 dist_title_text">
                ${new Intl.NumberFormat().format(d.properties.totalcasedata[casetype])}
                </h4>

            </div>
        </div>
    `).join('');
}


function getTopDistrictsHTML(top3Data, casetype) {
    return top3Data.map((d) => `
        <div class="media mg-b-6">
            <div class="crypto-icon crypto-icon-sm bg-primary op-8">
                <i class="mdi mdi-map-marker-outline tx-22"></i>
            </div>
            <div class="media-body pd-l-8">
                <h6 class="tx-11 tx-spacing-1 tx-color-03 tx-uppercase tx-semibold mg-0">${d.properties.district}</h6>
                <h4 class="tx-18 tx-rubik tx-bold tx-brand-01 mg-b-0 dist_title_text">
                ${new Intl.NumberFormat().format(d.properties.totalcasedata[casetype])}
                </h4>

            </div>
        </div>
    `).join('');
}

async function fetchOrderMetricsSummary4(start_date, end_date, category, sub_category, state) {
    try {
        let pathname = window.location.pathname;
        const queryParams = new URLSearchParams({ start_date, end_date });

        if (category) queryParams.append('category', category);
        if (sub_category) queryParams.append('subCategory', sub_category);
        if (state) queryParams.append('state', state);

        const url = `${pathname}map_state_data/?${queryParams.toString()}`;

        const response = await fetch(url);
        const map_state_data = await response.json();
        // flashMessage("Error in daterange", 'info');
    } catch (error) {
        console.error('Error fetching data:', error);
        const map_state_data = null;
        // flashMessage("Error in daterange", 'success');
    }
}


async function fetchOrderMetricsSummary(start_date, end_date, category, sub_category, state) {
    try {
//        let pathname = window.location.pathname;
        const baseUrl = `${window.location.origin}${window.location.pathname.replace(/\/$/, '')}`;

        const domainName = 'None'
        const queryParams = new URLSearchParams({ domainName, start_date, end_date });

        if (category) queryParams.append('category', category);
        if (sub_category) queryParams.append('subCategory', sub_category);
        if (state) queryParams.append('state', state);

        const url = `${baseUrl}/map_state_data/?${queryParams.toString()}`;

        const response = await fetch(url);
        map_state_data = await response.json();
        // flashMessage("Error in daterange", 'info');
    } catch (error) {
        console.error('Error fetching data:', error);
        map_state_data = null;
        // flashMessage("Error in daterange", 'success');
    }
}

async function fetchMapStateData(startDate, endDate, category, sub_category, state) {
    try {
        let pathname = window.location.pathname;
        const loader = $('body');
        loader.append(loaderCont)
        const domainName = 'None'
        const queryParams = new URLSearchParams({ domainName, startDate, endDate });
        if (category) queryParams.append('category', category);
        if (sub_category) queryParams.append('subCategory', sub_category);
        if (state) queryParams.append('state', state);

        const url = `${pathname}map_statewise_data/?${queryParams.toString()}`;

        const response = await fetch(url);
        map_statewise_data = await response.json();
        $(".loaderBox").remove();

    } catch (error) {
        console.error('Error fetching data:', error);
        map_statewise_data = null;
    }
}



async function fetchdatajson(map_statewise_data) {
    const resjson = map_statewise_data
    const l = resjson.statewise.length;
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
  return fetchFromApi(`top_card_delta/?${queryParams}`);
}

async function loadTopCardsDeltaData(start_date, end_date, category, sub_category,domain, state) {
    emptyTopCardMetrics()
    const SessionStatename = localStorage.getItem('statename');
    if (SessionStatename) {
        state = SessionStatename
    }
    fetchTopCardsData(start_date, end_date, category, sub_category,domain, state)
        .then(data => updateTopCardsDelta(data))
        .catch(error => console.error('Error in fetchTopStateOrders:', error));

}



async function loadMapDataAndVisualizations(start_date, end_date, category, sub_category, state) {
    try {
        const [map_state_data, map_statewise_data] = await Promise.all([
            fetchMapStateData(start_date, end_date, category, sub_category, state),
            fetchOrderMetricsSummary(start_date, end_date, category, sub_category, state),
            loadTopCardsDeltaData(start_date, end_date, category, sub_category, 'None', state)

        ]);
    } catch (error) {
        console.error("Error with Promise.all:", error);
    }


    if (!map_state_data || !map_statewise_data) {
        console.error("Failed to fetch map state data or map statewise data");
        return;
    }

    await fetchdatajson(map_statewise_data);

    const maxdata = {
        map_total_orders_metrics: d3.max(datajson.cummulative.od, d => +d),
    };
    const indiamapdata = await indiamapdataprocessed(map_state_data);
    const statemap_geojson = topojson.feature(indiamapdata, indiamapdata.objects.states);
    const districtmap_geojson = topojson.feature(indiamapdata, indiamapdata.objects.districts);
    const state_meshdata = topojson.mesh(indiamapdata, indiamapdata.objects.states);
    let metric_selected = $('.metric-option.active').attr('value');

    await statechloromap(statemap_geojson, maxdata, metric_selected);

    buttonChange(statemap_geojson, districtmap_geojson, state_meshdata, maxdata, start_date, end_date, category, sub_category, state); // Assuming this doesn't return a Promise

    const btn_india_district_map = d3.select('#india-district-map-btn')
    const btn_india_state_map = d3.select('#india-state-map-btn')
    const btn_chloro_map_style = d3.select('#chloro-viz-btn')
    const btn_bubble_map_style = d3.select('#bubble-viz-btn')

    const btn_orders_metrics = d3.select('#orders-metrics-btn')

    const btnarr = new Array(
        btn_india_district_map,
        btn_india_state_map,
        btn_chloro_map_style,
        btn_bubble_map_style,
        btn_orders_metrics,
    );
    buttonvaluecheck(
        btnarr,
        statemap_geojson,
        districtmap_geojson,
        state_meshdata, maxdata
    );
    plotStateMap(map_state_data,metric_selected);

    negativeValue();



}

function updateTopCardsDelta(data) {

    updateTopCardMetrics("total-confirmed-orders", data.total_confirmed_orders, "confirmedPrevDate", data.prev_date_range);
    updateTopCardMetrics("confirmed-orders-change", data.cnf_delta, "india-items-per-order", data.avg_items);

    updateTopCardMetrics("india-active-pincodes", data.total_districts, "districtsPrevDate", data.prev_date_range);
    updateTopCardMetrics("active-pincodes-change", data.district_delta, "max_orders_delivered_area", data.max_orders_delivered_area);
    negativeValue();

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
        districtchloromap(districtmap_geojson, maxdata, metric_selected);
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

    const btn_orders_metrics = d3.select('#orders-metrics-btn')

    const btnarr = new Array(
        btn_india_district_map,
        btn_india_state_map,
        btn_chloro_map_style,
        btn_bubble_map_style,
        btn_orders_metrics
    );

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
    btn_orders_metrics.on('click', async () => {
        if (!btn_orders_metrics.classed('active')) {
            btn_orders_metrics.classed('active', true)
        }
        buttonvaluecheck(btnarr, statemap_geojson, districtmap_geojson, state_meshdata, maxdata);
        let metric_selected  = $('.metric-option.active').attr('value');
        plotStateMap(map_state_data, metric_selected);
        $('.nav-item a[href="#summary"]').tab('show');

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
    const statenametostatecode_2 = { "India": "TT", "Maharashtra": "MH", "Tamil Nadu": "TN", "Andhra Pradesh": "AP", "Karnataka": "KA", "Delhi": "DL", "Uttar Pradesh": "UP", "West Bengal": "WB", "Bihar": "BR", "Telangana": "TG", "Gujarat": "GJ", "Assam": "AS", "Rajasthan": "RJ", "Odisha": "OR", "Haryana": "HR", "Madhya Pradesh": "MP", "Kerala": "KL", "Punjab": "PB", "Jammu and Kashmir": "JK", "Jharkhand": "JH", "Chhattisgarh": "CT", "Uttarakhand": "UT", "Goa": "GA", "Tripura": "TR", "Puducherry": "PY", "Manipur": "MN", "Himachal Pradesh": "HP", "Nagaland": "NL", "Arunachal Pradesh": "AR", "Andaman and Nicobar Islands": "AN", "Ladakh": "LA", "Chandigarh": "CH", "Dadra and Nagar Haveli and Daman and Diu": "DN", "Meghalaya": "ML", "Sikkim": "SK", "Mizoram": "MZ", UN:"State Unassigned" }

    $('.state-name').text(selected_state);

    const statecasedata = map_state_data
    localStorage.setItem('statename', selected_state);
    localStorage.setItem('statecode', statecode);
    let metric_selected  = $('.metric-option.active').attr('value');

    plotStateMap(map_state_data,metric_selected);
}

function formatNumber(num){
   var num_parts = num.toString().split(".");
   num_parts[0] = num_parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
   return num_parts.join(".");
}
function updateTopCardMetrics(id, data, changeid, datachange) {
   const element = document.getElementById(id);
   const changeElement = document.getElementById(changeid);

   const numericData = Number(data);
   if (!isNaN(numericData)) {
       element.innerText = `${formatNumber(numericData)}`;
   } else {
       element.innerText = data;
   }

   const numericDataChange = Number(datachange);
   if (!isNaN(numericDataChange)) {
       if (numericDataChange) {
           changeElement.innerText = `${formatNumber(numericDataChange)}`;
       }
   } else {
       changeElement.innerText = datachange;
   }
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
