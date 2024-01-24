class GameScene extends Phaser.Scene {
  constructor() {
      super({ key: 'GameScene' });
  }

  preload() {
      // Load game-related assets
      this.load.image('gameBackground', 'assets/images/gameover-bg.jpg');
  }

  create() {
      // Add game elements and logic here
      this.add.image(400, 300, 'gameBackground').setDisplaySize(800, 600);
  }
}