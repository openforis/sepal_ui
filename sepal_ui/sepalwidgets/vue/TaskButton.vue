<template>
  <v-btn
    :color="currentColor"
    :disabled="false"
    @click="on_click_python()"
    :style="{ minWidth: buttonWidth }"
    :small="small"
    :x-small="x_small"
    :large="large"
    :x-large="x_large"
    :block="block"
    ref="button"
  >
    <!-- Custom loading spinner when running -->
    <v-progress-circular
      v-if="isLoading"
      :size="spinnerSize"
      :width="2"
      color="white"
      indeterminate
      class="mr-2"
    ></v-progress-circular>
    <!-- Regular icon when not loading -->
    <v-icon v-else-if="currentIcon" left :small="small || x_small">{{
      currentIcon
    }}</v-icon>
    {{ currentText }}
  </v-btn>
</template>

<script>
export default {
  name: "TaskButton",
  data() {
    return {
      buttonWidth: "auto",
    };
  },
  props: {
    original_text: {
      type: String,
      default: "Start Taskss",
    },
    cancel_text: {
      type: String,
      default: "Cancel",
    },
    original_color: {
      type: String,
      default: "primary",
    },
    cancel_color: {
      type: String,
      default: "error",
    },
    original_icon: {
      type: String,
      default: "",
    },
    cancel_icon: {
      type: String,
      default: "mdi-close",
    },
    is_running: {
      type: Boolean,
      default: false,
    },
    show_loading: {
      type: Boolean,
      default: true,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    small: {
      type: Boolean,
      default: false,
    },
    x_small: {
      type: Boolean,
      default: false,
    },
    large: {
      type: Boolean,
      default: false,
    },
    x_large: {
      type: Boolean,
      default: false,
    },
    block: {
      type: Boolean,
      default: false,
    },
  },
  mounted() {
    // Capture the original button width after layout is complete
    this.captureButtonWidth();
  },
  methods: {
    captureButtonWidth() {
      // Use ResizeObserver or polling to wait for actual width
      const checkWidth = () => {
        if (this.$refs.button && this.$refs.button.$el) {
          const width = this.$refs.button.$el.offsetWidth;
          if (width > 0) {
            this.buttonWidth = `${width}px`;
            console.log("Captured button width:", this.buttonWidth);
            return true;
          }
        }
        return false;
      };

      // Try immediately first
      if (!checkWidth()) {
        // If width is still 0, use requestAnimationFrame to wait for layout
        const waitForLayout = () => {
          if (!checkWidth()) {
            requestAnimationFrame(waitForLayout);
          }
        };
        requestAnimationFrame(waitForLayout);
      }
    },
    on_click_python() {
      this.$emit("click");
    },
  },
  computed: {
    currentText() {
      return this.is_running ? this.cancel_text : this.original_text;
    },
    currentColor() {
      return this.is_running ? this.cancel_color : this.original_color;
    },
    currentIcon() {
      return this.is_running ? this.cancel_icon : this.original_icon;
    },
    isLoading() {
      return this.is_running && this.show_loading;
    },
    isDisabled() {
      return this.disabled;
    },
    spinnerSize() {
      if (this.x_small) return 12;
      if (this.small) return 14;
      if (this.large) return 20;
      if (this.x_large) return 24;
      return 16;
    },
  },
};
</script>
