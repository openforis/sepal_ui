<template>
  <div
    v-if="visible && hasContent"
    class="sepal-legend"
    :class="{
      'sepal-legend--collapsed': isCollapsed,
      'sepal-legend--dark': isDark,
      'sepal-legend--light': !isDark,
    }"
  >
    <!-- Collapsed state: icon pill -->
    <div v-if="isCollapsed" class="sepal-legend__pill" @click="toggleCollapse">
      <v-icon small :dark="isDark" :light="!isDark">mdi-map-legend</v-icon>
    </div>

    <!-- Expanded state -->
    <div v-else class="sepal-legend__body">
      <!-- Gradient sections -->
      <div
        v-for="(grad, gi) in parsedGradients"
        :key="'g-' + gi"
        class="sepal-legend__gradient-section"
      >
        <div v-if="grad.title" class="sepal-legend__gradient-title">
          {{ grad.title }}
        </div>
        <div
          class="sepal-legend__gradient-bar"
          :style="{ background: grad.cssGradient }"
        ></div>
        <div class="sepal-legend__gradient-labels">
          <span v-for="(lbl, li) in grad.labels" :key="'gl-' + li">{{
            lbl
          }}</span>
        </div>
      </div>

      <!-- Discrete items -->
      <div v-if="parsedItems.length > 0" class="sepal-legend__items">
        <div
          v-for="(item, ii) in parsedItems"
          :key="'i-' + ii"
          class="sepal-legend__item"
        >
          <span
            class="sepal-legend__chip"
            :style="{ backgroundColor: item.color }"
          ></span>
          <span class="sepal-legend__label">{{ item.label }}</span>
        </div>
      </div>

      <!-- Collapse toggle -->
      <button class="sepal-legend__toggle" @click="toggleCollapse">
        <v-icon x-small :dark="isDark" :light="!isDark"
          >mdi-chevron-down</v-icon
        >
      </button>
    </div>
  </div>
</template>

<script>
module.exports = {
  props: {
    legend_data: {
      type: Object,
      default: () => ({}),
    },
    visible: {
      type: Boolean,
      default: true,
    },
    collapsed: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      internalCollapsed: this.collapsed,
    };
  },
  computed: {
    isDark() {
      // Reactive: changes when the user toggles the Vuetify theme at runtime.
      return (
        this.$vuetify &&
        this.$vuetify.theme &&
        this.$vuetify.theme.dark === true
      );
    },
    isCollapsed() {
      return this.internalCollapsed;
    },
    hasContent() {
      if (!this.legend_data) return false;
      var g = this.legend_data.gradients || [];
      var i = this.legend_data.items || [];
      return g.length > 0 || i.length > 0;
    },
    parsedGradients() {
      if (!this.legend_data || !this.legend_data.gradients) return [];
      return this.legend_data.gradients.map(function (g) {
        var stops = g.colors
          .map(function (c, i) {
            var pct =
              g.colors.length === 1 ? 0 : (i / (g.colors.length - 1)) * 100;
            return c + " " + pct + "%";
          })
          .join(", ");
        return {
          title: g.title || "",
          labels: g.labels || [],
          cssGradient: "linear-gradient(to right, " + stops + ")",
        };
      });
    },
    parsedItems() {
      if (!this.legend_data || !this.legend_data.items) return [];
      return this.legend_data.items;
    },
  },
  watch: {
    collapsed(newValue) {
      this.internalCollapsed = newValue;
    },
  },
  methods: {
    toggleCollapse() {
      const nextCollapsed = !this.internalCollapsed;
      this.internalCollapsed = nextCollapsed;
      if (typeof this.set_collapsed === "function") {
        this.set_collapsed(nextCollapsed);
      }
    },
  },
};
</script>

<style scoped>
.sepal-legend {
  position: fixed;
  bottom: calc(var(--sepal-bottom-reserved, 0px) + 16px);
  left: calc(
    var(--sepal-drawer-width, 0px) +
      (
        100vw - var(--sepal-drawer-width, 0px) -
          var(--sepal-right-panel-width, 0px)
      ) / 2
  );
  transform: translateX(-50%);
  z-index: 1000;
  pointer-events: auto;
  font-family: Roboto, sans-serif;
  transition: left 0.3s ease, bottom 0.3s ease;
}

/* Hide while a step dialog/modal is open — the legend's stacking context
   sits above the modal scrim due to the jupyter-widget z-index, so simply
   removing it from the layer is the cleanest fix. */
body.sepal-modal-open .sepal-legend {
  display: none;
}

.sepal-legend__pill,
.sepal-legend__body {
  backdrop-filter: blur(4px);
}

.sepal-legend__pill {
  border-radius: 16px;
  padding: 6px 12px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
}

.sepal-legend__body {
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-width: 90vw;
  position: relative;
}

/* --- Dark theme --- */
.sepal-legend--dark .sepal-legend__pill,
.sepal-legend--dark .sepal-legend__body {
  background: rgba(33, 33, 33, 0.85);
  color: #fff;
}

/* --- Light theme --- */
.sepal-legend--light .sepal-legend__pill,
.sepal-legend--light .sepal-legend__body {
  background: rgba(255, 255, 255, 0.9);
  color: rgba(0, 0, 0, 0.87);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.08);
}

/* --- Gradient --- */
.sepal-legend__gradient-section {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sepal-legend__gradient-title {
  font-size: 11px;
  opacity: 0.8;
  text-align: center;
}

.sepal-legend__gradient-bar {
  height: 12px;
  border-radius: 3px;
  min-width: 200px;
}

.sepal-legend__gradient-labels {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  opacity: 0.85;
}

/* --- Discrete items --- */
.sepal-legend__items {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 12px;
  align-items: center;
}

.sepal-legend__item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.sepal-legend__chip {
  width: 14px;
  height: 14px;
  border-radius: 3px;
  flex-shrink: 0;
}

.sepal-legend--dark .sepal-legend__chip {
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.sepal-legend--light .sepal-legend__chip {
  border: 1px solid rgba(0, 0, 0, 0.2);
}

.sepal-legend__label {
  white-space: nowrap;
  font-size: 12px;
}

/* --- Toggle --- */
.sepal-legend__toggle {
  position: absolute;
  top: 4px;
  right: 4px;
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.6;
  padding: 2px;
  line-height: 1;
}

.sepal-legend__toggle:hover {
  opacity: 1;
}
</style>
