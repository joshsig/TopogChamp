class GameScene extends Phaser.Scene {
    constructor() {
        super({ key: 'GameScene' });
    }

    preload() {
        // Load game-related assets
        this.load.image('gameBackground', 'assets/images/gameover-bg.jpg');
        this.load.image('router', 'assets/images/router1.png');
    }

    create() {

        const router_1 = new RouterObject(this, 450, 400);
        const router_12 = new RouterObject(this, 450, 400);
        const router_123 = new RouterObject(this, 450, 400);
        const router_124 = new RouterObject(this, 450, 400);
        
        // Rest of the code...
    }
}
