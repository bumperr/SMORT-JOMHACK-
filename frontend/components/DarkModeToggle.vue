<script setup lang="ts">
import type ButtonVariants from "@/components/button";

const props = withDefaults(
  defineProps<{
    class?: HTMLAttributes["class"];
    variant?: ButtonVariants["variant"];
  }>(),
  { variant: "outline" },
);

const colorMode = useColorMode();
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button :variant="props.variant" size="icon" :class="props.class">
        <Icon
          name="radix-icons:moon"
          class="rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0"
        />
        <Icon
          name="radix-icons:sun"
          class="absolute rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100"
        />
        <span class="sr-only">Toggle theme</span>
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end">
      <DropdownMenuItem @click="colorMode.preference = 'light'">Light</DropdownMenuItem>
      <DropdownMenuItem @click="colorMode.preference = 'dark'">Dark</DropdownMenuItem>
      <DropdownMenuItem @click="colorMode.preference = 'system'">System</DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
