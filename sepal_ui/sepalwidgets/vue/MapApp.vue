<template>
  <v-app :style="{ '--drawer-width': sidebarOffset }">
    <div
      v-if="main_map && main_map.length > 0"
      id="map-container"
      class="map-background"
      @click="handleMapClick"
    >
      <jupyter-widget :widget="main_map[0]"></jupyter-widget>
    </div>

    <div
      v-if="activeStep && activeStep.display === 'step'"
      class="step-content-container"
    >
      <jupyter-widget :widget="activeStep.content"></jupyter-widget>
    </div>

    <v-navigation-drawer
      v-model="drawer"
      :mini-variant="mini"
      :mini-variant-width="collapsedWidth"
      :width="expandedWidth"
      app
      permanent
    >
      <div style="display: flex; flex-direction: column; height: 100%">
        <div
          class="drawer-top"
          style="flex: 1; overflow-y: auto; overflow-x: hidden"
        >
          <div class="drawer-controls">
            <v-btn
              icon
              @click="toggleDrawer"
              class="toggle-btn mb-2 ml-1"
              :title="mini ? 'Expand sidebar' : 'Collapse sidebar'"
            >
              <v-icon>{{
                mini ? "mdi-chevron-right" : "mdi-chevron-left"
              }}</v-icon>
            </v-btn>

            <v-btn
              icon
              @click="togglePin"
              class="pin-btn mb-2"
              :title="isPinned ? 'Unpin sidebar' : 'Pin sidebar'"
              v-if="!mini"
            >
              <v-icon>{{ isPinned ? "mdi-pin" : "mdi-pin-outline" }}</v-icon>
            </v-btn>
          </div>

          <v-divider class="ma-0 pa-0"></v-divider>

          <!-- steps -->
          <v-list dense class="pa-0 ma-0">
            <v-list-item
              @click="showMainMap"
              :class="{ 'active-step': !activeStepId }"
            >
              <v-list-item-icon>
                <v-icon class="mb-1">mdi-map</v-icon>
              </v-list-item-icon>
              <v-list-item-content v-if="!mini">
                <v-list-item-title class="font-weight-medium"
                  >Map</v-list-item-title
                >
              </v-list-item-content>
            </v-list-item>

            <v-list-item
              v-for="(step, i) in steps"
              :key="`step-${i}`"
              @click="activateStep(step)"
              :class="{ 'active-step': activeStepId === step.id }"
            >
              <v-list-item-icon>
                <v-icon class="mb-1">{{
                  step.icon || "mdi-checkbox-blank-circle-outline"
                }}</v-icon>
              </v-list-item-icon>
              <v-list-item-content v-if="!mini">
                <v-list-item-title class="font-weight-medium">{{
                  step.name
                }}</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </div>

        <div class="drawer-bottom" style="padding: 16px 0">
          <v-divider class="mb-4"></v-divider>
          <!-- helper steps -->
          <v-list class="pa-0 ma-0" dense v-if="!mini">
            <v-list-item
              v-for="(link, i) in externalLinks"
              :key="`external-${i}`"
              :href="link.url"
              target="_blank"
              link
            >
              <v-list-item-icon>
                <v-icon class="mb-1">{{ link.icon }}</v-icon>
              </v-list-item-icon>
              <v-list-item-content v-if="!mini">
                <v-list-item-title class="d-flex align-center">
                  {{ link.title }}
                  <v-spacer></v-spacer>
                  <v-icon small class="ml-1">mdi-open-in-new</v-icon>
                </v-list-item-title>
              </v-list-item-content>
            </v-list-item>

            <v-divider class="mt-2 mb-4"></v-divider>
            <!-- configuration drawers -->
            <v-list-item>
              <v-list-item-content>
                <v-list-item-title class="d-flex align-center">
                  Theme configuration
                  <v-spacer></v-spacer>
                  <jupyter-widget :widget="theme_toggle[0]"></jupyter-widget>
                </v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </div>
      </div>
    </v-navigation-drawer>

    <!-- main Area -->
    <v-main class="transparent-main" @click="handleMainClick"> </v-main>

    <!-- dialog for dialog-type steps -->
    <v-dialog
      v-model="dialogOpen"
      :width="dialogWidthComputed"
      :fullscreen="dialogFullscreen"
      content-class="dialog-container"
      @click:outside="handleDialogOutsideClick"
    >
      <v-card class="dialog-card">
        <v-card-title class="headline d-flex justify-space-between">
          <span>{{ activeStep ? activeStep.name : "" }}</span>
          <v-btn icon @click="closeDialog">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>

        <v-divider></v-divider>

        <v-card-text class="dialog-content">
          <jupyter-widget
            v-if="
              activeStep && activeStep.content && activeStep.content.length > 0
            "
            :widget="activeStep.content"
            class="jupyter-widget-container"
          ></jupyter-widget>
        </v-card-text>

        <v-divider
          v-if="
            activeStep && activeStep.actions && activeStep.actions.length > 0
          "
        ></v-divider>

        <v-card-actions
          v-if="
            activeStep && activeStep.actions && activeStep.actions.length > 0
          "
        >
          <v-spacer></v-spacer>
          <v-btn
            v-for="(action, i) in activeStep.actions"
            :key="`action-${i}`"
            :color="action.color || 'primary'"
            :text="action.text !== false"
            @click="handleActionClick(action)"
          >
            {{ action.label }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-app>
</template>

<script>
export default {
  name: "MapApp",

  props: {
    main_map: {
      type: Array,
      default: () => [],
    },
    steps_data: {
      type: Array,
      default: () => [],
    },
    steps_content: {
      type: Array,
      default: () => [],
    },
    repo_url: {
      type: String,
      default: "https://github.com/sepal-contrib/",
    },
    dialog_width: {
      type: [String, Number],
      default: 800,
    },
    dialog_fullscreen: {
      type: Boolean,
      default: false,
    },
  },

  data: () => ({
    drawer: true,
    mini: false,
    isPinned: true,
    collapsedWidth: 60,
    expandedWidth: 320,
    activeStepId: null,
    dialogOpen: false,
  }),

  computed: {
    steps() {
      return this.steps_data.map((step, index) => ({
        ...step,
        content: this.steps_content[index],
      }));
    },

    activeStep() {
      if (!this.activeStepId) return null;
      return this.steps.find((step) => step.id === this.activeStepId);
    },

    sidebarOffset() {
      return this.mini ? this.collapsedWidth + "px" : this.expandedWidth + "px";
    },

    externalLinks() {
      return [
        {
          title: "Source Code",
          icon: "mdi-code-braces",
          url: this.repo_url,
        },
        {
          title: "Wiki",
          icon: "mdi-book-open-page-variant",
          url: `${this.repo_url}/blob/main/doc/en.rst`,
        },
        {
          title: "Report Bug",
          icon: "mdi-bug",
          url: `${this.repo_url}/issues/new`,
        },
      ];
    },

    dialogWidthComputed() {
      // get dialog width based on prop and viewport
      // Ensure dialog width doesn't exceed viewport minus sidebar
      const viewportWidth = window.innerWidth;
      const sidebarWidth = this.mini ? this.collapsedWidth : this.expandedWidth;
      const maxDialogWidth = viewportWidth - sidebarWidth - 40;

      if (
        typeof this.dialog_width === "string" &&
        this.dialog_width.includes("%")
      ) {
        const percentage = parseInt(this.dialog_width, 10) / 100;
        return Math.min(maxDialogWidth, viewportWidth * percentage);
      }

      return Math.min(maxDialogWidth, this.dialog_width || 800);
    },
  },

  watch: {
    dialog_fullscreen: {
      immediate: true,
      handler(newValue) {
        this.dialogFullscreen = newValue;
      },
    },
  },

  mounted() {
    window.addEventListener("resize", this.handleResize);

    if (this.steps.length > 0) {
      this.activeStepId = null;
    }
  },

  beforeDestroy() {
    window.removeEventListener("resize", this.handleResize);
  },

  methods: {
    handleResize() {
      this.$forceUpdate();
    },

    toggleDrawer() {
      this.mini = !this.mini;
    },

    togglePin() {
      this.isPinned = !this.isPinned;
    },

    expandIfMini() {
      if (this.mini) {
        this.mini = false;
      }
    },

    handleMapClick() {
      this.collapseIfNotPinned();
    },

    handleMainClick() {
      this.collapseIfNotPinned();
    },

    collapseIfNotPinned() {
      if (!this.isPinned && !this.mini) {
        this.mini = true;
      }
    },

    activateStep(step) {
      this.activeStepId = step.id;

      // for dialog display type, open the dialog
      if (step.display === "dialog") {
        this.dialogOpen = true;
      } else {
        // close dialog when activating non-dialog step
        this.dialogOpen = false;
      }

      this.$emit("step-activated", step);
    },

    closeDialog() {
      this.dialogOpen = false;
    },

    handleDialogOutsideClick() {
      // TODO: implement logic to close dialog when clicking outside
    },

    handleActionClick(action) {
      this.$emit("step-action", {
        step: this.activeStep,
        action: action,
      });

      if (action.close) {
        this.closeDialog();
      }
    },

    showMainMap() {
      this.activeStepId = null;
      this.dialogOpen = false;
      this.$emit("show-main-map");
    },
  },
};
</script>

<style scoped>
.map-background {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
}

/* Step content container */
.step-content-container {
  position: fixed;
  top: 0;
  left: var(--drawer-width);
  right: 0;
  bottom: 0;
  z-index: 0;
  background-color: var(--v-background-base, #f5f5f5);
  padding: 16px;
  transition: left 0.3s ease;
}

.transparent-main {
  background-color: transparent !important;
  z-index: 1;
  pointer-events: none; /* Allow clicking through to the map */
}

.drawer-header {
  display: flex;
  align-items: center;
  padding: 0 16px;
  height: 64px;
}

.app-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.drawer-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 8px 0 8px;
  width: 100%;
}

.toggle-btn,
.pin-btn {
  background-color: var(
    --v-secondary-lighten5,
    rgba(255, 255, 255, 0.1)
  ) !important;
}

.dialog-container {
  z-index: 1000 !important;
  position: relative;
  margin-left: var(--drawer-width);
}

.dialog-card {
  max-width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.dialog-content {
  min-height: 200px;
  max-height: 70vh;
  overflow-y: auto;
  flex: 1;
}

.jupyter-widget-container {
  width: 100%;
  height: 100%;
}

/* Ensure interactive elements in the drawer can be clicked */
.v-navigation-drawer .v-list-item,
.v-navigation-drawer .v-btn,
.v-navigation-drawer .v-select {
  pointer-events: auto;
}

/* Style active step */
.active-step {
  background-color: var(--v-primary-lighten4, rgba(0, 0, 0, 0.1));
}

/* override sepal-ui default css */
.full-screen-map > .leaflet-container {
  position: fixed !important;
  width: 100vw !important;
  height: 100vh !important;
  z-index: 800;
  bottom: 0;
  left: 0;
}

.v-dialog--active {
  position: relative !important;
}

/* v-dialog overlay should be below our dialog but above other elements */
.v-overlay__scrim {
  z-index: 999 !important;
}

.leaflet-left {
  transition: left 0.3s ease;
  left: var(--drawer-width) !important;
}
</style>
