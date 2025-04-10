<!-- Adapted (hard copied) from  https://github.com/widgetti/solara/blob/master/solara/lab/components/theming.vue-->
<template>
  <v-btn icon @click="countClicks">
    <v-icon>
      {{
        this.clicks === 1
          ? this.on_icon
          : this.clicks === 2
          ? this.off_icon
          : this.auto_icon
      }}
    </v-icon>
  </v-btn>
</template>
<script>
export default {
  name: "ThemeToggle",

  props: {
    dark: {
      type: [Boolean, null],
      default: null,
    },

    enable_auto: {
      type: Boolean,
      default: false,
    },
    on_icon: {
      type: String,
      default: "mdi-weather-night",
    },
    off_icon: {
      type: String,
      default: "mdi-weather-sunny",
    },
    auto_icon: {
      type: String,
      default: "mdi-auto-fix",
    },
  },
  data() {
    return {
      clicks: 1,
      lim: 2,
      storedTheme: null,
    };
  },

  created() {
    if (!window.sepalUi) {
      window.sepalUi = {};
    }
  },
  mounted() {
    if (window.sepalUi) {
      if (localStorage.getItem(":sepalUi:theme.variant")) {
        // eslint-disable-next-line vue/no-mutating-props
        this.dark = this.initTheme();
      }
    }

    if (this.dark === false) {
      this.clicks = 2;
    } else if (this.dark === null) {
      this.clicks = 3;
    }
    this.lim = this.enable_auto ? 3 : 2;
  },
  methods: {
    countClicks() {
      if (this.clicks < this.lim) {
        this.clicks++;
      } else {
        this.clicks = 1;
      }
      // eslint-disable-next-line vue/no-mutating-props
      this.dark = this.get_theme_bool(this.clicks);
    },
    get_theme_bool(clicks) {
      if (clicks === 3) {
        return null;
      } else if (clicks === 2) {
        return false;
      } else {
        return true;
      }
    },
    stringifyTheme() {
      return this.dark === true
        ? "dark"
        : this.dark === false
        ? "light"
        : "auto";
    },
    initTheme() {
      let storedTheme = null;
      storedTheme = JSON.parse(localStorage.getItem(":sepalUi:theme.variant"));
      return storedTheme === "dark"
        ? true
        : storedTheme === "light"
        ? false
        : null;
    },
    setTheme() {
      if (window.sepalUi && this.dark === null) {
        this.$vuetify.theme.dark = this.prefersDarkScheme();
        return;
      }
      this.$vuetify.theme.dark = this.dark;
    },
    prefersDarkScheme() {
      return (
        window.matchMedia &&
        window.matchMedia("(prefers-color-scheme: dark)").matches
      );
    },
  },
  watch: {
    clicks() {
      if (window.sepalUi) {
        this.$vuetify.theme.variant = this.stringifyTheme();
      }
      this.setTheme();
      if (window.sepalUi) {
        localStorage.setItem(
          ":sepalUi:theme.variant",
          JSON.stringify(this.$vuetify.theme.variant)
        );
      }
    },
  },
};
</script>
