var selectedObject = null;
var selectedObject_2 = null;

class GameScene extends Phaser.Scene {
    constructor() {
        super({ key: 'GameScene' });
    }
    preload() {
        // Load game-related assets
        this.load.image('pc', 'assets/images/pc.png');
        this.load.image('router', 'assets/images/router.png');
        this.load.image('wire', 'assets/images/wire.png');
    }

    create() {
        // add background
        this.add.image(400, 300, 'menuBackground').setDisplaySize(800, 600);
        // level select
        this.input.keyboard.on('keydown-M', () => {
            this.scene.start('LevelSelect');
        });

        
        // set up level 1


        let wires = [];

        // deselect if clicked outside of any object
        this.input.on('pointerdown', () => {

            this.drawWires(wires, graphics);

            if (selectedObject)
            {
                selectedObject.setTint('0xffffff');
                selectedObject = null;
            }
            if (selectedObject_2) {
                selectedObject_2.setTint('0xffffff');
                selectedObject_2 = null;
            }

        });

        // draw a wire from the selected object to the mouse

        this.input.on('pointermove', (pointer) => {
            
            if (selectedObject && selectedObject_2) {
                // draw a wire from the selected object to the mouse
                console.log("drawing wire");
                graphics.clear();
                graphics.lineStyle(2, 0x00ff00);
                graphics.strokeLineShape(curr_wire.setTo(selectedObject.x, selectedObject.y, selectedObject_2.x, selectedObject_2.y));
                wires.push(new WireObject(this, selectedObject, selectedObject_2));
                this.drawWires(wires, graphics);

                // deselect the objects
                selectedObject.setTint('0xffffff');
                selectedObject_2.setTint('0xffffff');
                selectedObject = null;
                selectedObject_2 = null;
            }
        });
        

    }

    update() {
        // Update game logic
    }

    levelSelect() {

    }

    drawWires(wires, graphics) {
        if (wires.length > 0) {
            graphics.clear();
            for (let i = 0; i < wires.length; i++) {
                graphics.lineStyle(2, 0x00ff00);
                graphics.strokeLineShape(new Phaser.Geom.Line(wires[i].conn1.x, wires[i].conn1.y, wires[i].conn2.x, wires[i].conn2.y));
            }
        }

    }

}

class WireObject {

    constructor(name, conn1, conn2) {
        this.name = "id" + Math.random().toString(16).slice(2);
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
                console.log(`${name} clicked`);
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
            
            // if there is a selected object, deselect it
            if (selectedObject) {
                selectedObject.setTint("0xffffff");
            }

            if (selectedObject === object) {
                selectedObject = null;
            } else if (selectedObject && selectedObject_2 === null) {
                // there is already a selected object, select this object as the second object
                selectedObject_2 = this;
                this.setTint("0x0000ff");
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
		