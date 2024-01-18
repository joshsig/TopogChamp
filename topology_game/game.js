var config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    physics: {
        default: 'arcade',
        arcade: {
            debug: false,
        },
    },
    scene: {
        preload: preload,
        create: create,
        update: update,
    },
};

var game = new Phaser.Game(config);

var nodes;
var connections;
var selectedNode = null;
var drawingWire = false;
var wire;

function preload() {
    this.load.image('node', "/assets/router.jpg");
    this.load.image('wire', 'path/to/wire-image.png');
}

function create() {
    nodes = this.physics.add.group();
    connections = this.add.group();

    // Create nodes
    createNode(100, 100, 1);
    createNode(500, 100, 2);
    createNode(300, 300, 3);

    // Set up input events
    this.input.on('pointerdown', handlePointerDown);
    this.input.on('pointerup', handlePointerUp);

    // Add button to draw wire
    var drawWireButton = this.add.text(700, 16, 'Draw Wire', { fontSize: '16px', fill: '#fff' });
    drawWireButton.setInteractive();
    drawWireButton.on('pointerdown', startDrawingWire);

    // Initialize wire sprite
    wire = this.add.sprite(0, 0, 'wire').setOrigin(0.5, 0.5).setVisible(false);
}

function update() {
    // Update wire position based on pointer
    if (drawingWire) {
        wire.setPosition(game.input.x, game.input.y);
    }
}

function createNode(x, y, id) {
    var node = nodes.create(x, y, 'node');
    node.setInteractive();
    node.setData('id', id);
}

function connectNodes(id1, id2) {
    var node1 = getNodeById(id1);
    var node2 = getNodeById(id2);

    if (node1 && node2) {
        var line = new Phaser.Geom.Line(node1.x, node1.y, node2.x, node2.y);
        var connection = connections.add(
            game.add.line(0, 0, line.x1, line.y1, line.x2, line.y2, 0x0000ff)
        );

        connection.setData('source', id1);
        connection.setData('target', id2);
    }
}

function getNodeById(id) {
    return nodes.getChildren().find((node) => node.getData('id') === id);
}

function handlePointerDown(pointer) {
    var node = nodes.getFirstAlive();

    if (node) {
        if (drawingWire) {
            // If drawing wire, connect the selectedNode to the clicked node
            connectNodes(selectedNode.getData('id'), node.getData('id'));
            selectedNode.clearTint();
            selectedNode = null;
            drawingWire = false;
            wire.setVisible(false);
        } else {
            // If not drawing wire, highlight the clicked node
            node.setTint(0xff0000);
            selectedNode = node;
        }
    }
}

function handlePointerUp() {
    if (drawingWire) {
        // If drawing wire, stop drawing and hide the wire sprite
        drawingWire = false;
        wire.setVisible(false);
    }
}

function startDrawingWire() {
    if (selectedNode) {
        // If a node is selected, start drawing wire
        drawingWire = true;
        wire.setPosition(selectedNode.x, selectedNode.y).setVisible(true);
    }
}
