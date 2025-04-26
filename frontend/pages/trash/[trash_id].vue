<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
});

const route = useRoute();
const id = useId();
const binId = computed(() => {
  const segments = route.path.split("/").filter(Boolean);
  return segments[segments.length - 1];
});

const { data: binDetails } = await useFetch(() => `http://172.104.185.250/sensor/${binId.value}`);

const { data: binTrashLevel } = await useFetch(
  () => `http://172.104.185.250/sensor/${binId.value}/record`,
);

const { data: binAllTrashLevels } = await useFetch(
  () => `http://172.104.185.250/sensor/${binId.value}/records`,
);

const tableData = computed(() => {
  const data = [];

  binAllTrashLevels.value
    .slice(-4)
    .reverse()
    .forEach((level) => {
      data.push({
        id: level[0],
        timestamp: new Date(level[1]),
        trash_level: level[2],
        image: level[3],
      });
    });
  return data;
});

const invoices = [
  {
    invoice: "INV001",
    paymentStatus: "Paid",
    totalAmount: "$250.00",
    paymentMethod: "Credit Card",
  },
  {
    invoice: "INV002",
    paymentStatus: "Pending",
    totalAmount: "$150.00",
    paymentMethod: "PayPal",
  },
  {
    invoice: "INV003",
    paymentStatus: "Unpaid",
    totalAmount: "$350.00",
    paymentMethod: "Bank Transfer",
  },
  {
    invoice: "INV004",
    paymentStatus: "Paid",
    totalAmount: "$450.00",
    paymentMethod: "Credit Card",
  },
  {
    invoice: "INV005",
    paymentStatus: "Paid",
    totalAmount: "$550.00",
    paymentMethod: "PayPal",
  },
  {
    invoice: "INV006",
    paymentStatus: "Pending",
    totalAmount: "$200.00",
    paymentMethod: "Bank Transfer",
  },
  {
    invoice: "INV007",
    paymentStatus: "Unpaid",
    totalAmount: "$300.00",
    paymentMethod: "Credit Card",
  },
];
</script>

<template>
  <div class="grid auto-rows-min gap-4 md:grid-cols-3">
    <Card class="col-span-2 row-span-2 rounded-xl bg-muted/50">
      <CardHeader>
        <CardTitle>History</CardTitle>
        <CardDescription>Trash level history every 15 minutes.</CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableCaption>History of trash level in Trash #{{ binId }}</TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead> Timestamp </TableHead>
              <TableHead class="w-[10rem]">Trash Level</TableHead>
              <TableHead class="text-right"> Image </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-for="row in tableData" :key="row.id">
              <TableCell class="font-medium">
                {{ row.timestamp }}
              </TableCell>
              <TableCell>{{ row.trash_level }}</TableCell>
              <TableCell class="text-right">
                <NuxtImg
                  v-if="row.image"
                  :src="`data:iamge/jpeg;base64,${row.image}`"
                  alt="trash image"
                  class="aspect-video max-w-[100px] rounded-md"
                />
                <Skeleton v-else class="aspect-video max-w-[100px]" />
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>Information</CardTitle>
        <CardDescription>Hello judges!</CardDescription>
      </CardHeader>
      <CardContent>
        <form>
          <div class="grid items-center w-full gap-4">
            <div class="flex flex-col space-y-1.5">
              <Label for="name">Name</Label>
              <Input id="name" :placeholder="binDetails[3]" disabled />
            </div>
            <div class="flex flex-col space-y-1.5">
              <Label for="name">Trash Level</Label>
              <Input id="name" :placeholder="`${binTrashLevel[2]}%`" disabled />
            </div>
          </div>
        </form>
      </CardContent>
    </Card>

    <Map
      class="aspect-video rounded-xl bg-muted/50"
      :initial-center="[binDetails[2], binDetails[1]]"
    >
      <MapboxDefaultMarker
        :marker-id="`${binDetails[0]}-${id}`"
        :options="{}"
        :lnglat="[binDetails[2], binDetails[1]]"
      />
    </Map>
  </div>
</template>

<style scoped></style>
