import { useCollection, useFirestore } from "vuefire";
import { collection } from "firebase/firestore";

export default defineEventHandler((event) => {
  const location_id = getRouterParam(event, "location_id");

  const db = useFirestore();

  const location = useCollection(collection(db, "trash_bins", location_id!, "bins"));

  return location.data;
});
