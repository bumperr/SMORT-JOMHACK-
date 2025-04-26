import { useDocument, useFirestore } from "vuefire";
import { doc } from "firebase/firestore";

export default defineEventHandler((event) => {
  const location_id = getRouterParam(event, "location_id");

  const db = useFirestore();

  const location = useDocument(doc(db, "trash_bins", location_id!));

  return location.data.value;
});
