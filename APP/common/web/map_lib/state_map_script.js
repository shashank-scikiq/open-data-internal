const bubblecolormapper = {
    map_total_active_sellers_metrics: ["rgba(0,123,255,0.8)", "rgba(0,123,255,0.5)", "rgba(0,123,255,0.5)"], // Product
    map_total_orders_metrics: ["rgba(253,127,58,0.8)", "rgba(253,127,58,0.5)", "rgba(253,127,58,0.5)"], // Seller
    map_total_zonal_commerce_metrics: ["rgba(16,183,89,0.8)", "rgba(16,183,89,0.5)", "rgba(16,183,89,0.5)"], // Pincode
}



//const a = new Date()
    //.text(`${a.getDate()}/${a.getMonth() + 1}/${a.getFullYear()}`)

let SessionStatename = localStorage.getItem('statename')
let SessionStatecode = localStorage.getItem('statecode')

    if (SessionStatename && SessionStatecode) {
        // document.getElementById('statename').innerText = SessionStatename + " " + SessionStatecode
        localStorage.setItem('change_cd_st', SessionStatecode)
    }
    else {
        SessionStatename = "Karnataka"
        SessionStatecode = "KA"
        // document.getElementById('statename').innerText = SessionStatename
        localStorage.setItem('change_cd_st', SessionStatecode)
    }

