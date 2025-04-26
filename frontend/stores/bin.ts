import { defineStore } from "pinia";
import { useCollection, useFirestore } from "vuefire";
import { collection } from "firebase/firestore";
import { useLocationStore } from "@/stores/location";

export const useBinStore = defineStore("bin", () => {
  const locationStore = useLocationStore();

  const db = useFirestore();

  const binSource = computed(() => {
    if (locationStore.activeLocationId === null) {
      return null;
    }
    return collection(db, "trash_bins", locationStore.activeLocationId, "bins");
  });
  const bins = useCollection(binSource);
  return { bins };
});
