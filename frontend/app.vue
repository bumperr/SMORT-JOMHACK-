<script setup lang="ts">
import {useToast} from "@/components/ui/toast/use-toast";

const router = useRouter();
const route = useRoute();
const user = useCurrentUser();

const {toast} = useToast();

onMounted(() => {
  watch(user, (user, prevUser) => {
    if (prevUser && !user) {
      // user logged out
      router.push("/login");
    } else if (user && typeof route.query.redirect === "string") {
      // user logged in
      router.push(route.query.redirect);
    }
  });

  // if (process.env.NODE_ENV !== "production") {
  //   toast({
  //     title: "DEVELOPMENT MODE",
  //     description: "Be careful with the API calls!",
  //     variant: "destructive",
  //   });
  // }
});
</script>

<template>
  <NuxtLoadingIndicator/>
  <NuxtLayout>
    <NuxtPage/>
  </NuxtLayout>
  <Toaster/>
</template>
