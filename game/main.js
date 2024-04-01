// Phaser 3 game configuration
var config = {
    type: Phaser.AUTO,
    width: 1200,
    height: 900,
    scene: [MainMenu, GameScene, SimulationScene, OptionsScene],
};

var game = new Phaser.Game(config);

// Start the main menu scene
game.scene.start('MainMenu');
