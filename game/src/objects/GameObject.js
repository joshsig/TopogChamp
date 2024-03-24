images = {
    switch: '/assets/images/switch1.png',
    server: '/assets/images/server1.png',
    pc: '/assets/images/pc.png',
    cable: '/assets/images/cable.png',
    router: '/assets/images/router.png'
};

class GameObject extends Phaser.GameObjects.GameObject {

  constructor(scene, x, y, name, img) {
    super(scene, x, y);
    this.name = name
    this.scene = scene;


    const object = scene.add.sprite(x, y, img).setDisplaySize(150, 150).setInteractive({ pixelPerfect: true, draggable: true });

    object.on('drag', function (pointer, dragX, dragY) {
        x = dragX;
        y = dragY;
        this.x = x;
        this.y = y;
    });

    // Add event listeners for mouse interactions
    object.on('pointerdown', this.onPointerDown, this);
    object.on('pointerup', this.onPointerUp, this);


    this.isSelected = false; // Flag to check if the object is selected
    this.pointerWire = null; // Reference to the wire being drawn
    this.connections = [];
  }

  onPointerDown1(pointer) {
        if (!this.isSelected) {
            // When the object is not selected, select it and draw a wire to the pointer
            this.isSelected = true;
            this.pointerWire = this.drawWire(this.x, this.y, pointer.x, pointer.y);

        } else {
            // When the object is already selected, test if the pointer is on another object
            const selectedObject = this.scene.input.hitTestPointer(pointer);

            if (selectedObject && selectedObject.gameObject instanceof GameObject) {
                // If another object is selected, draw a wire from this object to the selected object
                const targetX = selectedObject.gameObject.x;
                const targetY = selectedObject.gameObject.y;
                this.connections.push(selectedObject.gameObject);
                selectedObject.gameObject.connections.push(this);

                // Draw wire and reset selection
                this.drawWire(this.x, this.y, targetX, targetY);
                this.isSelected = false;
                this.pointerWire = null;
            } else {
                // If no object is selected, destroy the wire and reset selection
                this.isSelected = false;
                this.pointerWire.destroy();
                this.pointerWire = null;
            }
        }
    }


    onPointerDown(pointer) {
        // Set the dragging flag to true

        
        // wait for another click
        // if that click is on another object, add to connections
        // if that click is on the same object, destroy the wire
        // if that click is on nothing, destroy the wire
        if (!this.isSelected) {
            // When the object is not selected, select it and draw a wire to the pointer
            this.isSelected = true;
            //this.pointerWire = this.drawWire(this.x, this.y, pointer.x, pointer.y);

        } else {
            // When the object is already selected, test if the pointer is on another object
            const selectedObject = this.scene.input.hitTestPointer(pointer);
            console.log(selectedObject.gameObject)

            if (selectedObject && selectedObject.gameObject instanceof GameObject) {
                // If another object is selected, draw a wire from this object to the selected object
                this.connections.push(selectedObject.gameObject);
                selectedObject.gameObject.connections.push(this);
                console.log("selectedObject: ", selectedObject.gameObject.name)
                print("connections: ", this.connections, selectedObject.gameObject.connections)
                this.isSelected = false;
            } else {
                // If no object is selected, destroy the wire and reset selection
                
            }
        }


    }

    drawWire(startX, startY, endX, endY) {
        const graphics = this.scene.add.graphics();
        graphics.lineStyle(3, 0x00ff00); // Green color, you can change it as needed
        graphics.beginPath();
        graphics.moveTo(startX, startY);
        graphics.lineTo(endX, endY);
        graphics.strokePath();

        return graphics;
    }

    updateWire(x, y) {
        this.connections.forEach((connectedObject) => {
            this.drawWire(x, y, connectedObject.x, connectedObject.y);
        })
    }

    onPointerUp(pointer) {
        // Set the dragging flag to false
        this.isDragging = false;
    }

}