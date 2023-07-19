<template>
  <q-drawer v-model="open" behavior="desktop" persistent bordered style="">
    <q-list v-for="horse in horses" :key="horse.id">
      <q-item class="q-pb-md">
        <q-item-section>
          <div class="text-h6">{{ horse.title }}</div>
          <q-btn-group style="height: 20px" spread>
            <q-btn
              :color="horse.color"
              icon="fa-solid fa-eye"
              label="Show"
              outlined
              @click="show(horse)"
            ></q-btn>
            <q-btn
              :color="horse.color"
              icon="delete"
              outlined
              label="Remove"
              @click="removeHorse(horse.id)"
            ></q-btn>
          </q-btn-group>
        </q-item-section>
      </q-item>
    </q-list>
    <q-item>
      <q-item-section>
        <q-input
          :disable="horses.length === 6"
          v-model="newBreed"
          class="q-pt-sm"
          outlined
          label="Add PDF"
          label-color="accent"
          debounce="300"
          @update:model-value="process(newBreed)"
        ></q-input>
        <q-btn
          class="q-mt-sm"
          text-color="accent"
          color="secondary"
          outlined
          icon="download"
          label="Download Graph"
          label-color="accent"
          @click="download"
          :disable="horses.length === 0"
        >
        </q-btn>
      </q-item-section>
    </q-item>
    <q-item>
      <div class="q-pr-md text-body2">Opacity</div>
      <q-slider
        color="accent"
        v-model="lowOpacity"
        @change="updateOpacity(lowOpacity)"
      ></q-slider>
    </q-item>
  </q-drawer>
  <q-page class="row" style="background-color: whitesmoke">
    <horse-viewer :horses="horses" />
  </q-page>
</template>

<script lang="ts">
import HorseViewer from 'components/HorseViewer.vue';
import { defineComponent, ref } from 'vue';
import { Horse } from 'components/models';
import { exportFile } from 'quasar';

