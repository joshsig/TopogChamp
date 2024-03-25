// create an array with nodes
fetch('/levelsData.json')
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
    // You can perform further operations with the data here
    levelsData = data;
    updateData("ring");
  })
  .catch(error => {
    console.error('There was a problem with the fetch operation:', error);
  });


var network = null;
var selectedData = null;

// Function to update the nodes and edges based on the selected level
function updateData(selectedLevel) {
    selectedData = levelsData[selectedLevel];
    if (selectedData) {
        
        var container = document.getElementById("mynetwork");
        // Update nodes and edges arrays based on selected level
        var nodes = selectedData.nodes;
        var edges = selectedData.edges;
        // Perform actions with updated data
        var data = {
            nodes: nodes,
            edges: edges,
          };

        var options = {
            manipulation: Boolean(selectedData.options.manipulation),
        };
        network = new vis.Network(container, data, options);
    } else {
        console.error("Selected level data not found.");
    }
}

function submitAnswer() {
    if (!selectedData) {
        alert("Please select a level first.");
        return;
    }

    if (!network) {
        alert("Network not initialized.");
        return;
    }

    // get the nodes
    let nodes = []
    let curr_edges = []
    for (var i = 0; i < selectedData.nodes.length; i++) {
        console.log(selectedData.nodes[i].id);
        nodes.push(selectedData.nodes[i].id);
    }
    for (var i = 0; i < nodes.length; i++) {
        curr_edges.push(network.getConnectedEdges(nodes[i]));
    }
    
    // check if the answer is correct
    if (curr_edges.length === 5) {
        
        alert("Correct Answer!");
    } else {
        alert("Incorrect Answer!");
    }
}