function mapprojection(data) {
    const el = document.getElementById("statemap")
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

export async function plotStateMap(map_state_data,metricValue) {
    let latest_state_json = map_state_data
    SessionStatename = localStorage.getItem('statename');
    SessionStatecode = localStorage.getItem('statecode');

    const lst_order_demand_st = new Array();
    const lst_active_sellers_st = new Array();
    const lst_total_intradistrict_orders_percentage_st = new Array();


    if (SessionStatecode === null || SessionStatecode === undefined || SessionStatecode === "undefined") {
        let selected_state = $('#state-list option:selected').text();
        let statecode = $('#state-list option:selected').val();
    
        if (statecode && statecode !== "undefined") {
            $('.state-name').text(selected_state);
            SessionStatename = selected_state;
            SessionStatecode = statecode;
            localStorage.setItem('statename', selected_state);
            localStorage.setItem('statecode', statecode);
        } else {
            SessionStatecode='TT'
        }
    }
    try {
    const SessionStatecode = localStorage.getItem('statecode');

    let state_card_data = {};
    let lst_order_demand = [];
    let lst_active_sellers = [];
    let lst_total_intradistrict_percentage = [];

    if (SessionStatecode in latest_state_json) {
        if (typeof latest_state_json[SessionStatecode].districts === 'object' && latest_state_json[SessionStatecode].districts !== null) {
            Object.keys(latest_state_json[SessionStatecode].districts).forEach(key => {
                const element = latest_state_json[SessionStatecode].districts[key];
            if (element.active_sellers <= 3) {
                element.active_sellers = 0;
            }
            let order_demand_st = element.order_demand || 0;
            let active_sellers_st = element.active_sellers || 0;
            let total_intradistrict_percentage_st = element.intradistrict_percentage || 0;

            lst_order_demand.push(order_demand_st);
            lst_active_sellers.push(active_sellers_st);
            lst_total_intradistrict_percentage.push(total_intradistrict_percentage_st);
        });

        state_card_data['active_sellers'] = lst_active_sellers;
        state_card_data['order_demand'] = lst_order_demand;
        state_card_data['intradistrict_percentage'] = lst_total_intradistrict_percentage;

    }
    }else {
        latest_state_json[SessionStatecode] = {};
        latest_state_json[SessionStatecode]["districts"] = {};
        latest_state_json[SessionStatecode]["districts"][SessionStatename] = {
            "order_demand": "0",
            "total_items_delivered": "0",
            "active_sellers": 0,
            "intradistrict_orders": "0",
            "intrastate_orders": "0",
            "intradistrict_percentage": "0",
            "intrastate_percentage": "0"
        };
        latest_state_json[SessionStatecode]["total"] = {
            "order_demand": "0",
            "total_items_delivered": "0",
            "active_sellers": 0,
            "intradistrict_orders": "0",
            "intrastate_orders": "0",
            "intradistrict_percentage": "0",
            "intrastate_percentage": "0"
        };
        state_card_data = latest_state_json[SessionStatecode].total;
    }

    if (state_card_data.active_sellers <= 3) {
        state_card_data.active_sellers = 0;
    }

    const maxdata = {
        map_total_active_sellers_metrics: state_card_data.active_sellers && state_card_data.active_sellers.length > 0 ? d3.max(state_card_data.active_sellers, d => +d) : 0,
        map_total_orders_metrics: state_card_data.order_demand && state_card_data.order_demand.length > 0 ? d3.max(state_card_data.order_demand, d => +d) : 0,
        map_total_zonal_commerce_metrics: state_card_data.intradistrict_percentage && state_card_data.intradistrict_percentage.length > 0 ? d3.max(state_card_data.intradistrict_percentage, d => +d) : 0
    };

    if (SessionStatecode === null) {
        return null; // or handle it in a way that makes sense for your application
    } else {
        const each_state_topo = await fetchspecificmapdata(map_state_data);
        const each_state_geojson = topojson.feature(each_state_topo, each_state_topo.objects.districts);
        const each_state_mesh = topojson.mesh(each_state_topo, each_state_topo.objects.districts);

        each_state_border(each_state_geojson, each_state_mesh, metricValue);
        each_state_chloro(each_state_geojson, maxdata, metricValue);
        buttontoggle(each_state_geojson, each_state_mesh, maxdata);
    }
} catch (e) {
    console.error('Error:', e);
}
}

function titleCase(str) {
    if (str === null) {
      return null;
    }
    return str.toLowerCase().replace(/\b\w/g, (s) => s.toUpperCase());
  }


function normalizeString(str) {
    return str.toUpperCase().trim().replace(/\s+/g, '').replace(/[.,'’]/g, '');
}

async function fetchspecificmapdata(map_state_data) {
    const loaderDiv = `<div class="innerLoader bg-black-1-">
        <div class="d-flex ht-40 justify-content-center pd-10">
            <span class="spinner-border spinner-border-sm bd-2 mg-b-25" role="status" aria-hidden="true"></span>
            <h6 class="mg-l-10 tx-16 tx-bold">Loading ${SessionStatename} Map</h6>
        </div>
     </div>`
    $('#stateMapLoader').html(loaderDiv);
    SessionStatename = localStorage.getItem('statename');
    SessionStatecode = localStorage.getItem('statecode');
    let res = await fetch(`/static/map_lib/mapdata/${titleCase(SessionStatename)}.json`)
    let each_state_map_data = await res.json()
    let latest_state_json = map_state_data

    let each_district_data = latest_state_json[SessionStatecode].districts

    each_state_map_data.objects.districts.geometries.forEach(el => {
        let districtName = (el.properties.district).toUpperCase().trim().replace(/\s+/g, ' ').replace(/[.,'’]/g, '');
        let normalizedDistrictName = normalizeString(districtName);
    
        let matchFound = false;
        let total_data;
    
        if (each_district_data[districtName]) {
            total_data = each_district_data[districtName];
            matchFound = true;
        } else if (each_district_data[normalizedDistrictName]) {
            total_data = each_district_data[normalizedDistrictName];
            matchFound = true;
        }
    
        if (matchFound) {
                    
            if (total_data.active_sellers <= 3){
                total_data.active_sellers = 0

            }
            el.properties['totalcasedata'] = {
                map_total_orders_metrics: total_data.order_demand ? total_data.order_demand : 0,
                map_total_active_sellers_metrics: total_data.active_sellers ? total_data.active_sellers : 0,
                map_total_zonal_commerce_metrics: total_data.intradistrict_percentage ? total_data.intradistrict_percentage : 0,
            };
        } else {
            el.properties['totalcasedata'] = nocasedata;
        }
    });

    $(".innerLoader").remove()
    return each_state_map_data

}

function each_state_border(each_state_geojson, each_state_mesh, casetype) {
    let mapprojectionresult = mapprojection(each_state_geojson)
    $('#each-state-border').html("");
    $('#each-state-bubble').html("");

    d3.select('#each-state-border')
        .append("path")
        .attr("stroke", bubblecolormapper[casetype][2])
        .attr("stroke-width", 1.5)
        .style('z-index', 5)
        .attr('fill', 'none')
        .attr("d", mapprojectionresult[1](each_state_mesh));

}

var chloroplethcolormapper3 = {
    map_total_orders_metrics:["#ffffff", "#FF7722"],
    map_total_active_sellers_metrics: ["#ffffff", "#1c75bc"], 
    map_total_zonal_commerce_metrics: ["#ffffff", "#10b759"],
}
var chloroplethcolormapper2 = {
    map_total_orders_metrics:["#ffffff", "#f9f0e9", "#FF7722"],
    map_total_active_sellers_metrics: ["#ffffff", "#dfebf5", "#1c75bc"], 
    map_total_zonal_commerce_metrics: ["#ffffff", "#71d49c", "#10b759"],
}


// function customColorRange(value, max) {
//     const step = max / 7;
//     let selectedMetric = $('.metric-option.active').attr('value');
//     if (value === 0) return "#ffffff";
//     switch (selectedMetric) {
//         case "map_total_orders_metrics":
//             return value <= step ? "#fef0d7" :
//                    value <= 2 * step ? "#ff9e9f" :
//                    value <= 3 * step ? "#f78e68" :
//                    value <= 4 * step ? "#fed976" :
//                    value <= 5 * step ? "#f7a448" :
//                    value <= 6 * step ? "#f87e67" :
//                    "#e3570a";
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

function each_state_chloro(each_state_geojson, maxdata, casetype) {
    $("#each-state-chloro-btn").addClass("active");
    $("#each-state-bubble-btn").removeClass("active");

    const mapprojectionresult = mapprojection(each_state_geojson);
    const color = d3.scaleSequentialLog(chloroplethcolormapper3[casetype]).domain([1, maxdata[casetype]]);
    const sortedData = each_state_geojson.features.sort((a, b) => b.properties.totalcasedata[casetype] - a.properties.totalcasedata[casetype]);
    const top3Data = sortedData.slice(0, 3);

    const iconWidth = 35;
    const iconHeight = 35;

    let customColorRange;
    const metricText = getMetricKey(casetype);
    if (metricText === "map_total_orders_metrics") {
            customColorRange = d3.scaleLinear()
            .domain([0, 1, maxdata[casetype]])
            .range(chloroplethcolormapper2[casetype]); 
        } else if (metricText === "map_total_active_sellers_metrics") {
            customColorRange = d3.scaleLinear()
            .domain([0, 1, maxdata[casetype]])
            .range(chloroplethcolormapper2[casetype]); 
        }else if (metricText === "map_total_zonal_commerce_metrics") {
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
    
    

    $('#each-state-border').html("");
    $('#each-state-chloro').html("");
    $('#each-state-bubble').html("");

    const g = d3.select('#each-state-chloro');

    if (getMetricKey(casetype) === "Intrastate Percentage") {
        var metricTextKey = "Intradistricts Percentage";
    } else {
        var metricTextKey = getMetricKey(casetype);
    }
    g.selectAll('path')
        .data(each_state_geojson.features)
        .enter()
        .append('path')
        .attr('d', (data) => mapprojectionresult[1](data))
        .attr('fill', (el) => customColorRange(el.properties.totalcasedata[casetype], maxdata[casetype]))
        .attr('stroke-width', 0.5)
        .attr('stroke', 'black')
        .attr('class', 'state')
        .attr("data-title", (i) => {
            const value = i.properties.totalcasedata[casetype];
            return `State: ${i.properties.st_nm}<br/> District : ${i.properties.district}<br/> ${metricTextKey} : ${
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
            // d3.selectAll('.state').style('opacity','.5');
            // d3.select(this).style('opacity','1');
        })
        .on('mouseout', function () {
            d3.select(this).attr('stroke-width', 0.5);
            hideTooltip();
            $(".tooltip").tooltip("hide");
            // d3.selectAll('.state').style('opacity','1');

        });


    d3.select('#each-state-chloro').select('.icon-container').remove();
    const iconContainer = d3.select('#each-state-chloro').append('g');
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
            } else if (metricText === "Total Active Sellers") {
                iconClass = "mdi mdi-account";
                metricValue = i.properties.totalcasedata[casetype];
            } else if (metricText === "Intrastate Percentage") {
                iconClass = "mdi mdi-truck-delivery";
                metricValue = `${i.properties.totalcasedata[casetype]}%`;
            } else {
                iconClass = "mdi mdi-cart-variant";
                metricValue = i.properties.totalcasedata[casetype];
            }
          
            return `<div class="pointer" data-toggle="tooltip" data-placement="top" data-html="true" title="State: ${i.properties.st_nm}</br>Districts: ${i.properties.district}</br>${metricTextKey}: ${metricValue.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")}"><i class="${iconClass}"></i></div><div class="pulse"></div>`;
          });

    $("path").tooltip({
        container: 'body',
        html: true,
        placement: 'top'
    });

    $('[data-toggle="tooltip"]').tooltip();
    addStateLegend(customColorRange, casetype, maxdata[casetype]);
}


function handleMouseover(event, d, casetype, color, top3Data) {
    if (d && d.properties && d.properties.district) {
        const tooltipContent = generateTooltipContent(d, casetype, color, top3Data);
        showTooltip(tooltipContent);
        
    }
}

function getMetricValue(metricTextKey, casetype, d) {
    if (metricTextKey === 'Total Active Sellers' && d.properties.totalcasedata[casetype] === 0) {
        return 'No Data';
    } else if (metricTextKey === 'Intradistricts Percentage') {
        return new Intl.NumberFormat().format(d.properties.totalcasedata[casetype]) + '%';
    } else {
        return new Intl.NumberFormat().format(d.properties.totalcasedata[casetype]);
    }
}

function generateTooltipContent(d, casetype, color, top3Data) {
    let metricTextKey = getMetricKey(casetype);

    if (getMetricKey(casetype) === "Intrastate Percentage") {
        metricTextKey = "Intradistricts Percentage";
    } 

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
            <h6 class="tx-uppercase tx-11 tx-spacing-1 tx-color-03 tx-semibold mg-b-0">${metricTextKey}</h6>
            <h6 class="tx-uppercase tx-11 tx-spacing-1 tx-color-03 tx-semibold mg-b-0 mg-l-3">in</h6>
        </div>
        <h3 class="tx-normal tx-rubik mg-b-0 dist_desc"><i class="mdi mdi-map-marker-outline"></i> ${d.properties.district}</h3>
        <h3 class="tx-bold mg-b-5 total_count_txt ${metricTextKey === 'Total Active Sellers' && d.properties.totalcasedata[casetype] === 0 ? 'tx-50' : 'tx-70'}" style="line-height: ${metricTextKey === 'Total Active Sellers' && d.properties.totalcasedata[casetype] === 0 ? '55px' : '65px'}; color: ${colorValue};">
            ${getMetricValue(metricTextKey, casetype, d)}
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

function getTopDistrictsHTML(top3Data, casetype) {
    return top3Data.map((district) => `
        <div class="media mg-b-6">
            <div class="crypto-icon crypto-icon-sm bg-primary op-8">
                <i class="mdi mdi-map-marker-outline tx-26"></i>             
            </div>
            <div class="media-body pd-l-8">
                <h6 class="tx-11 tx-spacing-1 tx-color-03 tx-uppercase tx-semibold mg-0">${district.properties.district}</h6>
                <h4 class="tx-18 tx-rubik tx-bold tx-brand-01 mg-b-0 dist_title_text">
                ${casetype === 'map_total_active_sellers_metrics' && district.properties.totalcasedata[casetype] === 0
                ? 'No Data'
                : (casetype === 'map_total_zonal_commerce_metrics'
                    ? new Intl.NumberFormat().format(district.properties.totalcasedata[casetype]) + '%'
                    : new Intl.NumberFormat().format(district.properties.totalcasedata[casetype]))
                }
                </h4>
            </div>
        </div>
    `).join('');
}


function addStateLegend(customColorRange, casetype, maxdata, topDistVal) {
    const legendContainer = d3.select('#mapLegends');
    legendContainer.html('');

    const maxDivisions = maxdata < 50 ? 2 : 5;

    const divisionFactor = maxDivisions === 1 ? maxdata : maxdata / (maxDivisions - 1);

    const legendValues = [0, ...Array.from({ length: maxDivisions - 1 }, (_, i) => (i + 1) * divisionFactor)];

    const legendHeight = 20;
    const newLegendContainer = legendContainer.append('svg')
        .attr('class', 'legend')
        .attr('width', 20)
        .attr('height', legendHeight * maxDivisions + 40)

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
        .attr('transform', (d, i) => `translate(0, ${i * (200 / 8) + 20})`);

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
                    return `${startRange.toLocaleString()}%`;
                } else if (i === 1) {
                    return `< ${endRange.toLocaleString()}%`;
                } else if (i === legendValues.length - 1) {
                    return `> ${startRange.toLocaleString()}%`;
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

function each_state_bubble(each_state_geojson, maxdata, casetype) {
    d3.select('#each-state-chloro').select('.icon-container').remove();

    const color = d3.scaleSequentialLog(chloroplethcolormapper2[casetype]).domain([1, maxdata[casetype]]);
    const sortedData = each_state_geojson.features.sort((a, b) => b.properties.totalcasedata[casetype] - a.properties.totalcasedata[casetype]);
    const top3Data = sortedData.slice(0, 3);
    const iconWidth = 35;
    const iconHeight = 35;

    let customColorRange;
    const metricText = getMetricKey(casetype);
    if (metricText === "Total Confirmed Orders ") {
        customColorRange = d3.scaleLinear()
        .domain([0, 1, maxdata[casetype]])
        .range(chloroplethcolormapper2[casetype]); 
    } else if (metricText === "Total Active Sellers") {
        customColorRange = d3.scaleLinear()
        .domain([0, 1, maxdata[casetype]])
        .range(chloroplethcolormapper2[casetype]); 
    }else if (metricText === "Intrastate Percentage") {
        customColorRange = d3.scaleLinear()
        .domain([0, 1, maxdata[casetype]])
        .range(chloroplethcolormapper2[casetype]); 
    } else {
        customColorRange = d3.scaleLinear()
        .domain([0, 0.1, maxdata[casetype]])
        .range(chloroplethcolormapper2[casetype]); 
    }

    $('#each-state-chloro').html("");
    $('#each-state-bubble').html("");

    if (getMetricKey(casetype) === "Intrastate Percentage") {
        var metricTextKey = "Intradistricts Percentage";
    } else {
        var metricTextKey = getMetricKey(casetype);
    }


    const g = d3.select('#each-state-bubble')

    const bubbleradius = d3.scaleSqrt()
        .domain([0, maxdata[casetype]])
        .range([3, 40]);

    const mapprojectionresult = mapprojection(each_state_geojson)

    const sorteddata = each_state_geojson.features.sort((a, b) => b.properties.totalcasedata[casetype] - a.properties.totalcasedata[casetype])

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
            handleMouseover.call(this, event, d, casetype, color, top3Data);
            // updatemaphoverdata(d, i)
        })
        .on('mouseout', function (d, i) {
            d3.select(this).attr("fill-opacity", 0.25).attr('stroke', bubblecolormapper[casetype][0]);
            hideTooltip();
            $(".tooltip").tooltip("hide");
        });

        d3.select('#each-state-bubble').select('.icon-container').remove();
        const iconContainer = d3.select('#each-state-bubble').append('g');
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
                } else if (metricText === "Total Active Sellers") {
                    iconClass = "mdi mdi-account";
                    metricValue = i.properties.totalcasedata[casetype];
                } else if (metricText === "Intrastate Percentage") {
                    iconClass = "mdi mdi-truck-delivery";
                    metricValue = `${i.properties.totalcasedata[casetype]}%`;
                } else {
                    iconClass = "mdi mdi-cart-variant";
                    metricValue = i.properties.totalcasedata[casetype];
                }
              
                return `<div class="pointer" data-toggle="tooltip" data-placement="top" data-html="true" title="State: ${i.properties.st_nm}</br>Districts: ${i.properties.district}</br>${metricTextKey}: ${metricValue.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")}"><i class="${iconClass}"></i></div><div class="pulse"></div>`;
              });
    $("circle").tooltip({
        container: 'body',
        html: true,
        placement: 'top'
    });

    $('[data-toggle="tooltip"]').tooltip();

}

function buttonvaluecheck(btnarray, each_state_geojson, each_state_mesh, maxdata) {

    d3.select('#each-state-border').selectAll('path').remove()
    d3.select('#each-state-chloro').selectAll('path').remove()
    d3.select('#each-state-bubble').selectAll('circle').remove()

    const nwbtnarry = btnarray.filter(a => a.classed('active'))
    const nwbtnarry2 = nwbtnarry.map(a => a.attr('value'))

    let metric_selected  = $('.metric-option.active').attr('value');

    if (nwbtnarry2.includes("chloro")) {
        each_state_chloro(each_state_geojson, maxdata, metric_selected)
    }
    else if (nwbtnarry2.includes("bubble")) {
        each_state_border(each_state_geojson, each_state_mesh, metric_selected)
        each_state_bubble(each_state_geojson, maxdata, metric_selected)
    }
    else {

    }
}
function buttontoggle(each_state_geojson, each_state_mesh, maxdata) {
    const btn1_1 = d3.select('#each-state-chloro-btn')
    const btn2_1 = d3.select('#each-state-bubble-btn')

    const btnarr = new Array(
        btn1_1, 
        btn2_1, 
    );



    btn1_1.on('click', (e, i) => {
        if (btn1_1.classed('active')) {

        }
        else {
            btn1_1.classed('active', true)
            btn2_1.classed('active', false)

        }
        buttonvaluecheck(btnarr, each_state_geojson, each_state_mesh, maxdata)

    })
    btn2_1.on('click', (e, i) => {
        if (btn2_1.classed('active')) {

        }
        else {
            btn2_1.classed('active', true)
            btn1_1.classed('active', false)

        }
        buttonvaluecheck(btnarr, each_state_geojson, each_state_mesh, maxdata)
    })
}
buttontoggle()
