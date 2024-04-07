// create an array with nodes
fetch('/levelsData.json')
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
    levelsData = data;
    updateData("ring");
  })
  .catch(error => {
    console.error('There was a problem with the fetch operation:', error);
  });


var network = null;
var selectedData = null;

function resetData() {
    let curr_level = document.getElementById("levelSelect").value;
    updateData(curr_level);
}

// Function to update the nodes and edges based on the selected level
function updateData(selectedLevel) {

    let correct = document.getElementById("correct");
    correct.innerHTML = "";

    selectedData = levelsData[selectedLevel];
    if (selectedData) {

        let goal = selectedData.goal;
        let goalText = document.getElementById("goal");
        goalText.innerHTML = goal;
        
        var container = document.getElementById("mynetwork");
        // Update nodes and edges arrays based on selected level
        var nodes = selectedData.nodes;
        var edges = selectedData.edges;
        // Perform actions with updated data
        var data = {
            nodes: nodes,
            edges: edges,
          };
          
          // ensure json has valid data
        try   {
          arrows = selectedData.options.arrows;
          manipulation = selectedData.options.manipulation;
        } catch (e) {
          arrows = false
          manipulation = true
        }

        var options = {
            manipulation: Boolean(manipulation), 
            edges: { arrows: { to: {enabled: false} } },
            physics: {
                enabled: false,
            },
        };
        network = new vis.Network(container, data, options);

        let adding_edge = false;

        document.addEventListener('keydown', function(event) {
            if (event.key === "Enter") {
                submitAnswer();
            } else if (event.key === "r") {
                    resetData();
            } else if (event.key === "e") {
                if(!adding_edge) {
                    network.enableEditMode();
                    network.addEdgeMode();
                    adding_edge = true;
                } else {
                    network.disableEditMode();
                    adding_edge = false;
                }
            } else if (event.key === "d") {
                network.deleteSelected();
            }
        });

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
        nodes.push(selectedData.nodes[i].id);
    }
    let curr_nodes = network.selectNodes(nodes); 
    for (var i = 0; i < nodes.length; i++) {
        curr_edges.push(network.getConnectedEdges(nodes[i]));
    }

    // generate edge hash table

    // key: edge id
    // value: every node that has that edge
    var edgeHash = new Map();
    for (var i = 0; i < curr_edges.length; i++) {
        for (var j = 0; j < curr_edges[i].length; j++) {
            let edge_id = curr_edges[i][j];
            if (edgeHash.has(edge_id)) {
                edgeHash.get(edge_id).push(i);
            } else {
                edgeHash.set(edge_id, [i]);
            }
        
        }
    }

    // switch statement for each level
    let curr_level = document.getElementById("levelSelect").value;
    let correct = false;

    switch(curr_level) {
        case "ring":
            if (ringCheck(curr_edges, nodes)) {
                correct = true;
                console.log("Correct answer!")
            } else {
                console.log("Incorrect answer.")
            }
            break;
        case "star":
            if (starCheck(curr_edges, nodes)) {
                correct = true;
                console.log("Correct answer!")
            } else {
                console.log("Incorrect answer.")
            }
            break;
        case "bus":
            if (busCheck(curr_edges, nodes, edgeHash)) {
                correct = true;
                console.log("Correct answer!")
            } else {
                console.log("Incorrect answer.")
            }
            break;
        case "fully_connected":
          if (fullyConnectedCheck(curr_edges, nodes)) {
            correct = true;
            console.log("Correct answer!")
        } else {
            console.log("Incorrect answer.")
        }
        break;
        case "partial_connected":
            if (partialCheck(curr_edges, nodes)) {
              correct = true;
              console.log("Correct answer!")
            } else {
                console.log("Incorrect answer.")
            }
            break;
        default:
            console.error("Invalid level selected.");
            break;
    }

    if (correct) {
        let correct= document.getElementById("correct");
        correct.innerHTML = "Correct!";
    } else {
        let correct= document.getElementById("correct");
        correct.innerHTML = "Incorrect. Try Again.";
    
    }
}


function ringCheck(edges, nodes) {
    // check if the edges are correct
    // if each node has 2 edges, then it is a ring
    for (var i = 0; i < edges.length; i++) {
        if (edges[i].length != 2) {
            return false;
        }
    }
    return true;
}

function starCheck(edges, nodes) {
    // check if the edges are correct
    // if one node has n-1 edges, and the rest have 1 edge, then it is a star
    let n = nodes.length;
    let center = -1;
    for (var i = 0; i < edges.length; i++) {
        if (edges[i].length == n-1) {
            if (center != -1) {
                return false;
            }
            center = i;
        } else if (edges[i].length != 1) {
            return false;
        }
        if (center >= 0) {
          if (!nodes[center].startsWith("r")) {
              return false;
        }
      }
    }
    return true;
}

function busCheck(edges, nodes, edgeHash) {
    // check if the edges are correct
    // if each pc node has 1 edge, each terminator has 1 edge, and each router has 3 edges, then it is a bus
    for (var i = 0; i < edges.length; i++) {
        if (nodes[i].startsWith("t")) {
            
        }

        if (nodes[i].startsWith("pc") || nodes[i].startsWith("t")) {
            if (edges[i].length != 1) {
                return false;
            }
        } else if (nodes[i].startsWith("r")) {
            if (edges[i].length != 3) {
                return false;
            }
        }
    }
    return true;
}

function fullyConnectedCheck(edges, nodes) {
   // check if every node has n-1 edges
    let n = nodes.length;
    for (var i = 0; i < edges.length; i++) {
        if (edges[i].length != n-1) {
            return false;
        }
    }
    return true;
}

function partialCheck(edges, nodes) {
    // check if the edges are correct
    // if each node has at least 1 edge, then it is a partially connected graph
    for (var i = 0; i < edges.length; i++) {
        if (edges[i].length < 1) {
            return false;
        }
    }
    return true;
}