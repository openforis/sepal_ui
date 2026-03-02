<template>
  <v-list-item
    :input-value="input_value"
    :href="href"
    :target="target"
    :link="link"
    @click="on_click_python()"
  >
    <template v-for="(child, index) in children" :key="index">
      <jupyter-widget :widget="child"></jupyter-widget>
    </template>
  </v-list-item>
</template>

<script>
export default {
  name: "DrawerItem",
  props: {
    input_value: {
      type: Boolean,
      default: false,
    },
    href: {
      type: String,
      default: null,
    },
    target: {
      type: String,
      default: null,
    },
    link: {
      type: Boolean,
      default: false,
    },
  },
  watch: {
    resize(newValue) {
      if (newValue) {
        window.dispatchEvent(new Event("resize"));
        setTimeout(() => {
          window.dispatchEvent(new Event("resize"));
        }, 100); // Wait for 1 second (1000 milliseconds)
      }
    },
  },
};
</script>
