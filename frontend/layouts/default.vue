<!-- eslint-disable vue/multi-word-component-names -->
<script setup lang="ts">
import {
  BadgeCheck,
  Bell,
  Bot,
  ChevronRight,
  ChevronsUpDown,
  Folder,
  Globe,
  LayoutDashboard,
  LogOut,
  MoreHorizontal,
  Sparkles,
  Trash2,
} from "lucide-vue-next";
import lodash from "lodash";

import { signOut } from "firebase/auth";
import { useToast } from "@/components/ui/toast/use-toast";

import { useLocationStore } from "@/stores/location";
import { storeToRefs } from "pinia";

const data = {
  projects: [
    {
      name: "Invent for the Planet Hackathon 2025",
      url: "#",
      icon: Globe,
    },
    {
      name: "Petrobots Hackathon 2025",
      url: "#",
      icon: Bot,
    },
  ],
};

const predictSensorId = ref(1);
const auth = useFirebaseAuth()!;
const user = useCurrentUser();
const router = useRouter();
const route = useRoute();
const { toast } = useToast();

const locationStore = useLocationStore();
const { activeLocationId: activeLocation } = storeToRefs(locationStore);

const regionId = ref(1);

let {
  data: bins,
  status: binStatus,
  refresh: binRefresh,
} = await useFetch(() => `http://172.104.185.250/region/${regionId.value}/sensors`);

const breadcrumbs = computed(() => {
  const segments = route.path.split("/").filter(Boolean);
  return segments.map((segment, index) => ({
    name: lodash.startCase(segment.replace(/-/g, " ")),
    path: "/" + segments.slice(0, index + 1).join("/"),
  }));
});

watch(
  activeLocation,
  async (id) => {
    if (id !== null) {
      regionId.value = id;
      await binRefresh();
    }
  },
  { immediate: true },
);

function handleSignOut() {
  signOut(auth).then(() => router.replace("/login"));
}

async function getPredictionValue() {
  const { data: predictionValue } = await useFetch(
    () => `http://172.104.185.250/predict/${predictSensorId.value}`,
  );
  toast({
    title: "Predicted Value",
    description: `The trash will be full in ${predictionValue.value.hours_until_full} hours. The trash level will be at ${predictionValue.value.predicted_level}%.`,
  });
}
</script>

