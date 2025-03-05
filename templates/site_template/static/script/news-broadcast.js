// import * as PIXI from "https://pixijs.download/release/pixi.js";

// Get the container element
const main_container = document.getElementById('pixi-container');

const app = new PIXI.Application();

await app.init({
  width: main_container.clientWidth,
  height: main_container.clientHeight,
  background: '#FFF4D5',
});

main_container.appendChild(app.canvas);

// // background
// const office_texture = await PIXI.Assets.load('static/img/office.jpg')
// const office_sprite = new PIXI.Sprite(office_texture)
// office_sprite.filters = [new PIXI.filters.PixelateFilter()]
// app.stage.addChild(office_sprite)


// Load sprite visuals
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

// LIVE indicator
const live_container = new PIXI.Container()
const liveColor = 0xFBC62C;
const startX = app.screen.width - 95;
const startY = 22;
const circle = new PIXI.Graphics().circle(startX, startY, 6).fill({ color: liveColor });
app.stage.addChild(circle)

// wait for the font to be loaded by the browser
const font = new FontFaceObserver('Silkscreen');
await font.load();

const text1 = new PIXI.Text({ text: 'LIVE', style: { fontFamily: 'Silkscreen', fontSize: 25, fill: liveColor, fontStyle: "bold" } });
text1.y = startY - text1.height / 2 - 3;
text1.x = startX + 10
app.stage.addChild(text1);


// add a close button
const x_button = new PIXI.Container()
x_button.eventMode = 'static';
x_button.on('pointerdown', onXButtonClick);
x_button.cursor = 'pointer';

const x_text = new PIXI.Text({ text: 'X', style: { fontFamily: 'Silkscreen', fontSize: 25, fill: liveColor, fontStyle: "bold" } });
x_text.x = 10
x_text.y = 5

x_button.addChild(x_text);
app.stage.addChild(x_button);
var SOUND_GLO = null; // we'll set this later
function onXButtonClick() {
  if (SOUND_GLO) {
    SOUND_GLO.unload()
  }
  app.destroy({ removeView: true })
  if (main_container)
    main_container.remove();
}

// sound button
var SOUND_ON = false;

fetch('static/audio/output.json')
  .then(response => response.json())
  .then(async (data) => {
    console.log(data); // JSON data as a JavaScript object
    var sound = new Howl(data);
    SOUND_GLO = sound;
    await addSoundButton(sound);
  })
  .catch(error => console.error('Error loading JSON:', error));

async function addSoundButton(sound) {
  // visuals
  const sound_button = new PIXI.Container()
  sound_button.eventMode = 'static';
  sound_button.on('pointerdown', onSoundButtonClick);
  sound_button.cursor = 'pointer';

  const muted_texture = await PIXI.Assets.load('static/img/muted.png')
  const playing_texture = await PIXI.Assets.load('static/img/playing.png')
  const sound_sprite = new PIXI.Sprite(muted_texture)

  const x = 45;
  const y = 15;
  sound_sprite.x = x;
  sound_sprite.y = y;

  sound_button.addChild(sound_sprite);
  app.stage.addChild(sound_button)

  // audio control
  const sprite_keys = Object.keys(sound._sprite);
  const base_volume = 0.5;
  Howler.volume(base_volume);

  sound.on('end', function(){
    const sound_id = sprite_keys[Math.floor(Math.random() * sprite_keys.length)];
    console.log(sound_id)
    sound.rate(Math.random()*3, sound_id); 
    sound.volume(base_volume + (Math.random() - 0.5) / 4)
    sound.play(sound_id);
  });

  function onSoundButtonClick() {
    console.log("button press")
    SOUND_ON = !SOUND_ON;

    if(SOUND_ON) {
      sound_sprite.texture = playing_texture;
      console.log(sound)
      const sound_id = sprite_keys[Math.floor(Math.random() * sprite_keys.length)];
      sound.play(sound_id);
    } else {
      sound_sprite.texture = muted_texture;
      if (sound.playing())
        sound.stop();
    }

  }
}