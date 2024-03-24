
class MainMenu extends Phaser.Scene {
    constructor() {
        super({ key: 'MainMenu' });
        
        const element = document.createElement('style');
        document.head.appendChild(element);
        const sheet = element.sheet;
        let styles = '@font-face { font-family: "sofia"; src: url("assets/fonts/Sofia-Regular.otf") format("opentype"); }';
        sheet.insertRule(styles, 0);
    }

    preload() {
        this.load.image('menuBackground', 'assets/images/menuBackground.png');
    }

    create() {
        this.add.image(400, 300, 'menuBackground').setDisplaySize(800, 600);
        WebFont.load({
            custom: {
                families: ['sofia'],
            },
            active: () => {
                const graphics = this.add.graphics();

                // Draw a rounded rectangle as a background behind the text
                graphics.fillStyle(0x006400, 0.7);
                graphics.fillRoundedRect(400 - 150, 200 - 40, 300, 180, 10);

                // Add buttons using the loaded font
                let playButton = this.add.text(400, 200, 'Play Game', {
                    fontFamily: 'sofia',
                    fontSize: '48px',
                    fill: '#fff'
                })
                    .setOrigin(0.5)
                    .setInteractive({ useHandCursor: true })
                    .on('pointerdown', function () {
                        this.scene.start('GameScene');
                    }, this)
                    .setPadding(30);

                let simulationButton = this.add.text(400, 250, 'Start Simulation', {
                    fontFamily: 'sofia',
                    fontSize: '48px',
                    fill: '#fff'
                })
                    .setOrigin(0.5)
                    .setInteractive({ useHandCursor: true })
                    .on('pointerdown', function () {
                        this.scene.start('SimulationScene');
                    }, this)
                    .setPadding(30);

                let optionsButton = this.add.text(400, 300, 'Options', {
                    fontFamily: 'sofia', 
                    fontSize: '48px',
                    fill: '#fff'
                })
                    .setOrigin(0.5)
                    .setInteractive({ useHandCursor: true })
                    .on('pointerdown', function () {
                        this.scene.start('OptionsScene');
                    }, this)
                    .setPadding(30);
            },
            inactive: () => {
                console.error('Failed to load custom font.');
            }
        });
    }
}

