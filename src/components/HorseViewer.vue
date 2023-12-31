<template>
  <q-page class="row justify-center items-center">
    <div v-if="horses.length === 0">
      <h3 class="title" style="color: #041e29">
        Unleash the Champions: <br />Explore and Compare Photo Finish Breeding
        Reports!
      </h3>
      <h5 style="color: #041e29">Please paste a report PDF link</h5>
    </div>
    <q-list v-if="horses.length !== 0">
      <q-item
        class="q-pa-none"
        v-for="horse in horses"
        :key="horse.title"
        @vue:mounted="renderAll()"
      >
      </q-item>
    </q-list>
    <canvas id="canvas" :width="width" :height="height"></canvas>
  </q-page>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { Horse } from './models';

export default defineComponent({
  setup() {
    const width = 1220;
    const height = 700;
    return { width, height };
  },
  props: {
    horses: {
      type: Array as () => Horse[],
      required: true,
    },
  },
  data() {
    return {
      canvas: null as HTMLCanvasElement | null,
      ctx: null as CanvasRenderingContext2D | null,
      images: [] as Horse[],
    };
  },
  methods: {
    renderAll: function () {
      // console.log('rendering all images.');
      if (this.canvas === null || this.ctx === null) {
        console.log('canvas or ctx is null.');
        return;
      }
      this.ctx.clearRect(0, 0, this.width, this.height);

      this.horses.forEach((breed) => {
        if (breed === undefined) {
          console.log('breed is undefined.');
          return;
        }

        this.render(breed);
      });
      this.horses.forEach((breed) => {
        if (this.canvas === null) {
          console.log('canvas is null.');
          return;
        }
        var canvas = document.getElementById('canvas') as HTMLCanvasElement;
        var ctx = canvas.getContext('2d');
        if (ctx === null) {
          console.log('ctx is null.');
          return;
        }
        ctx.drawImage(breed.canvas, 0, 0);
      });
    },
    render: function (img: Horse) {
      console.log('rendering image: ', img.id);
      if (img.canvas === null || img.ctx === null) {
        console.log('canvas or ctx is null.');
        return;
      }

      var scale = this.scale(img);
      var height = img.bitmap.height * scale;
      var width = img.bitmap.width * scale;

      // console.log('scale: ', scale, ' height: ', height, ' width: ', width);
      img.canvas.height = height;
      img.canvas.width = width;

      // console.log('drawing image: ', img.id);
      img.ctx.save();
      img.ctx.globalAlpha = 0.6;
      img.ctx.drawImage(
        img.bitmap,
        0,
        0,
        img.bitmap.width,
        img.bitmap.height,
        0,
        0,
        width,
        height
      );
      this.removeWhite(img);
      img.ctx.globalAlpha = img.opacity;
      img.ctx.globalCompositeOperation = 'source-atop';
      img.ctx.fillStyle = img.color; // Replace with desired color
      img.ctx.fillRect(0, 55, img.canvas.width, img.canvas.height - 55);
      img.ctx.restore();
    },
    removeWhite: function (img: Horse) {
      const imageData = img.ctx.getImageData(
        0,
        0,
        img.bitmap.width,
        img.bitmap.height
      );
      const pixels = imageData.data;
      var cnt = 0;
      // Convert white color to transparency
      for (let i = 0; i < pixels.length; i += 4) {
        const red = pixels[i];
        const green = pixels[i + 1];
        const blue = pixels[i + 2];

        // Check if the pixel is white
        if (red === 255 && green === 255 && blue === 255) {
          cnt += 1;
          // Set the alpha value to 0 for white pixels
          pixels[i + 3] = 0;
        }
      }
      // console.log('removed white pixels: ', cnt);
      // Put the modified pixel data back to the temporary canvas
      img.ctx.putImageData(imageData, 0, 0);
      return img;
    },
    scale: function (img: Horse) {
      var scale = 1;
      var scaleX = 1;
      var scaleY = 1;
      if (img.bitmap.width > window.innerWidth) {
        scaleX = window.innerWidth / img.bitmap.width;
      }

      if (img.bitmap.height > window.innerHeight) {
        scaleY = window.innerHeight / img.bitmap.height;
      }

      if (scaleX < scale) {
        scale = scaleX;
      }
      if (scaleY < scale) {
        scale = scaleY;
      }
      return scale;
    },
  },
  mounted() {
    this.canvas = document.getElementById('canvas') as HTMLCanvasElement;
    this.ctx = this.canvas.getContext('2d');
    if (this.ctx === null) {
      console.log('ctx is null.');
      return;
    }
    this.ctx.globalAlpha = 1;
    this.renderAll();
  },
  updated() {
    this.renderAll();
  },
});
</script>

<style scoped></style>
