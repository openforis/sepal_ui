<!-- Custom dialog to trigger a resize event when it is open -->
<template>
  <v-dialog
    v-model="show"
    :persistent="persistent"
    :max-width="max_width"
    :min-width="min_width"
    :retain-focus="retain_focus"
  >
    <template v-for="(child, index) in children" :key="index">
      <jupyter-widget :widget="child"></jupyter-widget>
    </template>
  </v-dialog>
</template>

<script>
export default {
  watch: {
    show(newValue) {
      if (newValue) {
        window.dispatchEvent(new Event("resize"));
      }
    },
  },
};
</script>
