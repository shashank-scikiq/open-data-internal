var treeData = null;

async function fetchTreeData(domainName, startDate, endDate, category, subCategory, state) {
  // const SessionStatename = localStorage.getItem('statename');
  const queryParams = new URLSearchParams({ startDate, endDate, domainName });
  
  if (category) queryParams.append('category', category);
  if (subCategory) queryParams.append('subCategory', subCategory);
  if (state) queryParams.append('state', state);

  const url = `/dashboard/api/top_seller_states/?${queryParams.toString()}`;

  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching tree data:', error);
    throw error;
  }
}


async function loadTreeData(domainName, startDate, endDate, category, subCategory) {
  const SessionStatename = localStorage.getItem('statename');
  try {
    if (SessionStatename) {
      treeData = await fetchTreeData(domainName, startDate, endDate, category, subCategory, SessionStatename);
    } else {
      const state = default_state;
      treeData = await fetchTreeData(domainName, startDate, endDate, category, subCategory, state);
    }
    return treeData;
    // Further processing of treeData if required
  } catch (error) {
    console.error('Error loading tree data:', error);
  }
}


async function loadAndCreateTreeChart(domainName, startDate, endDate, category, subCategory) {
  try {
    const treeData = await loadTreeData(domainName, startDate, endDate, category, subCategory);
    create_chart(treeData);
  } catch (error) {
    console.error('Error in loading and creating tree chart:', error);
  }
}


function create_chart(treeData){

  
  d3.select("#inntraDistrictTree").selectAll("*").remove();
  
  // Set the dimensions and margins of the diagram
  var margin_mr = { top: 0, right: 0, bottom: 0, left: 180 },
    width_w = 540 - margin_mr.left - margin_mr.right,
    height_t = 250 - margin_mr.top - margin_mr.bottom;
  
  // Append the SVG object to the body of the page
  var svg_d3 = d3
    .select("#inntraDistrictTree")
    .append("svg")
    .attr("width", width_w + margin_mr.right + margin_mr.left)
    .attr("height", height_t + margin_mr.top + margin_mr.bottom)
    .append("g")
    .attr("transform", "translate(" + (width_w + margin_mr.right) + "," + margin_mr.top + ")");
  
  var i = 0,
    duration = 750,
    root;
  
  // Declare a tree layout and assign the size
  var treemap = d3.tree().size([height_t, width_w]);
  
  // Assign parent, children, height, depth
  root = d3.hierarchy(treeData, function (d) {
    return d.children;
  });
  root.x0 = height_t / 2;
  root.y0 = 0;
  
  // Collapse after the second level
  root.children.forEach(collapse);
  
  update(root);
  
  // Collapse the node and all its children
  function collapse(d) {
    if (d.children) {
      d._children = d.children;
      d._children.forEach(collapse);
      d.children = null;
    }
  }
  
  function update(source) {
    // Assign the x and y position for the nodes
    var treeData = treemap(root);
  
    // Compute the new tree layout
    var nodes = treeData.descendants(),
      links = treeData.descendants().slice(1);
  
    // Normalize for fixed-depth
    nodes.forEach(function (d) {
      d.y = d.depth * -180; // Adjusted y-coordinate for right-to-left direction
    });
  
    // ****************** Nodes section ***************************
  
    // Update the nodes...
    var node = svg_d3.selectAll("g.node").data(nodes, function (d) {
      return d.id || (d.id = ++i);
    });
  
    // Enter any new modes at the parent's previous position
    var nodeEnter = node
      .enter()
      .append("g")
      .attr("class", "node")
      .attr("transform", function (d) {
        return "translate(" + source.y0 + "," + source.x0 + ")";
      })
      .on("click", click);
  
    // Add Circle for the nodes
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
        return -12; // Adjust the x-coordinate for the icon
        })
        .attr("y", -12) // Adjust the y-coordinate for the icon
        .attr("width", 24)
        .attr("height", 24)
        .attr("class", "node-icon")
        .html(function (d) {
            // Check if it's the first node and apply a different icon
            if (d.depth === 0) {
              return '<i class="mdi mdi-home"></i>'; // Change the icon for the first node
            } else {
              return '<i class="mdi mdi-truck-delivery-outline"></i>'; // Use the default icon for other nodes
            }
          });

        // .html('<i class="mdi mdi-truck-delivery-outline"></i>'); // You can replace this with your own icon or SVG content

    // Add labels for the nodes
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
  
    // UPDATE
    var nodeUpdate = nodeEnter.merge(node);
  
    // Transition to the proper position for the node
    nodeUpdate
      .transition()
      .duration(duration)
      .attr("transform", function (d) {
        return "translate(" + d.y + "," + d.x + ")";
      });
  
    // Update the node attributes and style
    nodeUpdate
      .select("circle.node")
      .attr("r", 12)
      .style("fill", function (d) {
        return d._children ? "lightgreen" : "#fff";
      })
      .attr("cursor", "pointer");
  
    // Remove any exiting nodes
    var nodeExit = node.exit().transition().duration(duration).attr("transform", function (d) {
      return "translate(" + source.y + "," + source.x + ")";
    }).remove();
  
    // On exit reduce the node circles size to 0
    nodeExit.select("circle").attr("r", 1e-6);
  
    // On exit reduce the opacity of text labels
    nodeExit.select("text").style("fill-opacity", 1e-6);
  
    // ****************** Links section ***************************
  
    // Update the links...
    var link = svg_d3.selectAll("path.link").data(links, function (d) {
      return d.id;
    });
  
    // Enter any new links at the parent's previous position
    var linkEnter = link
      .enter()
      .insert("path", "g")
      .attr("class", "link")
      .attr("d", function (d) {
        var o = { x: source.x0, y: source.y0 };
        return diagonal(o, o);
      });
  
    // UPDATE
    var linkUpdate = linkEnter.merge(link);
  
    // Transition back to the parent element position
    linkUpdate
      .transition()
      .duration(duration)
      .attr("d", function (d) {
        return diagonal(d, d.parent);
      });
  
    // Remove any exiting links
    var linkExit = link.exit().transition().duration(duration).attr("d", function (d) {
      var o = { x: source.x, y: source.y };
      return diagonal(o, o);
    }).remove();
  
    // Store the old positions for transition
    nodes.forEach(function (d) {
      d.x0 = d.x;
      d.y0 = d.y;
    });
  
    // Creates a curved (diagonal) path from parent to the child nodes
    function diagonal(s, d) {
      path = `M ${s.y} ${s.x}
              C ${(s.y + d.y) / 2} ${s.x},
                ${(s.y + d.y) / 2} ${d.x},
                ${d.y} ${d.x}`;
  
      return path;
    }
  
    // Toggle children on click
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