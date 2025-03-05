// import * as PIXI from "https://pixijs.download/release/pixi.js";

// Get the container element
const container = document.getElementById('pixi-container');
const app = new PIXI.Application();
await app.init({ 
  width: container.clientWidth, 
  height: container.clientHeight,
  background: '#FFF4D5' 
});

// Append the canvas to the container
container.appendChild(app.canvas);
const SPRITE_PX = 256;
const NUM_SPRITES = 9;

function getSpriteData(sprite_idx) {
  return {
    frame: { x: sprite_idx * SPRITE_PX, y: 0, w: SPRITE_PX, h: SPRITE_PX },
    sourceSize: { w: SPRITE_PX, h: SPRITE_PX },
    spriteSourceSize: { x: 0, y: 0, w: SPRITE_PX, h: SPRITE_PX }
  }
}

const spritesheetData = {
  frames: {
    base_face: getSpriteData(0)
  },
  meta: {
    image: 'static/img/big-news-anchor-sprites.png',
    format: 'RGBA8888',
    size: { w: SPRITE_PX * NUM_SPRITES, h: SPRITE_PX },
    scale: 1
  },
  animations: {} // we'll add these later
}

// add each non-base sprite
for (let i = 1; i < NUM_SPRITES; i++) {
  spritesheetData.frames[`face${i}`] = getSpriteData(i);
}

// generate animation sequences
const faces = Object.keys(spritesheetData.frames).slice(1)
faces.forEach((face_key, i) => {
  spritesheetData.animations[`animation_${i}`] = ['base_face', face_key]

  // add a longer random animation
  const sequence_len = 1 + Math.floor(Math.random() * 3);
  let sequence = ['base_face', face_key]
  for (let j = 0; j < sequence_len; j++) {
    sequence.push(faces[Math.floor(Math.random() * faces.length)])
  }
  spritesheetData.animations[`animation_${i}_multi`] = sequence
});


try {
  const texture = await PIXI.Assets.load(spritesheetData.meta.image);
  const spritesheet = new PIXI.Spritesheet(texture, spritesheetData);
  await spritesheet.parse();
  const anim = new PIXI.AnimatedSprite(spritesheet.animations.animation_2);

  anim.animationSpeed = 0.09;
  anim.loop = false;

  anim.onComplete = () => {
    // Play a random sequence of animations
    const animation_keys = Object.keys(spritesheet.animations)
    const key = animation_keys[Math.floor(Math.random() * animation_keys.length)]
    const speed = Math.random() / 10 + 0.07
    anim.textures = spritesheet.animations[key];
    anim.animationSpeed = speed
    anim.play()
  };

  anim.play();
  app.stage.addChild(anim);
} catch (error) {
  console.error("Error loading spritesheet:", error);
}

const liveColor = 0xFBC62C;
const startX = app.screen.width - 95;
const startY = 25;
const circle = new PIXI.Graphics().circle(startX, startY, 6).fill({ color: liveColor });
app.stage.addChild(circle)

// wait for the font to be loaded by the browser
const font = new FontFaceObserver('Silkscreen');
await font.load();

const text1 = new PIXI.Text({ text: 'LIVE',  style: { fontFamily: 'Silkscreen', fontSize: 25, fill: liveColor, fontStyle: "bold" }});
text1.y = startY - text1.height/2 - 3;
text1.x = startX + 10
app.stage.addChild(text1);
