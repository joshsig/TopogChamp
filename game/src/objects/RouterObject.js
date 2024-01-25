class RouterObject extends Phaser.GameObjects.Container {
    constructor(scene, x, y) {
        super(scene, x, y);

        // Load the router image
        scene.load.image('router1', '/assets/images/router1.png');

        // Create the router sprite
        const router = scene.add.sprite(350, 400, 'router').setDisplaySize(150, 150).setInteractive({ pixelPerfect: true, draggable: true });

        // Enable input for the router object;
        router.on('drag', function (pointer, dragX, dragY) {
            this.x = dragX;
            this.y = dragY;
        });

        // Add event listeners for mouse interactions
        this.on('pointerdown', this.onPointerDown, this);
        this.on('pointerup', this.onPointerUp, this);
        this.on('pointermove', this.onPointerMove, this);

        // Initialize properties for mouse interactions
        this.isDragging = false;
        this.isSelected = false;
        this.startX = x;
        this.startY = y;
    }

    onPointerDown(pointer) {
        // Set the dragging flag to true
        this.isDragging = true;
        this.isSelected = true;

        if (this.isSelected) {
            this.scene.children.bringToTop(this);
            this.setTint(0x00ff00);
        }

        // Store the initial position of the router object
        this.startX = this.x;
        this.startY = this.y;

        // Bring the router object to the top of the display list
        this.scene.children.bringToTop(this);
    }

    onPointerUp(pointer) {
        // Set the dragging flag to false
        this.isDragging = false;
    }

    onPointerMove(pointer) {
        // Check if the router object is being dragged
        if (this.isDragging) {
            // Calculate the new position based on the pointer movement
            const deltaX = pointer.x - pointer.prevPosition.x;
            const deltaY = pointer.y - pointer.prevPosition.y;
            this.x += deltaX;
            this.y += deltaY;
        }
    }
}