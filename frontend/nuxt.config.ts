// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2024-11-01",
  devtools: {enabled: true},
  ssr: false,
  modules: [
    "@nuxt/image",
    "@pinia/nuxt",
    "@vueuse/nuxt",
    "@nuxtjs/tailwindcss",
    "@nuxtjs/color-mode",
    "shadcn-nuxt",
    "nuxt-lodash",
    "@nuxt/eslint",
    "@nuxt/icon",
    "nuxt-vuefire",
    "nuxt-mapbox",
  ],
  shadcn: {
    prefix: "",
    componentDir: "./components/ui",
  },
  vuefire: {
    auth: {
      enabled: true,
      sessionCookie: true,
    },
    services: {
      firestore: true,
    },
    config: {
      apiKey: "AIzaSyDjn-bmrNEja2xU_ZXEE87T9dN-kalWMsw",
      authDomain: "smort-thrasher.firebaseapp.com",
      projectId: "smort-thrasher",
      storageBucket: "smort-thrasher.firebasestorage.app",
      messagingSenderId: "551880187815",
      appId: "1:551880187815:web:937503e89178a2205c6082",
    },
    // appCheck: {
    //   debug: process.env.NODE_ENV !== "production",
    //   isTokenAutoRefreshEnabled: true,
    //   provider: "ReCaptchaV3",
    //   key: "6LcWFtcqAAAAAK2sbcVGv1lNSZAVoX-HpAuQn0ce",
    // },
  },
  colorMode: {
    classPrefix: "",
    classSuffix: "",
  },
  // routeRules: {
  //   "/login": { ssr: false },
  // },
  mapbox: {
    accessToken: "pk.eyJ1IjoiZnJvc3Q4eXRlcyIsImEiOiJjbTMwZWM4emUwaXNhMmpxcGMydXV6MWF2In0.NedNyfVIxBrS2skQAfMxsQ",
  },
});
