<template>
  <div>
    <!-- Main language selector button -->
    <v-btn
      depressed
      @click="openDialog"
      style="background-color: unset !important"
    >
      <v-icon small left>mdi-translate</v-icon>
      {{ currentLanguage }}
    </v-btn>

    <!-- Dialog with language options -->
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
          <v-alert
            type="info"
            border="left"
            colored-border
            icon="mdi-alert"
            class="mt-4"
            >To apply the language settings, you need to refresh the
            page.</v-alert
          >
        </v-card-text>
        <v-divider></v-divider>
        <v-card-text>
          <v-list>
            <v-list-item
              v-for="(locale, index) in available_locales"
              :key="index"
              @click="selectLanguage(locale.code)"
            >
              <v-list-item-content>
                <v-list-item-title
                  >{{ locale.name }} ({{ locale.code }})</v-list-item-title
                >
              </v-list-item-content>

              <v-list-item-action v-if="locale.code === selectedLanguage">
                <v-icon color="primary">mdi-check</v-icon>
              </v-list-item-action>
            </v-list-item>
          </v-list>
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
      default: () => [{ code: "en", name: "English", flag: "gb" }],
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
      handler(newCountries) {
        // If there's only one language available, set it as the current language
        if (newCountries.length === 1) {
          const onlyLanguage = newCountries[0].code;

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
    // Check if the selected locale exists in available locales
    const localeExists = this.available_locales.some(
      (country) => country.code === this.selected_locale
    );

    if (localeExists) {
      // If locale exists, update current and selected language
      this.currentLanguage = this.selected_locale;
      this.selectedLanguage = this.selected_locale;
    } else if (this.available_locales.length > 0) {
      // If locale doesn't exist but we have available locales, use the first one
      this.currentLanguage = this.available_locales[0].code;
      this.selectedLanguage = this.available_locales[0].code;
      // Emit events to update parent component
      this.$emit("update:selected_locale", this.available_locales[0].code);
      this.$emit("language-changed", this.available_locales[0].code);
    } else {
      // Fallback to 'en' if no locales available
      const fallbackLocale = "en";
      this.currentLanguage = fallbackLocale;
      this.selectedLanguage = fallbackLocale;
      this.$emit("update:selected_locale", fallbackLocale);
      this.$emit("language-changed", fallbackLocale);
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
