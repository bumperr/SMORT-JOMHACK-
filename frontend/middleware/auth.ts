export default defineNuxtRouteMiddleware(async (to, from) => {
  const user = await getCurrentUser();

  // code snippet if global middleware
  // if (user && to.name === "login") {
  //   return navigateTo("/");
  // }

  // if (!user && to.name !== "login") {
  //   return navigateTo("/login");
  // }

  if (!user) {
    return navigateTo({
      path: "/login",
      query: {
        redirect: to.fullPath,
      },
    });
  }
});
