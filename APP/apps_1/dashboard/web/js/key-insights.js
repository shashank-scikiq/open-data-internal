async function fetchData() {
    try {
        const response = await fetch('api/key_insights/');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching data:', error);
        return null;
    }
}


function generateCardTemplate(keyInsightHTML, time_period) {
    return `
        <div class="card item slide_items">
            <div class="card-body pd-10 card-text" style="height: 130px;">
                <div class="d-flex flex-column tx-center align-items-center">
                    ${keyInsightHTML}
                </div>
            </div>
            <div class="card-footer card-footer-text pd-x-10 pd-y-5 tx-right">
                ${time_period}
            </div>
        </div>`;
}

function updateFunFacts(data, elementId) {
if (!data) {
    console.error('No data to update');
    return;
}

const element = document.getElementById(elementId);
if (!element) {
    console.error(`${elementId} element not found`);
    return;
}
const { seller_card, state_order_volume, state_order_volume_weekwise, 
    district_order_volume, district_order_volume_weekwise, 
    subcategory_order_volume, unique_items, highest_order_by_seller } = data;

element.innerHTML = '';

// if (seller_card) {
//     const { percentage_seller, percentage_of_orders, current_period } = seller_card;
//     const cardHTML = generateCardTemplate(`
//         <h3 class="tx-rubik">${percentage_seller}%</h3>
//         <div class="card-text tx-medium">Percent of the Active Sellers are contributing to
//         <span class="m-0">${percentage_of_orders}%</span>
//         of total delivered orders
//         </div>
//     `, current_period);
//     element.innerHTML += cardHTML;
// }
if (state_order_volume) {
    const { delta_volume_max_state, state_name, current_period, previous_period } = state_order_volume;
    const time_period = current_period + ' Vs ' + previous_period
    const cardHTML = generateCardTemplate(`
        <div class="card-text mg-b-10 tx-medium">
            State with highest increase in order volume is
            <span class="mg-x-5-f text-truncate" style="max-width:200px;">${state_name}</span>
            at
        </div>
        <div class="d-flex justify-content-center align-items-end card-text">
            <h3 class="tx-rubik">${delta_volume_max_state}%</h3>
            <p class="card-text mg-l-3 tx-16 tx-medium">since last month</p>
        </div>
    `, time_period);
    element.innerHTML += cardHTML;
}
if (state_order_volume_weekwise) {
    const { delta_volume_max_state, state_name, current_period, previous_period} = state_order_volume_weekwise;

    const time_period = current_period + ' Vs ' + previous_period

    const cardHTML = generateCardTemplate(`
        <div class="card-text mg-b-10 tx-medium">
            State with highest increase in Intrastate % Order Volume is
            <span class="mg-x-5-f text-truncate" style="max-width:200px;">${state_name}</span>
            at
        </div>
        <div class="d-flex justify-content-center align-items-end card-text w-100">
            <h3 class="tx-rubik" style="max-width:290px">${delta_volume_max_state}%</h3>
            <p class="card-text mg-l-3 tx-16 tx-medium">since last month</p>
        </div>
    `, time_period);
    element.innerHTML += cardHTML;
}
if (district_order_volume) {
    const { delta_volume_max_state, district_name , current_period, previous_period } = district_order_volume;
    const time_period = current_period + ' Vs ' + previous_period
    const cardHTML = generateCardTemplate(`
        <div class="card-text mg-b-10 tx-medium">
            District with highest increase in order volume is
            <span class="mg-x-5-f text-truncate" style="max-width:200px;">${district_name}</span>
            at
        </div>
        <div class="d-flex justify-content-center align-items-end card-text w-100">
            <h3 class="tx-rubik" style="max-width:290px">${delta_volume_max_state}%</h3>
            <p class="card-text mg-l-3 tx-16 tx-medium">since last month</p>
        </div>
    `, time_period);
    element.innerHTML += cardHTML;
}

if (district_order_volume_weekwise) {
    const { delta_volume_max_state, district_name , current_period, previous_period} = district_order_volume_weekwise;
    const time_period = current_period + ' Vs ' + previous_period
    const cardHTML = generateCardTemplate(`
        <div class="card-text mg-b-10 tx-medium">
            District with highest increase in Intradistrict % order volume is
            <span class="mg-x-5-f text-truncate" style="max-width:200px;">${district_name}</span>
            at
        </div>
        <div class="d-flex justify-content-center align-items-end card-text">
            <h3 class="tx-rubik">${delta_volume_max_state}%</h3>
            <p class="card-text mg-l-3 tx-16 tx-medium">since last week</p>
        </div>
    `, time_period);
    element.innerHTML += cardHTML;

}
if (subcategory_order_volume && includeCategory) {
    const { delta_volume_max_subcat, sub_category , current_period, previous_period} = subcategory_order_volume;

    const time_period = current_period + ' Vs ' + previous_period

    const cardHTML = generateCardTemplate(`
        <div class="card-text mg-b-10 tx-medium">
            Sub-Category with highest increase in Order Volume is
            <span class="mg-x-5-f text-truncate text-nowrap" style="max-width:200px;">${sub_category}</span>
            at
        </div>
        <div class="d-flex justify-content-center align-items-end card-text">
            <h3 class="tx-rubik">${delta_volume_max_subcat}%</h3>
            <p class="card-text mg-l-3 tx-16 tx-medium">since last month</p>
        </div>
    `, time_period);
    element.innerHTML += cardHTML;
}

if (unique_items) {
    const { unique_item_count, delta_mtd_unique_items } = unique_items;
    const cardHTML = generateCardTemplate(`
        <div class="card-text mg-b-10 tx-medium">
            Unique Item with highest increase in Order Volume in
            <span class="mg-x-5-f text-truncate" style="max-width:200px;">${delta_mtd_unique_items}</span>
            at
        </div>
        <div class="d-flex justify-content-center align-items-end card-text">
            <h3 class="tx-rubik">${unique_item_count}%</h3>
            <p class="card-text mg-l-3 tx-16 tx-medium">since last month</p>
        </div>
    `, 'Jan 26, 2024 - Jan 31, 2024');
    element.innerHTML += cardHTML;
}

if (highest_order_by_seller) {
    const { order_count, previous_mtd } = highest_order_by_seller;
    const cardHTML = generateCardTemplate(`
        <div class="card-text mg-b-10 tx-medium">
            State with highest increase in Unique Items Order Volume in
            <span class="mg-x-5-f text-truncate" style="max-width:200px;">${previous_mtd}</span>
            at
        </div>
        <div class="d-flex justify-content-center align-items-end card-text">
            <h3 class="tx-rubik">${order_count}%</h3>
            <p class="card-text mg-l-3 tx-16 tx-medium">since last month</p>
        </div>
    `, 'Jan 26, 2024 - Jan 31, 2024');
    element.innerHTML += cardHTML;
}

}

