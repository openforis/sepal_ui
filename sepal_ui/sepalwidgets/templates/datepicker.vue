<v-menu
    v-model="menu"
    :close-on-content-click="false"
    :nudge-right="40"
    transition="scale-transition"
    offset-y
    min-width="290px"
    dark
  >
    <template v-slot:activator="{ on, attrs }">
      <v-text-field
        v-model="v_model"
        :label="label"
        prepend-icon="mdi-calendar"
        readonly
        v-bind="attrs"
        v-on="on"          >
      </v-text-field>
    </template>
    <v-date-picker

      v-model="v_model"
      dark
      @input="menu = false"
      @input=date_click()
    >
    </v-date-picker>
</v-menu>