<template>
  <v-app
    :style="{
      '--drawer-width': sidebarOffset,
      '--right-panel-width': rightPanelOffset,
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
      :style="{
        right: right_panel_open
          ? (extra_content_config.width || 300) + 'px'
          : '0px',
      }"
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
                'right-panel-trigger':
                  rightPanelTriggerStepId === step.id && right_panel_open,
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

    <!-- Right side panel for extra content -->
    <v-navigation-drawer
      v-if="isExtraContentAvailable"
      v-model="right_panel_open"
      :width="extra_content_config.width || 300"
      app
      right
      class="right-panel"
      hide-overlay
    >
      <div style="display: flex; flex-direction: column; height: 100%">
        <div class="drawer-header">
          <div class="app-title">
            <v-icon class="mr-2">{{
              extra_content_config.icon || "mdi-widgets"
            }}</v-icon>
            <span class="title font-weight-medium">{{
              extra_content_config.title || "Extra Content"
            }}</span>
          </div>
          <v-spacer></v-spacer>
          <v-btn
            icon
            @click="toggleRightPanel"
            class="pin-btn"
            title="Close panel"
          >
            <v-icon small>mdi-close</v-icon>
          </v-btn>
        </div>

        <!-- Main panel description -->
        <div
          v-if="extra_content_config.description"
          class="panel-description pa-3"
        >
          <p class="body-2 ma-0 text--secondary">
            {{ extra_content_config.description }}
          </p>
        </div>

        <v-divider class="ma-0 pa-0"></v-divider>

        <div
          class="drawer-top"
          style="flex: 1; overflow-y: auto; overflow-x: hidden"
        >
          <div class="pa-4">
            <div
              v-for="(section, sectionIndex) in extra_content_data"
              :key="`section-${sectionIndex}`"
              class="mb-4"
            >
              <!-- Section header if title/icon provided -->
              <div
                v-if="section.title || section.icon"
                class="section-header mb-3"
              >
                <div class="d-flex align-center">
                  <v-icon v-if="section.icon" small class="mr-2">{{
                    section.icon
                  }}</v-icon>
                  <span
                    v-if="section.title"
                    class="subtitle-2 font-weight-medium"
                    >{{ section.title }}</span
                  >
                </div>
              </div>

              <!-- Section description -->
              <div v-if="section.description" class="section-description mb-3">
                <p class="body-2 ma-0 text--secondary">
                  {{ section.description }}
                </p>
              </div>

              <!-- Section content widgets -->
              <div
                v-for="(widget, widgetIndex) in section.content"
                :key="`section-${sectionIndex}-widget-${widgetIndex}`"
                class="mb-3"
              >
                <jupyter-widget :widget="widget"></jupyter-widget>
              </div>

              <!-- Optional divider -->
              <v-divider
                v-if="
                  section.divider &&
                  sectionIndex < extra_content_data.length - 1
                "
                class="mt-4"
              ></v-divider>
            </div>
          </div>
        </div>
      </div>
    </v-navigation-drawer>

    <!-- Right panel toggle tab -->
    <div
      v-if="isExtraContentAvailable && !right_panel_open && !drawerDisabled"
      class="right-panel-tab"
    >
      <v-btn
        tile
        color="secondary"
        @click="toggleRightPanel"
        class="control-btn"
        title="Show extra content"
      >
        <v-icon>{{
          extra_content_config.toggle_icon || "mdi-chevron-left"
        }}</v-icon>
      </v-btn>
    </div>

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
    extra_content_config: {
      type: Object,
      default: () => ({
        title: "Extra Content",
        icon: "mdi-widgets",
        width: 300,
        description: "",
        toggle_icon: "mdi-chevron-left",
      }),
    },
    extra_content_data: {
      type: Array,
      default: () => [],
    },
    right_panel_open: {
      type: Boolean,
      default: false,
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
  },

  data: () => ({
    drawer: true,
    mini: false,
    isPinned: true,
    collapsedWidth: 60,
    expandedWidth: 320,
    activeStepId: null,
    open_dialog: false,
    rightPanelTriggerStepId: null,
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
      const width = this.extra_content_config.width || 300;
      return this.right_panel_open ? width + "px" : "0px";
    },

    hasExtraContent() {
      return this.extra_content_data && this.extra_content_data.length > 0;
    },

    isExtraContentAvailable() {
      return this.hasExtraContent;
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

    dialogFullscreen() {
      return this.dialog_fullscreen;
    },

    drawerDisabled() {
      return this.open_dialog;
    },
  },

  watch: {
    hasExtraContent: {
      immediate: true,
      handler(newValue) {
        // Close panel if no extra content available
        if (!newValue && this.right_panel_open) {
          this.right_panel_open = false;
        }
      },
    },

    // Watch for right panel opening - close dialogs
    right_panel_open: {
      immediate: true,
      handler(newValue) {
        if (newValue && this.open_dialog) {
          this.open_dialog = false;
          this.activeStepId = null;
        }
      },
    },

    // Watch for dialog opening - close right panel
    open_dialog: {
      immediate: true,
      handler(newValue) {
        if (newValue && this.right_panel_open) {
          this.right_panel_open = false;
          this.rightPanelTriggerStepId = null;
        }
      },
    },
  },

  mounted() {
    window.addEventListener("resize", this.handleResize);
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

    toggleRightPanel() {
      this.right_panel_open = !this.right_panel_open;

      if (!this.right_panel_open) {
        this.rightPanelTriggerStepId = null;
      }
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

    activateStep(step) {
      // Don't allow step activation if drawer is disabled (dialog is open)
      if (this.drawerDisabled) {
        return;
      }

      // Handle right panel actions first
      if (step.right_panel_action) {
        switch (step.right_panel_action) {
          case "open":
            this.right_panel_open = true;
            this.rightPanelTriggerStepId = step.id;
            break;
          case "close":
            this.right_panel_open = false;
            this.rightPanelTriggerStepId = null;
            break;
          case "toggle":
            this.right_panel_open = !this.right_panel_open;
            if (this.right_panel_open) {
              this.rightPanelTriggerStepId = step.id;
            } else {
              this.rightPanelTriggerStepId = null;
            }
            break;
        }
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
  transition: transform 0.3s ease;
}

/* Style active step */
.active-step {
  background-color: var(--v-primary-lighten4, rgba(0, 0, 0, 0.1));
}

/* Style step that triggered the right panel */
.right-panel-trigger {
  background-color: var(--v-secondary-lighten4, rgba(0, 0, 0, 0.08));
  border-left: 3px solid var(--v-secondary-base, #1976d2);
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

.leaflet-right {
  transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  right: var(--right-panel-width) !important;
}

.v-application a {
  color: inherit;
  text-decoration: underline;
}

.link-item {
  color: inherit;
  text-decoration: none !important;
}

/* Right panel styles */
.right-panel {
  /* z-index: 5 !important; */
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.right-panel .v-navigation-drawer__content {
  transition: none !important;
}

.right-panel .section-header {
  padding: 8px 0;
  border-bottom: 1px solid var(--v-divider-base, rgba(0, 0, 0, 0.12));
  margin-bottom: 12px;
}

/* Description styling for both main panel and sections */
.panel-description {
  background-color: var(--v-background-lighten1, rgba(0, 0, 0, 0.05));
  border-radius: 4px;
}

.section-description {
  padding-left: 16px;
  margin-top: 8px;
}

/* Right panel toggle tab */
.right-panel-tab {
  position: fixed;
  top: 50%;
  right: 0;
  transform: translateY(-50%);
  z-index: 6 !important;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.right-panel-tab .control-btn {
  min-width: 40px !important;
  min-height: 40px !important;
  padding: 8px !important;
  margin-bottom: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  border-radius: 3px 0 0 3px !important;
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
