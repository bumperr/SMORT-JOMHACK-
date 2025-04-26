<script lang="ts">
import { GoogleAuthProvider } from "firebase/auth";
export const googleAuthProvider = new GoogleAuthProvider();
</script>

<script setup lang="ts">
import { useToast } from "@/components/ui/toast/use-toast";
import { signInWithPopup } from "firebase/auth";
import { useFirebaseAuth } from "vuefire";

definePageMeta({
  layout: false,
});

const auth = useFirebaseAuth()!;

const router = useRouter();
const route = useRoute();
const { toast } = useToast();

function signInWithGoogle() {
  signInWithPopup(auth, googleAuthProvider)
    .then(() => router.push(route.params.redirect ?? "/"))
    .catch((reason) => {
      console.error("Failed sign in redirect", reason);
      error.value = reason;
    });
}

const error = ref<Error | null>(null);

onMounted(() => {
  watch(error, (error, prevError) => {
    if (error.value) {
      toast({
        title: "Sign In Error",
        description: error.value,
        variant: "destructive",
      });
    }
  });
});
</script>

<template>
  <main class="w-full h-screen flex items-center justify-center px-4">
    <Card class="w-full max-w-sm">
      <CardHeader>
        <CardTitle class="text-2xl flex justify-between">Login<DarkModeToggle /></CardTitle>
        <CardDescription>Enter your email below to login to your account.</CardDescription>
      </CardHeader>
      <CardContent class="grid gap-4">
        <div class="grid gap-2">
          <Label for="email">Email</Label>
          <Input id="email" type="email" placeholder="john.doe@frost8ytes.com" required disabled />
        </div>
        <div class="grid gap-2">
          <Label for="password">Password</Label>
          <Input id="password" type="password" required placeholder="••••••••" disabled />
        </div>
      </CardContent>
      <CardFooter class="flex-col">
        <Button class="w-full" disabled>Sign in</Button>
        <Separator class="block my-4" label="Or" />
        <Button class="w-full" variant="secondary" @click="signInWithGoogle">
          <Icon name="devicon:google" class="w-4 h-4 mr-2" />
          Sign in with Google
        </Button>
      </CardFooter>
    </Card>
  </main>
</template>
