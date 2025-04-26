<script setup lang="ts">
import { ChevronsUpDown, Plus } from "lucide-vue-next";
import { useLocationStore } from "@/stores/location";
import lodash from "lodash";

type Location = [number, string, string, number, number];

const activeLocationIndex = ref<number | null>(null);

const { data: locations, status } = await useFetch<Location[]>("http://172.104.185.250/region");

const emblems = ["/perak_tengah.png", "/ipoh.svg", "/batu_gajah.png"];

const locationStore = useLocationStore();

watch(
  status,
  () => {
    if (status.value === "success" && activeLocationIndex.value === null) {
      activeLocationIndex.value = 0;
    }
  },
  { immediate: true },
);

watch(activeLocationIndex, (index) => {
  if (index !== null) {
    locationStore.setActiveLocationId(locations.value![index!][0]);
  }
});

function setActiveLocation(index: number) {
  activeLocationIndex.value = index;
}
</script>

<template>
  <Skeleton v-if="status !== 'success'" class="rounded-lg w-full h-[3rem]" />
  <SidebarMenu v-else>
    <SidebarMenuItem>
      <DropdownMenu>
        <DropdownMenuTrigger as-child>
          <SidebarMenuButton
            size="lg"
            class="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
          >
            <div
              class="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground"
            >
              <NuxtImg
                :src="emblems[activeLocationIndex]"
                alt="district emblem"
                class="size-6"
                :key="activeLocationIndex"
              />
            </div>
            <div class="grid flex-1 text-left text-sm leading-tight">
              <span class="truncate font-semibold">{{
                lodash.startCase(locations[activeLocationIndex][1])
              }}</span>
              <span class="truncate text-xs">{{
                lodash.startCase(locations[activeLocationIndex][2])
              }}</span>
            </div>
            <ChevronsUpDown class="ml-auto" />
          </SidebarMenuButton>
        </DropdownMenuTrigger>
        <DropdownMenuContent
          class="w-[--radix-dropdown-menu-trigger-width] min-w-56 rounded-lg"
          align="start"
          side="bottom"
          :side-offset="4"
        >
          <DropdownMenuLabel class="text-xs text-muted-foreground">Location</DropdownMenuLabel>
          <DropdownMenuItem
            v-for="(location, index) in locations"
            :key="location.id"
            class="gap-2 p-2"
            @click="setActiveLocation(index)"
          >
            <div class="flex size-6 items-center justify-center rounded-sm border">
              <NuxtImg
                :src="emblems[index]"
                alt="district emblem"
                class="size-6"
                :key="location[0]"
              />
            </div>
            {{ lodash.startCase(location[1]) }}
            <DropdownMenuShortcut>⌘{{ index + 1 }}</DropdownMenuShortcut>
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem class="gap-2 p-2" disabled>
            <div class="flex size-6 items-center justify-center rounded-md border bg-background">
              <Plus class="size-4" />
            </div>
            <div class="font-medium text-muted-foreground">Add location</div>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </SidebarMenuItem>
  </SidebarMenu>
</template>
