import {defineStore} from "pinia";

export const useLocationStore = defineStore("location", () => {
  const activeLocationId = ref<number | null>(null);

  function setActiveLocationId(id: number) {
    activeLocationId.value = id;
  }

  return {activeLocationId, setActiveLocationId};
});
