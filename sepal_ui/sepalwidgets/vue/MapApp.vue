<template>
  <v-app
    :style="{
      '--drawer-width': sidebarOffset,
      '--right-panel-width': rightPanelOffset,
      '--right-panel-open': rightPanelOpen ? '1' : '0',
    }"
  >
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
      :class="{ 'right-panel-open': rightPanelOpen }"
    >
      <jupyter-widget :widget="activeStep.content"></jupyter-widget>
    </div>

    <v-navigation-drawer
      v-model="drawer"
      :mini-variant="mini"
      :mini-variant-width="collapsedWidth"
      :width="expandedWidth"
      :class="{ 'drawer-disabled': drawerDisabled }"
      app
      permanent
    >
      <div style="display: flex; flex-direction: column; height: 100%">
        <div class="drawer-header">
          <div class="app-title">
            <v-icon class="mr-2">{{
              app_icon ? app_icon : "mdi-earth"
            }}</v-icon>
            <span class="title font-weight-medium">{{ app_title }}</span>
          </div>

          <v-spacer></v-spacer>
          <v-btn
            v-if="!mini"
            icon
            @click="togglePin"
            class="pin-btn"
            :title="isPinned ? 'Unpin sidebar' : 'Pin sidebar'"
          >
            <v-icon small>{{
              isPinned ? "mdi-pin" : "mdi-pin-outline"
            }}</v-icon>
          </v-btn>
        </div>

        <v-divider class="ma-0 pa-0"></v-divider>

        <div
          class="drawer-top"
          style="flex: 1; overflow-y: auto; overflow-x: hidden"
        >
          <!-- steps -->
          <v-list dense class="pa-0 ma-0">
            <v-list-item
              v-if="main_map && main_map.length > 0"
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
              :class="{
                'active-step':
                  activeStepId === step.id && step.content_enabled !== false,
              }"
              :data-step-id="step.id"
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
          <v-list class="pa-0 ma-0" dense>
            <v-list-item
              v-for="(link, i) in externalLinks"
              :key="`external-${i}`"
              :href="link.url"
              target="_blank"
              class="link-item"
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
                <v-list-item-title
                  :class="{
                    'd-flex align-center justify-center': !mini,
                    'flex-column': mini,
                  }"
                >
                  <div :class="{ 'mb-2': mini }">
                    <slot name="theme-toggle"></slot>
                    <jupyter-widget :widget="theme_toggle[0]"></jupyter-widget>
                  </div>
                  <div>
                    <slot name="language-selector"></slot>
                    <jupyter-widget
                      :widget="language_selector[0]"
                    ></jupyter-widget>
                  </div>
                </v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </div>
      </div>
    </v-navigation-drawer>

    <!-- Right Panel Component -->
    <jupyter-widget
      v-if="right_panel && right_panel.length > 0"
      :widget="right_panel[0]"
    ></jupyter-widget>

    <div class="sidebar-controls" :style="{ left: sidebarOffset }">
      <v-btn
        tile
        color="primary"
        @click="toggleDrawer"
        class="control-btn mb-2"
        :title="mini ? 'Expand sidebar' : 'Collapse sidebar'"
      >
        <v-icon>{{ mini ? "mdi-menu-right" : "mdi-menu-left" }}</v-icon>
      </v-btn>
    </div>

    <!-- main Area -->
    <v-main class="transparent-main" @click="handleMainClick"> </v-main>

    <!-- dialog for dialog-type steps -->
    <v-dialog
      v-model="open_dialog"
      :width="dialogWidthComputed"
      :height="dialogHeightComputed"
      :fullscreen="dialogFullscreen"
      :overlay="true"
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

        <v-card-text class="dialog-content pt-4">
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
            :text="action.cancel ? true : false"
            :outlined="action.cancel ? true : false"
            color="primary"
            small
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
    right_panel_config: {
      type: Object,
      default: () => ({
        title: "Extra Content",
        icon: "mdi-widgets",
        width: 300,
        description: "",
        toggle_icon: "mdi-chevron-left",
      }),
    },
    right_panel_content: {
      type: Array,
      default: () => [],
    },
    right_panel: {
      type: Array,
      default: () => [],
    },
    right_panel_open: {
      type: Boolean,
      default: false,
    },
    right_panel_width: {
      type: Number,
      default: 300,
    },
    repo_url: {
      type: String,
      default: "https://github.com/sepal-contrib/",
    },
    docs_url: {
      type: String,
      default: "",
    },
    dialog_width: {
      type: [String, Number],
      default: 800,
    },
    dialog_fullscreen: {
      type: Boolean,
      default: false,
    },
    app_title: {
      type: String,
      default: "SEPAL Module",
    },
    app_icon: {
      type: String,
      default: "mdi-earth",
    },
    theme_toggle: {
      type: Array,
      default: () => [],
    },
    language_selector: {
      type: Array,
      default: () => [],
    },
    initial_step: {
      type: Number,
      default: null,
    },
  },

  data: () => ({
    drawer: true,
    mini: false,
    isPinned: true,
    collapsedWidth: 60,
    expandedWidth: 320,
    activeStepId: null,
    open_dialog: false,
  }),

  computed: {
    steps() {
      return this.steps_data;
    },

    activeStep() {
      if (!this.activeStepId) return null;
      return this.steps.find((step) => step.id === this.activeStepId);
    },

    sidebarOffset() {
      return this.mini ? this.collapsedWidth + "px" : this.expandedWidth + "px";
    },

    rightPanelOffset() {
      return this.right_panel_width + "px";
    },

    rightPanelOpen() {
      return this.right_panel_open;
    },

    externalLinks() {
      return [
        {
          title: "Source Code",
          icon: "mdi-code-braces",
          url: this.repo_url,
        },
        {
          title: "Documentation",
          icon: "mdi-book-open-page-variant",
          url: this.docs_url || `${this.repo_url}/blob/main/doc/en.rst`,
        },
        {
          title: "Report Bug",
          icon: "mdi-bug",
          url: `${this.repo_url}/issues/new`,
        },
      ];
    },

    dialogWidthComputed() {
      const viewportWidth = window.innerWidth;
      const sidebarWidth = this.mini ? this.collapsedWidth : this.expandedWidth;
      const maxDialogWidth = viewportWidth - sidebarWidth - 40;

      // Check if active step has a specific width
      let targetWidth = this.dialog_width;
      if (this.activeStep && this.activeStep.width) {
        targetWidth = this.activeStep.width;
      }

      if (typeof targetWidth === "string" && targetWidth.includes("%")) {
        const percentage = parseInt(targetWidth, 10) / 100;
        return Math.min(maxDialogWidth, viewportWidth * percentage);
      }

      return Math.min(maxDialogWidth, targetWidth || 800);
    },

    dialogHeightComputed() {
      // Check if active step has a specific height
      if (this.activeStep && this.activeStep.height) {
        const viewportHeight = window.innerHeight;
        const maxDialogHeight = viewportHeight - 80; // Leave some margin

        if (
          typeof this.activeStep.height === "string" &&
          this.activeStep.height.includes("%")
        ) {
          const percentage = parseInt(this.activeStep.height, 10) / 100;
          return Math.min(maxDialogHeight, viewportHeight * percentage);
        }

        return Math.min(maxDialogHeight, this.activeStep.height);
      }

      // Return null if no height is specified (let dialog auto-size)
      return null;
    },

    dialogFullscreen() {
      return this.dialog_fullscreen;
    },

    drawerDisabled() {
      return this.open_dialog;
    },
  },

  watch: {
    // Watch for steps data changes to auto-activate first step when no main map
    steps_data: {
      immediate: true,
      handler() {
        this.autoActivateFirstStepIfNeeded();
      },
    },

    // Watch for main_map changes to handle auto-activation
    main_map: {
      immediate: true,
      handler() {
        this.autoActivateFirstStepIfNeeded();
      },
    },

    // Watch for initial_step changes
    initial_step: {
      immediate: true,
      handler() {
        this.autoActivateFirstStepIfNeeded();
      },
    },
  },

  mounted() {
    window.addEventListener("resize", this.handleResize);
    // Auto-activate first step if no main map
    this.autoActivateFirstStepIfNeeded();
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

    handleRightPanelAction(action) {
      // Call Python method to handle right panel state
      // Note: Python method is vue_handle_right_panel_action, called without 'vue_' prefix
      this.handle_right_panel_action(action);
    },

    activateStep(step) {
      // Don't allow step activation if drawer is disabled (dialog is open)
      if (this.drawerDisabled) {
        return;
      }

      // Handle right panel actions first
      if (step.right_panel_action) {
        this.handleRightPanelAction(step.right_panel_action);
      }

      // Only change step content if step has content
      if (step.content && step.content.length > 0) {
        this.activeStepId = step.id;

        // For dialog display type, open the dialog
        if (step.display === "dialog") {
          this.open_dialog = true;
        } else {
          // Close dialog when activating non-dialog step
          this.open_dialog = false;
        }

        this.$emit("step-activated", step);
      } else {
        // For action-only steps, provide visual feedback
        this.provideStepFeedback(step);
        this.$emit("step-action", step);
      }
    },

    closeDialog() {
      this.open_dialog = false;
      this.activeStepId = null;
    },

    handleDialogOutsideClick() {
      if (this.activeStep && this.activeStep.display === "dialog") {
        this.closeDialog();
      }
    },

    handleActionClick(action) {
      this.$emit("step-action", {
        step: this.activeStep,
        action: action,
      });

      if (action.close) {
        this.closeDialog();
      }

      if (action.next) {
        this.activeStepId = action.next;
      }
    },

    showMainMap() {
      // Don't allow if drawer is disabled (dialog is open)
      if (this.drawerDisabled) {
        return;
      }

      this.activeStepId = null;
      this.open_dialog = false;
      this.$emit("show-main-map");
    },

    provideStepFeedback(step) {
      // Add a temporary visual feedback for action-only steps
      // This could be enhanced with animations or other visual cues
      const stepElement = document.querySelector(`[data-step-id="${step.id}"]`);
      if (stepElement) {
        stepElement.style.transition = "background-color 0.2s ease";
        stepElement.style.backgroundColor =
          "var(--v-primary-lighten4, rgba(0, 0, 0, 0.1))";
        setTimeout(() => {
          stepElement.style.backgroundColor = "";
        }, 200);
      }
    },

    autoActivateFirstStepIfNeeded() {
      // Check if initial_step is specified
      if (this.initial_step !== null && !this.activeStepId) {
        const initialStep = this.steps.find(
          (step) => step.id === this.initial_step
        );
        if (
          initialStep &&
          initialStep.content &&
          initialStep.content.length > 0 &&
          initialStep.content_enabled !== false &&
          (initialStep.display === "step" || initialStep.display === "dialog")
        ) {
          this.$nextTick(() => {
            this.activeStepId = initialStep.id;

            // If it's a dialog step, open the dialog
            if (initialStep.display === "dialog") {
              this.open_dialog = true;
            }

            this.$emit("step-auto-activated", initialStep);
          });
          return;
        }
      }

      // Only auto-activate if:
      // 1. No main map is available
      // 2. No step is currently active
      // 3. There are steps available
      // 4. No initial_step was specified or it wasn't found
      const hasMainMap = this.main_map && this.main_map.length > 0;
      const hasSteps = this.steps && this.steps.length > 0;

      if (!hasMainMap && !this.activeStepId && hasSteps) {
        // Find the first step with content that can be displayed
        const firstStepWithContent = this.steps.find(
          (step) =>
            step.content &&
            step.content.length > 0 &&
            step.content_enabled !== false &&
            (step.display === "step" || step.display === "dialog")
        );

        if (firstStepWithContent) {
          // Use a small delay to ensure the component is fully mounted
          this.$nextTick(() => {
            this.activeStepId = firstStepWithContent.id;

            // If it's a dialog step, open the dialog
            if (firstStepWithContent.display === "dialog") {
              this.open_dialog = true;
            }

            this.$emit("step-auto-activated", firstStepWithContent);
          });
        }
      }
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
  transition: left 0.3s ease, right 0.3s ease;
}

/* When right panel is open, adjust step content */
.step-content-container.right-panel-open {
  right: var(--right-panel-width);
}

.transparent-main {
  background-color: transparent !important;
  z-index: 1;
  pointer-events: none; /* Allow clicking through to the map */
}

.drawer-header {
  display: flex;
  align-items: center;
  padding: 16px;
  height: 64px;
}

.app-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: flex;
  align-items: center;
}

