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
  </q-drawer>
  <q-page class="row" style="background-color: whitesmoke">
    <horse-viewer :horses="horses" />
  </q-page>
</template>

<script lang="ts">
import HorseViewer from 'components/HorseViewer.vue';
import { defineComponent, ref } from 'vue';
import { Horse } from 'components/models';
const regex = /((\w+%\d+)+x(%\d+\w+%\d+)+)Breeding/;

export default defineComponent({
  name: 'IndexPage',
  components: { HorseViewer },
  data() {
    return {
      port: '8080',
      horses: [] as Horse[],
      newBreed: '',
      colors: ['red', 'blue', 'green', 'orange', 'purple', 'pink'],
      currId: 0,
      exists: false,
    };
  },
  setup() {
    const width = 1500;
    const height = 1000;
    const defaultOpacity = 0.5;
    return { open: ref(true), width, height, defaultOpacity };
  },
  methods: {
    download: function () {
      console.log('Downloading graph.');
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
      var previous = this.horses;

      previous.forEach((breed) => {
        breed.ctx.clearRect(0, 0, this.width, this.height);
        if (breed.id === horse.id) {
          breed.opacity = 1;
        } else {
          breed.opacity = 0.2;
        }
      });
      this.horses = [];
      previous.forEach((breed) => {
        this.addHorse(
          breed.id,
          breed.bitmap,
          breed.title,
          breed.url,
          breed.opacity
        );
      });
      // this.addHorse(
      //   horse.id,
      //   horse.bitmap,
      //   horse.title,
      //   horse.url,
      //   horse.opacity
      // );
    },
    addHorse: function (
      id: number,
      bitmap: ImageBitmap,
      title: string,
      url: string,
      opacity?: number
    ) {
      console.log('Adding image with id: ', id, '.');
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
        color: this.colors[id],
        title: title,
      });
      this.newBreed = '';
    },
    removeHorse: function (id: number) {
      console.log('Removing image with id: ', id, '.');
      this.horses = this.horses.filter((horse) => horse.id !== id);
    },
    process: function (url: string) {
      if (url === '') {
        console.log('url is empty.');
        return;
      }
      url = url.trim();
      if (this.horses.length === 6) {
        this.newBreed = '';
        this.$q.notify({
          message: 'Maximum number of breeds reached.',
          color: 'red',
          icon: 'report_problem',
        });
        return;
      }
      fetch(`https://${location.hostname}:${this.port}/fetch`, {
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
  },
  mounted() {
    if (process.env.PORT === undefined) {
      this.port = '8080';
      return;
    } else {
      this.port = process.env.PORT;
    }
  },
});
</script>
