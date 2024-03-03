class WireObject extends Phaser.GameObjects.Graphics {

    constructor(scene, x, y) {
        super(scene, x, y, 0, 0, x, y, 0xFFFFFF);
        scene.add.existing(this);
        this.setOrigin(0, 0).setLineWidth(5);
    }

    updateEnd(x, y) {
        this.setTo(this.x, this.y, x, y);
    }

    connectTo(targetObject) {
        // Implement logic to connect the wire to the target object
        // For example, you can store the connection information or handle it in your game logic
        // In this example, I'm simply printing the connection information to the console
        console.log(`Connected ${this.parent.getName()} to ${targetObject.getName()}`);
    }
}