/* New sidebar controls styling */
.sidebar-controls {
  position: fixed;
  z-index: 5 !important;
  top: 50%;
  transform: translateY(-50%);
  z-index: 100;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: left 0.3s ease;
  margin-left: -5px;
}

.control-btn {
  min-width: 25px !important;
  padding: 0px !important;
  margin-bottom: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  border-radius: 3px !important;
}

.dialog-container {
  z-index: 1010 !important;
}

.dialog-card {
  max-width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  margin: 0 auto !important;
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
  transition: transform 0.3s ease;
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

/* v-dialog overlay should be below our dialog but above other elements */
.v-overlay__scrim {
  z-index: 1005 !important;
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
}

/* Ensure dialog overlay covers navigation drawer and right panel */
.v-application .v-overlay--active .v-overlay__scrim {
  z-index: 1005 !important;
}

/* Reduce navigation drawer z-index when dialog is open */
.v-application .v-navigation-drawer {
  z-index: 1002 !important;
}

/* Ensure right panel is below dialog overlay */
.v-application .jupyter-widget {
  position: relative;
  z-index: 1001 !important;
}

.leaflet-left {
  transition: left 0.3s ease;
  left: var(--drawer-width) !important;
}

.leaflet-right {
  transition: right 0.3s ease;
  right: calc(var(--right-panel-width) * var(--right-panel-open)) !important;
}

.v-application a {
  color: inherit;
  text-decoration: underline;
}

.link-item {
  color: inherit;
  text-decoration: none !important;
}

/* Disabled drawer when dialog is open */
.drawer-disabled {
  pointer-events: none !important;
  /* opacity: 0.6 !important; */
}

.drawer-disabled .v-list-item {
  pointer-events: none !important;
}
</style>
