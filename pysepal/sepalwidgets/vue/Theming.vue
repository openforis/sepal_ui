<!-- Adapted (hard copied) from  https://github.com/widgetti/solara/blob/master/solara/lab/components/theming.vue-->
<template>
  <v-btn icon @click="countClicks">
    <v-icon small>
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
    resolved_dark: {
      type: Boolean,
      default: false,
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
      mediaQuery: null,
    };
  },

  created() {
    if (!window.sepalUi) {
      window.sepalUi = {};
    }
  },
  mounted() {
    this.mediaQuery =
      window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)");
    if (this.mediaQuery) {
      if (this.mediaQuery.addEventListener) {
        this.mediaQuery.addEventListener(
          "change",
          this.handleColorSchemeChange
        );
      } else if (this.mediaQuery.addListener) {
        this.mediaQuery.addListener(this.handleColorSchemeChange);
      }
    }

    if (window.sepalUi) {
      if (localStorage.getItem(":sepalUi:theme.variant")) {
        // eslint-disable-next-line vue/no-mutating-props
        this.dark = this.initTheme();
      }
    }

    this.lim = this.enable_auto ? 3 : 2;
    this.syncClicksFromDark();
    this.setTheme();
    this.updateResolvedDark();
  },
  beforeDestroy() {
    if (this.mediaQuery) {
      if (this.mediaQuery.removeEventListener) {
        this.mediaQuery.removeEventListener(
          "change",
          this.handleColorSchemeChange
        );
      } else if (this.mediaQuery.removeListener) {
        this.mediaQuery.removeListener(this.handleColorSchemeChange);
      }
    }
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
    syncClicksFromDark() {
      let next = 1;
      if (this.dark === false) {
        next = 2;
      } else if (this.dark === null) {
        next = 3;
      }
      if (this.clicks !== next) {
        this.clicks = next;
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
    updateResolvedDark() {
      // eslint-disable-next-line vue/no-mutating-props
      this.resolved_dark = !!(
        this.$vuetify &&
        this.$vuetify.theme &&
        this.$vuetify.theme.dark
      );
    },
    prefersDarkScheme() {
      return (
        window.matchMedia &&
        window.matchMedia("(prefers-color-scheme: dark)").matches
      );
    },
    handleColorSchemeChange() {
      if (this.dark === null) {
        this.setTheme();
        this.updateResolvedDark();
      }
    },
    jupyter_fire_button(event, data) {
      this.countClicks();
    },
  },
  watch: {
    dark() {
      this.syncClicksFromDark();
      this.setTheme();
      this.updateResolvedDark();
    },
    clicks() {
      if (window.sepalUi) {
        this.$vuetify.theme.variant = this.stringifyTheme();
      }
      this.setTheme();
      this.updateResolvedDark();
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
