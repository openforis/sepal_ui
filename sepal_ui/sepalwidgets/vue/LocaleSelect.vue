<template>
  <div>
    <v-btn @click="openDialog">
      <v-icon left>mdi-translate</v-icon>
      {{ currentLanguage }}
    </v-btn>
    <v-dialog v-model="dialogOpen" max-width="400">
      <v-card>
        <v-card-title class="headline d-flex justify-space-between">
          <span>Select your language</span>
          <v-btn icon @click="closeDialog">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text>
          <v-list>
            <v-list-item
              v-for="(locale, index) in available_locales"
              :key="index"
              @click="selectLanguage(locale.code)"
              :class="{ secondary: locale.code === selectedLanguage }"
            >
              <v-list-item-content>
                <v-list-item-title
                  >{{ locale.name }} ({{ locale.code }})</v-list-item-title
                >
              </v-list-item-content>

              <v-list-item-action v-if="locale.code === selectedLanguage">
                <v-icon color="secondary">mdi-check</v-icon>
              </v-list-item-action>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-text class="text-center pt-2">
          <v-alert type="info">
            To apply the language settings, you need to refresh the page.
          </v-alert>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  name: "LanguageSelector",

  props: {
    available_locales: {
      type: [String, Array, Object],
      required: true,
    },
    selected_locale: {
      type: String,
      required: true,
      default: "en",
    },
  },

  data() {
    return {
      dialogOpen: false,
      selectedLanguage: this.selected_locale,
      currentLanguage: this.selected_locale,
    };
  },

  watch: {
    selected_locale(newValue) {
      this.currentLanguage = newValue;
      this.selectedLanguage = newValue;
    },

    available_locales: {
      immediate: true,
      handler(newLocale) {
        // If there's only one language available, set it as the current language
        if (newLocale.length === 1) {
          const onlyLanguage = newLocale[0].code;

          if (this.currentLanguage !== onlyLanguage) {
            this.currentLanguage = onlyLanguage;
            this.selectedLanguage = onlyLanguage;
            this.$emit("update:selected_locale", onlyLanguage);
            this.$emit("language-changed", onlyLanguage);
          }
        }
      },
    },
  },

  mounted() {
    if (this.available_locales && this.available_locales.length > 0) {
      const firstLocale = this.available_locales[0].code;
      if (this.currentLanguage !== firstLocale) {
        this.currentLanguage = firstLocale;
        this.selectedLanguage = firstLocale;
        this.$emit("update:selected_locale", firstLocale);
        this.$emit("language-changed", firstLocale);
      }
    }
  },

  methods: {
    openDialog() {
      this.selectedLanguage = this.currentLanguage;
      this.dialogOpen = true;
    },

    closeDialog() {
      this.dialogOpen = false;
    },
    selectLanguage(code) {
      this.selectedLanguage = code;
      if (this.selectedLanguage !== this.currentLanguage) {
        this.currentLanguage = this.selectedLanguage;

        // Emit events for parent component
        this.$emit("update:selected_locale", this.selectedLanguage);
        this.$emit("language-changed", this.selectedLanguage);
      }

      this.dialogOpen = false;
    },
  },
};
</script>
