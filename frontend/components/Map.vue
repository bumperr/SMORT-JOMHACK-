<script setup lang="ts">
import type {LngLatLike} from "mapbox-gl";
import type {HTMLAttributes} from "vue";

const props = withDefaults(defineProps<{
  class?: HTMLAttributes["class"];
  initialCenter?: LngLatLike;
  showControls?: boolean;
}>(), { showControls: false });

const id = useId();

const mapRef = useMapboxRef(id);
const colorMode = useColorMode();
const color = computed(() => colorMode.value);

const mapStyle = computed(() => {
  if (color.value === "light") {
    return "navigation-day-v1";
  } else {
    return "navigation-night-v1";
  }
});
const center: Ref<[number, number]> = ref(props.initialCenter ? props.initialCenter : [100.969551, 4.382069]);

watch(color, () => {
  const currCenter = mapRef.value?.getCenter();
  if (currCenter) {
    center.value[0] = currCenter.lng;
    center.value[1] = currCenter.lat;
  }
});
</script>

<template>
  <MapboxMap
    :map-id="id"
    :class="class"
    :options="{
      style: `mapbox://styles/mapbox/${mapStyle}`,
      center: center,
      zoom: 16,
    }"
  >
    <slot />
    <MapboxGeolocateControl v-if="showControls" position="top-left"/>
    <MapboxFullscreenControl v-if="showControls"/>
  </MapboxMap>
</template>

<style scoped>

</style>