function setTotalItemCount(count) {
    const totalCountElement = document.getElementById('totalItemCount');
    if (totalCountElement) {
        totalCountElement.textContent = `${count}`;
    }
}

setTimeout(function(){
const fetchPostsCarousel = $('#postsCarousel');
fetchPostsCarousel.html('<div class="innerLoader-dot"></div>')
fetchPostsCarousel.show()

fetchData().then(data => {

$(".innerLoader-dot").remove()

updateFunFacts(data, 'postsCarousel');
$('.text-truncate').tooltipOnOverflow();
const totalItemCount = $("#postsCarousel .slide_items").length;
        
setTotalItemCount(totalItemCount);

const postsOwl = $("#postsCarousel");
postsOwl.owlCarousel({
    items: 4,
    margin: 10,
    dots: false,
    // autoplay: true,
    loop: false,
    nav: false,
    slideSpeed: 50000,
    autoplayTimeout:10000,
    autoplayHoverPause:true,
    responsive: {
        0: {
            items: 1
        },
        600: {
            items: 2
        },
        1000: {
            items: 4
        }
    }
});
    $(".next-btn").click(function () {
        postsOwl.trigger("next.owl.carousel");
    });
    $(".prev-btn").click(function () {
        postsOwl.trigger("prev.owl.carousel");
    });
    $(".prev-btn").addClass("disabled");
    $(postsOwl).on("translated.owl.carousel", function (event) {
        if ($(".owl-prev").hasClass("disabled")) {
            $(".prev-btn").addClass("disabled");
        } else {
            $(".prev-btn").removeClass("disabled");
        }
        if ($(".owl-next").hasClass("disabled")) {
            $(".next-btn").addClass("disabled");
        } else {
            $(".next-btn").removeClass("disabled");
        }
    });

});
},2000)