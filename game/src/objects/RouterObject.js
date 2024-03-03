class RouterObject extends Phaser.GameObjects.GameObject {

    constructor(scene, x, y, name) {
        super(scene, x, y);
        // Create the router sprite
        this.name = name;
        scene.load.image('router', 'assets/images/router.png');
        const object = scene.add.sprite(x, y, 'router').setSize(150, 150).setInteractive({ pixelPerfect: true, draggable: true });
    
        object.on('drag', function (pointer, dragX, dragY) {
            x = dragX;
            y = dragY;
            this.x = x;
            this.y = y;
        });

        object.on('pointerdown', function (pointer, x,y, event) {
            // check if the pointer is over a object
            // if it is, select the object

            console.log(`${name} clicked`);
            return name;
        });
    
    }

    getName() {
        return this.name;
    }

    getCoordinates() {
        return { x: this.x, y: this.y };
    }

}