const regex = /((\w+%\d+)+x(%\d+(\w+%\d+)+))Breeding/;
const APIfetch = `https://${location.hostname}/fetch`;
// const APIfetch = `http://${location.hostname}:3000/fetch`;
export default defineComponent({
  name: 'IndexPage',
  components: { HorseViewer },
  data() {
    return {
      horses: [] as Horse[],
      newBreed: '',
      colors: [
        { color: 'red', used: false },
        { color: 'blue', used: false },
        { color: 'green', used: false },
        { color: 'orange', used: false },
        { color: 'purple', used: false },
      ],
      currId: 0,
      exists: false,
      currHighlighted: null as Horse | null,
      prevOpacity: this.lowOpacity,
    };
  },
  setup() {
    const width = 1220;
    const height = 700;
    const defaultOpacity = 0.5;
    const lowOpacity = 0.2;
    const highOpacity = 1;
    return {
      open: ref(true),
      width,
      height,
      defaultOpacity,
      lowOpacity,
      highOpacity,
    };
  },
  methods: {
    download: function () {
      console.log('Downloading graph.');
      const canvas = document.getElementById('canvas') as HTMLCanvasElement;
      var exportCanvas = document.createElement('canvas');
      var exportContext = exportCanvas.getContext('2d');
      if (exportContext === null || canvas === null) {
        this.$q.notify({
          message: 'Download failed.',
          color: 'red',
          icon: 'report_problem',
        });
        return;
      }
      exportCanvas.width = canvas.width;
      exportCanvas.height = canvas.height;
      exportContext.fillStyle = 'white';
      exportContext.fillRect(0, 0, canvas.width, canvas.height);
      exportContext.drawImage(canvas, 0, 0);
      exportCanvas.toBlob((blob) => {
        if (blob === null) {
          this.$q.notify({
            message: 'Download failed.',
            color: 'red',
            icon: 'report_problem',
          });
          return;
        }
        const status = exportFile('Graph.png', blob, {
          mimeType: 'image/png',
        });

        if (status === true) {
          // browser allowed it
        } else {
          // browser denied it
          console.log('Error: ' + status);
        }
      });
    },
    show: function (horse: Horse) {
      console.log('showing horse: ', horse.id);
      this.horses.forEach((breed) => {
        if (breed.id === horse.id) {
          this.highlight(breed);
          return;
        } else {
          breed.opacity = this.defaultOpacity;
        }
      });
    },
    highlight: function (horse: Horse) {
      console.log('highlighting horse: ', horse.id);
      this.currHighlighted = horse;
      var previous = this.horses;

      previous.forEach((breed) => {
        breed.ctx.clearRect(0, 0, this.width, this.height);
        if (breed.id === horse.id) {
          breed.opacity = this.highOpacity;
        } else {
          breed.opacity = this.lowOpacity;
        }
      });
      this.horses = [];
      this.addHorse(
        horse.id,
        horse.bitmap,
        horse.title,
        horse.url,
        horse.color,
        horse.opacity
      );
      previous.forEach((breed) => {
        if (breed.id === horse.id) {
          return;
        }
        this.addHorse(
          breed.id,
          breed.bitmap,
          breed.title,
          breed.url,
          breed.color,
          breed.opacity
        );
      });
    },
    addHorse: function (
      id: number,
      bitmap: ImageBitmap,
      title: string,
      url: string,
      color?: string,
      opacity?: number
    ) {
      console.log('Adding image with id: ', id, '.');
      console.log('Color: ', color);
      if (opacity === undefined) {
        opacity = this.defaultOpacity;
      } else {
        console.log('Opacity: ', opacity);
      }
      this.horses.forEach((horse) => {
        if (title === horse.title) {
          console.log('Breed already exists.');
          this.$q.notify({
            message: 'Breed already exists.',
            color: 'red',
            icon: 'report_problem',
          });
          this.exists = true;
          return;
        }
      });
      if (this.exists) {
        this.exists = false;
        return;
      }

      var layer = document.createElement('canvas');
      layer.width = this.width; // same size as original
      layer.height = this.height;
      var ctx = layer.getContext('2d');
      if (ctx === null) {
        console.log('ctx is null.');
        return;
      }
      this.horses.push({
        id: id,
        canvas: layer,
        opacity: opacity,
        ctx: ctx,
        bitmap: bitmap,
        url: url,
        color: color ? color : this.unusedColor(),
        title: title,
      });
      this.newBreed = '';
    },
    removeHorse: function (id: number) {
      console.log('Removing image with id: ', id, '.');
      this.horses.forEach((horse) => {
        if (horse.id === id) {
          this.colors.forEach((color) => {
            if (color.color === horse.color) {
              color.used = false;
            }
          });
        }
      });
      this.horses = this.horses.filter((horse) => horse.id !== id);
    },
    process: function (url: string) {
      if (url === '') {
        console.log('url is empty.');
        return;
      }
      url = url.trim();
      if (this.horses.length === 5) {
        this.newBreed = '';
        this.$q.notify({
          message: 'Maximum number of graphs reached.',
          color: 'red',
          icon: 'report_problem',
        });
        return;
      }
      fetch(APIfetch, {
        method: 'POST',
        headers: {
          'Access-Control-Allow-Origin': '*', // Required for CORS support to work,
        },
        body: url,
      })
        .then((response) => {
          if (response.body === null) {
            console.log('Body is null.');
            return;
          }
          response.arrayBuffer().then((data) => {
            if (data.byteLength === 0) {
              console.log('Fetched Image is empty.');
              return;
            }
            console.log(
              'Fetched Image is not empty: ',
              data.byteLength,
              ' bytes. '
            );
            var names = url.match(regex);
            var title = 'Breed ' + this.currId.toString();

            if (names !== null) {
              title = names[1].replaceAll('%20', ' ').trim();
              const blob = new Blob([data], { type: 'image/png' });
              createImageBitmap(blob).then(
                (img) => {
                  this.addHorse(
                    this.currId,
                    img,
                    title,
                    URL.createObjectURL(blob)
                  );
                  this.currId++;
                },
                (error) => {
                  console.log('error: ', error);
                }
              );
            } else {
              this.$q.notify({
                message: 'Horse names not found.',
                color: 'negative',
                icon: 'report_problem',
              });
              console.log('No names found.');
            }
          });
          console.log('response', response.body);
        })
        .catch((error) => {
          console.log('error', error);
        });
    },
    unusedColor: function () {
      let curColor = 'gray';
      this.colors.forEach((color) => {
        if (curColor !== 'gray') {
          return;
        }
        if (color.used === false) {
          color.used = true;
          curColor = color.color;
        }
      });
      console.log('curColor: ', curColor);
      return curColor;
    },
    updateOpacity: function (value: number) {
      this.lowOpacity = value / 100;
      console.log('Updated opacity to: ', this.lowOpacity);
      if (this.currHighlighted !== null) {
        this.highlight(this.currHighlighted);
      }
    },
  },
});
</script>
