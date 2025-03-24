const TEXT_BG_HEIGHT = 45;
const ANCHOR_RAT_Y = -15;

// Get the container element
const main_container = document.getElementById('pixi-container');

const app = new PIXI.Application();

await app.init({
  width: main_container.clientWidth,
  height: main_container.clientHeight,
  background: '#FFF4D5',
});

main_container.appendChild(app.canvas);

const graphics = new PIXI.Graphics();
app.stage.addChild(graphics)

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
    image: '/static/img/big-news-anchor-sprites.png',
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
  anim.y = ANCHOR_RAT_Y;
  anim.animationSpeed = 0.3;
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
const circle = graphics.circle(startX, startY, 6).fill({ color: liveColor });
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

fetch('/static/audio/output.json')
  .then(response => response.json())
  .then(async (data) => {
    data['html5'] = false;
    var sound = new Howl(data);  // note: this is probably causing a js console warning
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

  const muted_texture = await PIXI.Assets.load('/static/img/muted.png')
  const playing_texture = await PIXI.Assets.load('/static/img/playing.png')
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
    const playback_id = sound.play(sound_id);
    let rate = 0.9 + Math.random() / 2;
    if (Math.random() < 0.01) {
      rate = 0.4; // make it really slow sometimes... just cause
    }
    sound.rate(rate, playback_id); 
    sound.volume(base_volume + (Math.random() - 0.5) / 4, playback_id);
  });

  function onSoundButtonClick() {
    SOUND_ON = !SOUND_ON;

    if(SOUND_ON) {
      sound_sprite.texture = playing_texture;
      const sound_id = sprite_keys[Math.floor(Math.random() * sprite_keys.length)];
      sound.play(sound_id);
    } else {
      sound_sprite.texture = muted_texture;
      if (sound.playing())
        sound.stop();
    }

  }
}

// live transcript

const transcript = `Good evening, Ratopolis! I'm Whiskers Whiteclaw, and here's your 60-second rundown:

The Rat States have halted military aid to Cheeselandia, with leader Trumpet claiming they 'brought it on themselves.' Tensions rise as some worry about threats from neighboring Rodentia.

Meanwhile, billionaire Elon Whiskers addresses the firing of cheese inspectors, attributing it to individual agencies. Political scrutiny builds as President Cheddar calls for caution in downsizing.

Over at the palace, Whisker McCheese challenges the Rattus monarchy with a bold new vision. Reform promises spark debate between tradition and modernity.

Speaking of tradition, Ratopolis is pondering if rapid tech advances are causing it to 'lose its tail,' fueling a tug-of-war between heritage and innovation.

In lighter news, artisanal claw cursers are all the rage—part fashion, part function—giving local makers a boost.

Finally, the Ivy Claw League faces allegations of favoring high-status pedigrees over genuine potential, raising concerns about systemic inequality.

That's all for now! Stay sharp, Ratopolis, and keep those whiskers tuned for more updates.`;


function estimateReadingSeconds(text, wordsPerMinute = 180) {
  if (typeof text !== 'string' || text.trim() === '') {
      throw new Error("Input must be a non-empty string");
  }

  // Method 1: Word count
  const words = text.split(/\s+/);
  const wordCount = words.length;
  const wordCountEstimate = wordCount / wordsPerMinute;

  // Method 3: Flesch-Kincaid
  const sentences = countSentences(text);
  const syllables = words.reduce((sum, word) => sum + countSyllables(word), 0);

  let fleschKincaidGrade = 0;
  
  if (sentences > 0 && wordCount > 0) {
      fleschKincaidGrade = 0.39 * (wordCount / sentences) + 11.8 * (syllables / wordCount) - 15.59;
  }

  // Adjust word count estimate based on Flesch-Kincaid Grade Level
  const fkAdjustedEstimate = wordCountEstimate * (1 + Math.max(0, fleschKincaidGrade) / 100);

  return fkAdjustedEstimate * 60;
}

function countSentences(text) {
  return (text.match(/[.!?]+/g) || []).length || 1;
}

function countSyllables(word) {
  word = word.toLowerCase();
  if (word.length <= 3) return 1; // Simple heuristic for short words
  const syllableMatches = word.match(/[aeiouy]{1,2}/g);
  return syllableMatches ? syllableMatches.length : 1;
}

function chunkTextForSubtitles(text, maxChunkLength = 40) {
  const sentences = text.match(/[^.!?]+[.!?]/g) || [text]; // Split by sentence boundaries
  let chunks = [];
  let currentChunk = "";

  for (let sentence of sentences) {
      let words = sentence.trim().split(/\s+/);
      for (let word of words) {
          if ((currentChunk + " " + word).trim().length > maxChunkLength) {
              if (currentChunk) chunks.push(currentChunk.trim());
              currentChunk = word; // Start new chunk with the current word
          } else {
              currentChunk += " " + word;
          }
      }
      
      if (currentChunk.length <= maxChunkLength) {
          chunks.push(currentChunk.trim());
          currentChunk = "";
      }
  }
  
  if (currentChunk.trim()) {
      chunks.push(currentChunk.trim());
  }
  
  return chunks;
}

const subtitles = chunkTextForSubtitles(transcript);


const backdrop = graphics.rect(0, app.screen.height-TEXT_BG_HEIGHT, app.screen.width,TEXT_BG_HEIGHT)
backdrop.fill(0)

let sub = new PIXI.Text({ text: subtitles[0], style: 
  { fontFamily: 'Silkscreen', fontSize: 12, fill: liveColor, wordWrap: true, wordWrapWidth: app.screen.width-20} 
})

sub.y = app.screen.height - TEXT_BG_HEIGHT + 5;
sub.x = 10;

app.stage.addChild(sub);

let transcript_timer_s = 0;
let subtitle_idx = 0;
let read_time_s = estimateReadingSeconds(subtitles[subtitle_idx])

app.ticker.add((time) =>{
  transcript_timer_s += time.elapsedMS / 1000;
  if (transcript_timer_s > read_time_s) {
    transcript_timer_s = 0;
    subtitle_idx += 1;
    if (subtitle_idx == subtitles.length) {
      subtitle_idx = 0;
    }
    sub.text = subtitles[subtitle_idx];
    read_time_s = estimateReadingSeconds(subtitles[subtitle_idx]);
    read_time_s = Math.max(1, read_time_s);
  }
});