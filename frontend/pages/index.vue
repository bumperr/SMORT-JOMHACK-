<script setup lang="ts">
import { useLocationStore } from "@/stores/location";
import { storeToRefs } from "pinia";

definePageMeta({
  middleware: ["auth"],
});

const locationStore = useLocationStore();
const { activeLocationId: activeLocation } = storeToRefs(locationStore);

const regionId = ref(1);
const id = useId();

const { data: bins, refresh: binRefresh } = await useFetch(
  () => `http://172.104.185.250/region/${regionId.value}/sensors`,
);

// const {
//   data: latestTrashLevelInRegion,
//   refresh: refreshLatestTrashLevelInRegion
// } = await useFetch(() => `http://172.104.185.250/analytics/level/${regionId.value}`);
//
// const {
//   data: averageTrashLevelsInAllRegion
// } = await useFetch(() => `http://172.104.185.250/analytics/average/all`);
//
// const {
//   data: averageTrashLevelsInRegion,
//   refresh: refreshAverageTrashLevelsInRegion
// } = await useFetch(() => `http://172.104.185.250/analytics/average/${regionId.value}`);

const pieChartData = [
  {
    id: 1,
    "Trash Level": 42,
    Predicted: 46,
  },
  {
    id: 2,
    "Trash Level": 34,
    Predicted: 65,
  },
  {
    id: 3,
    "Trash Level": 74,
    Predicted: 44,
  },
  {
    id: 4,
    "Trash Level": 66,
    Predicted: 31,
  },
  {
    id: 5,
    "Trash Level": 63,
    Predicted: 32,
  },
];

watch(
  activeLocation,
  async (id) => {
    if (id !== null) {
      regionId.value = id;
      await binRefresh();
      // await refreshLatestTrashLevelInRegion();
      // await refreshAverageTrashLevelsInRegion();
    }
  },
  { immediate: true },
);

const areaChartData = [
  {
    timestamp: "2025-02-14T07:00:00",
    "In Region": 46,
    "All Regions": 87,
  },
  {
    timestamp: "2025-02-14T14:00:00",
    "In Region": 32,
    "All Regions": 65,
  },
  {
    timestamp: "2025-02-15T07:00:00",
    "In Region": 57,
    "All Regions": 11,
  },
  {
    timestamp: "2025-02-15T14:00:00",
    "In Region": 74,
    "All Regions": 32,
  },
  {
    timestamp: "2025-02-16T07:00:00",
    "In Region": 69,
    "All Regions": 24,
  },
  {
    timestamp: "2025-02-16T14:00:00",
    "In Region": 8,
    "All Regions": 43,
  },
];
</script>

<template>
  <div class="grid auto-rows-min gap-4 md:grid-cols-3">
    <Card class="aspect-video rounded-xl bg-muted/50">
      <CardHeader>
        <CardTitle>Status of Trash Bins in the Area</CardTitle>
      </CardHeader>
      <CardContent>
        <DonutChart
          index="id"
          :category="'Trash Level'"
          :data="pieChartData"
          class="md:max-h-[250px]"
        />
      </CardContent>
    </Card>
    <Card class="aspect-[32/9] rounded-xl bg-muted/50 col-span-2">
      <CardHeader>
        <CardTitle
          >Average Trash Level <span class="text-muted-foreground">vs</span> All Areas
        </CardTitle>
      </CardHeader>
      <CardContent>
        <AreaChart
          index="timestamp"
          :data="areaChartData"
          :categories="['In Region', 'All Regions']"
          class="md:h-48 md:max-h-[250px] pb-4"
        />
      </CardContent>
    </Card>
  </div>
  <Map class="min-h-[100vh] flex-1 rounded-xl bg-muted/50 md:min-h-min" show-controls>
    <MapboxDefaultMarker
      v-for="bin in bins"
      :marker-id="`${bin[0]}-${id}`"
      :options="{}"
      :lnglat="[bin[2], bin[1]]"
    />
  </Map>
</template>
