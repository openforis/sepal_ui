<template>
  <v-card>
    <v-tabs v-model="current">
      <v-tab v-for="(title, index) in titles" :key="index">
        {{ title }}
      </v-tab>
    </v-tabs>

    <v-tabs-items v-model="current">
      <v-tab-item v-for="(item, index) in content" :key="index">
        <jupyter-widget :widget="item"></jupyter-widget>
      </v-tab-item>
    </v-tabs-items>
  </v-card>
</template>

<script>
export default {
  name: "TabsComponent",
  props: {
    titles: {
      type: Array,
      required: true,
    },
    content: {
      type: Array,
      required: true,
    },
    current: {
      type: Number,
      default: 0,
    },
  },
};
</script>
