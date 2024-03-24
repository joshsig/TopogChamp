var selectedObject = null;
var selectedObject_2 = null;

class GameScene extends Phaser.Scene {
    constructor() {
        super({ key: 'GameScene' });
    }
    preload() {
        // Load game-related assets
        this.load.image('gameBackground', 'assets/images/gameover-bg.jpg');
        this.load.image('pc', 'assets/images/pc.png');
        this.load.image('router', 'assets/images/router.png');
        this.load.image('wire', 'assets/images/wire.png');
    }

    create() {
        // Create initial game state
        const router_1 = new RouterObject(this, 450, 400, 'router1');
        const router_12 = new RouterObject(this, 450, 400,'router2');
        const router_123 = new RouterObject(this, 450, 400,'router3');
        const es1 = new EndSystemObject(this, 450, 400, 'pc1');
        const es2 = new EndSystemObject(this, 450, 400, 'pc2');

        const graphics = this.add.graphics();
        const curr_wire = new Phaser.Geom.Line();
        // list of wires

        // deselect if clicked outside of any object
        this.input.on('pointerdown', () => {

            if (selectedObject)
            {
                selectedObject.setTint('0xffffff');
                selectedObject = null;
            }

        });

        // draw a wire from the selected object to the mouse

        this.input.on('pointermove', (pointer) => {
            if (selectedObject) {
                // draw a wire from the selected object to the mouse
                console.log("drawing wire");
                graphics.clear();
                graphics.lineStyle(2, 0x00ff00);
                graphics.strokeLineShape(curr_wire.setTo(selectedObject.x, selectedObject.y, pointer.x, pointer.y));
            }
        });

        this.input.on('down', (pointer) => {
            if (selectedObject) {
                // already selected an object
                // check if the pointer is over an object

                // if it is, connect the wire to the object

            }
        });

        

    }

    update() {
        // Update game logic
    }

    drawWires(wires, graphics) {
        // take the list of wires and draw them on the screen
        graphics.clear();

    }

}

class WireObject {

    constructor(scene, x, y, name, conn1, conn2) {
        this.name = name;
        this.conn1 = conn1;
        this.conn2 = conn2;
    
    }
}

class RouterObject extends Phaser.GameObjects.GameObject {

    constructor(scene, x, y, name) {
        super(scene, x, y);
        // Create the router sprite
        this.name = name;
        scene.load.image('router', 'assets/images/router.png');
        const object = scene.add.sprite(x, y, 'router').setSize(150, 150).setInteractive({ pixelPerfect: true, draggable: true });
        
        // move the object
        object.on('drag', function (pointer, dragX, dragY) {
            x = dragX;
            y = dragY;
            this.x = x;
            this.y = y;
        });

        // select the object
        object.on('pointerdown', function (pointer, x,y, event) {
            // check if the pointer is over a object
            // if it is, select the object
            console.log(`${name} clicked`);
            
            // if there is a selected object, deselect it
            if (selectedObject) {
                selectedObject.setTint("0xffffff");
            }

            if (selectedObject === object) {
                selectedObject = null;
            } else if (selectedObject && selectedObject_2 === null) {
                selectedObject_2 = this;
                this.setTint("0x00ff00");
            } else {
                selectedObject = this;

                this.setTint("0x00ff00");
            }

            event.stopPropagation();

        });
    
    }

    getName() {
        return this.name;
    }

    getCoordinates() {
        return { x: this.x, y: this.y };
    }

}

class EndSystemObject extends Phaser.GameObjects.GameObject {
    constructor(scene, x, y, name) {
        super(scene, x, y)

        scene.load.image('pc', 'assets/images/pc.png');
        const object = scene.add.sprite(x, y, "pc").setSize(150, 150).setInteractive({ pixelPerfect: true, draggable: true });

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
            
            // if there is a selected object, deselect it
            if (selectedObject) {
                selectedObject.setTint("0xffffff");
            }

            if (selectedObject === object) {
                selectedObject = null;
            } else if (selectedObject && selectedObject_2 === null) {
                selectedObject_2 = this;
                this.setTint("0x00ff00");
            } else {
                selectedObject = this;

                this.setTint("0x00ff00");
            }

            event.stopPropagation();

        });

    }


    getName() {
        return this.name;
    }

    getCoordinates() {
        return { x: this.x, y: this.y };
    }

}
