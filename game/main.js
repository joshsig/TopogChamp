// Phaser 3 game configuration
var config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    scene: [MainMenu, GameScene, OptionsScene],
};

var game = new Phaser.Game(config);

// Start the main menu scene
game.scene.start('MainMenu');