<template>
  <SidebarProvider>
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <LocationPicker />
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Platform</SidebarGroupLabel>
          <SidebarMenu>
            <Collapsible as-child :default-open="true" class="group/collapsible">
              <SidebarMenuItem>
                <CollapsibleTrigger as-child>
                  <SidebarMenuButton tooltip="Dashboard">
                    <LayoutDashboard />
                    <span>Dashboard</span>
                    <ChevronRight
                      class="ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90"
                    />
                  </SidebarMenuButton>
                </CollapsibleTrigger>
                <CollapsibleContent>
                  <SidebarMenuSub>
                    <SidebarMenuSubItem>
                      <SidebarMenuSubButton as-child>
                        <NuxtLink disabled href="/">
                          <span>All</span>
                        </NuxtLink>
                      </SidebarMenuSubButton>
                    </SidebarMenuSubItem>
                  </SidebarMenuSub>
                </CollapsibleContent>
              </SidebarMenuItem>
            </Collapsible>
            <Collapsible
              v-if="binStatus === 'success'"
              as-child
              :default-open="false"
              class="group/collapsible"
            >
              <SidebarMenuItem>
                <CollapsibleTrigger as-child>
                  <SidebarMenuButton tooltip="Trash Status">
                    <Trash2 />
                    <span>Trash Status</span>
                    <ChevronRight
                      class="ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90"
                    />
                  </SidebarMenuButton>
                </CollapsibleTrigger>
                <CollapsibleContent>
                  <SidebarMenuSub>
                    <SidebarMenuSubItem v-for="bin in bins" :key="bin[0]">
                      <SidebarMenuSubButton as-child>
                        <NuxtLink :href="`/trash/${bin[0]}`">
                          <span>Trash {{ bin[3] }} #{{ bin[0] }}</span>
                        </NuxtLink>
                      </SidebarMenuSubButton>
                    </SidebarMenuSubItem>
                  </SidebarMenuSub>
                </CollapsibleContent>
              </SidebarMenuItem>
            </Collapsible>
          </SidebarMenu>
        </SidebarGroup>
        <SidebarGroup class="group-data-[collapsible=icon]:hidden">
          <SidebarGroupLabel>Projects</SidebarGroupLabel>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in data.projects" :key="item.name">
              <SidebarMenuButton as-child>
                <a :href="item.url">
                  <component :is="item.icon" />
                  <span>{{ item.name }}</span>
                </a>
              </SidebarMenuButton>
              <DropdownMenu>
                <DropdownMenuTrigger as-child>
                  <SidebarMenuAction show-on-hover>
                    <MoreHorizontal />
                    <span class="sr-only">More</span>
                  </SidebarMenuAction>
                </DropdownMenuTrigger>
                <DropdownMenuContent class="w-48 rounded-lg" side="bottom" align="end">
                  <DropdownMenuItem>
                    <Folder class="text-muted-foreground" />
                    <span>View Project</span>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>
                    <Trash2 class="text-muted-foreground" />
                    <span>Delete Project</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <DropdownMenu>
              <DropdownMenuTrigger as-child>
                <SidebarMenuButton
                  size="lg"
                  class="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
                >
                  <Avatar class="h-8 w-8 rounded-lg">
                    <AvatarImage :src="user.photoURL" alt="user profile photo" />
                    <AvatarFallback class="rounded-lg">69</AvatarFallback>
                  </Avatar>
                  <div class="grid flex-1 text-left text-sm leading-tight">
                    <span class="truncate font-semibold">{{ user.displayName }}</span>
                    <span class="truncate text-xs">{{ user.email }}</span>
                  </div>
                  <ChevronsUpDown class="ml-auto size-4" />
                </SidebarMenuButton>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                class="w-[--radix-dropdown-menu-trigger-width] min-w-56 rounded-lg"
                side="bottom"
                align="end"
                :side-offset="4"
              >
                <DropdownMenuLabel class="p-0 font-normal">
                  <div class="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
                    <Avatar class="h-8 w-8 rounded-lg">
                      <AvatarImage :src="user.photoURL" alt="user profile photo" />
                      <AvatarFallback class="rounded-lg">69</AvatarFallback>
                    </Avatar>
                    <div class="grid flex-1 text-left text-sm leading-tight">
                      <span class="truncate font-semibold">{{ user.displayName }}</span>
                      <span class="truncate text-xs">{{ user.email }}</span>
                    </div>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuGroup>
                  <DropdownMenuItem>
                    <Sparkles />
                    Deez Nuts
                  </DropdownMenuItem>
                </DropdownMenuGroup>
                <DropdownMenuSeparator />
                <DropdownMenuGroup>
                  <DropdownMenuItem>
                    <BadgeCheck />
                    Account
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Bell />
                    Notifications
                  </DropdownMenuItem>
                </DropdownMenuGroup>
                <DropdownMenuSeparator />
                <DropdownMenuItem @click="handleSignOut">
                  <LogOut />
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
    <SidebarInset>
      <header
        class="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12"
      >
        <div class="flex items-center gap-2 px-4 w-full">
          <SidebarTrigger class="-ml-1" />
          <Separator orientation="vertical" class="mr-2 h-4" />
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbLink href="/">Home</BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator v-if="breadcrumbs.length > 0" />

              <template v-for="(breadcrumb, index) in breadcrumbs" :key="breadcrumb.path">
                <BreadcrumbItem v-if="index !== breadcrumbs.length - 1" class="hidden md:block">
                  <BreadcrumbLink :href="breadcrumb.path">{{ breadcrumb.name }}</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator
                  v-if="index !== breadcrumbs.length - 1"
                  class="hidden md:block"
                />
                <BreadcrumbItem v-else>
                  <BreadcrumbPage>{{ breadcrumb.name }}</BreadcrumbPage>
                </BreadcrumbItem>
              </template>
            </BreadcrumbList>
          </Breadcrumb>

          <div class="ml-auto flex gap-4 justify-center align-center">
            <Popover>
              <PopoverTrigger as-child>
                <Button variant="outline"> Predict Trash Level </Button>
              </PopoverTrigger>
              <PopoverContent class="w-80">
                <div class="grid gap-4">
                  <div class="space-y-2">
                    <h4 class="font-medium leading-none">Predictor</h4>
                    <p class="text-sm text-muted-foreground">
                      Predict the trash level and when it will be full.
                    </p>
                  </div>
                  <div class="grid gap-2">
                    <div class="grid grid-cols-3 items-center gap-4">
                      <Label for="width">Sensor ID</Label>
                      <Input
                        id="sensor_id"
                        type="number"
                        default-value="1"
                        v-model="predictSensorId"
                        class="col-span-2 h-8"
                      />
                    </div>
                    <Button class="mt-4" @click="getPredictionValue">Submit</Button>
                  </div>
                </div>
              </PopoverContent>
            </Popover>
            <Separator orientation="vertical" class="h-9" />
            <DarkModeToggle variant="ghost" />
          </div>
        </div>
      </header>
      <div class="flex flex-1 flex-col gap-4 p-4 pt-0">
        <slot />
      </div>
    </SidebarInset>
  </SidebarProvider>
</template>
