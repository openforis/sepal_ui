<template>
  <v-row class="d-flex align-center mx-2">
    <v-menu
      v-model="showFileMenu"
      :min-width="500"
      :max-width="500"
      :close-on-content-click="false"
      @open="resetScroll"
    >
      <template v-slot:activator="{ on }">
        <v-btn v-on="on" color="primary" class="mr-2">
          <v-icon left small>fa-solid fa-search</v-icon>
          {{ label }}
        </v-btn>
      </template>

      <v-card>
        <v-text-field
          v-model="searchQuery"
          label="Search files"
          prepend-inner-icon="fa-solid fa-filter"
          clearable
          @click:clear="searchQuery = ''"
          class="mx-3 mt-4"
          style="margin-bottom: 5px; margin-top: 5px;"
        ></v-text-field>

        <v-progress-linear
          v-if="loading"
          indeterminate
          background-color="menu"
        />

        <v-list
          ref="fileList"
          color="menu"
          flat
          dense
          :max-height="300"
          style="overflow: auto;"
        >
          <!-- Always show the parent item if it exists -->
          <v-list-item
            v-if="parentItem"
            @click="onFileSelect(parentItem)"
          >
            <v-list-item-action>
              <v-icon :color="getIconColor(parentItem)">
                {{ getIconName(parentItem) }}
              </v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>
                .. /{{ getParentName(parentItem.path) }}
              </v-list-item-title>
            </v-list-item-content>
          </v-list-item>

          <!-- Show effective file items if they exist -->
          <v-list-item-group v-if="nonParentFiles.length">
            <v-list-item
              v-for="(item, index) in nonParentFiles"
              :key="index"
              :value="item.path"
              @click="onFileSelect(item)"
            >
              <v-list-item-action>
                <v-icon :color="getIconColor(item)">
                  {{ getIconName(item) }}
                </v-icon>
              </v-list-item-action>
              <v-list-item-content>
                <v-list-item-title>{{ item.name }}</v-list-item-title>
              </v-list-item-content>
              <v-list-item-action-text
                class="ml-1"
                v-if="item.type === 'file'"
              >
                {{ formatFileSize(item.size) }}
              </v-list-item-action-text>
            </v-list-item>
          </v-list-item-group>

          <!-- If there are no effective file items, show the fallback message -->
          <v-list-item v-if="!nonParentFiles.length">
            <v-list-item-content class="text-center">
              <v-list-item-title class="font-italic text-grey">
                {{ searchQuery ? 'No files matching "' + searchQuery + '"' : getEmptyMsg()}}
              </v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>

    <v-text-field
      v-model="value"
      readonly
      label="Selected file"
      class="ml-2"
      :error-messages="getErrorMessages""
    >
      <template v-slot:append>
        <v-btn
          v-if="clearable"
          icon
          color="primary"
          @click.stop="reset"
        >
          <v-icon>fa-solid fa-times</v-icon>
        </v-btn>
        <v-btn icon color="primary" @click.stop="reloadFiles">
          <v-icon>fa-solid fa-sync-alt</v-icon>
        </v-btn>
      </template>
    </v-text-field>
  </v-row>
</template>



  
  <script>
  export default {
    name: 'FileInput',
  
    props: {
      file_list: {
        type: Array,
        default: () => []
      },
      current_folder: {
        type: String,
        default: '/'
      },
      loading: {
        type: Boolean,
        default: false
      },
      label: {
        type: String,
        default: 'Select File'
      },
      value: {
        type: String,
        default: ''
      },
      clearable: {
        type: Boolean,
        default: false
      },
      root: {
        type: String,
        default: '/'
      },
      reload_files: {
        type: Number,
        default: 0
      },
      reset_prop: {
        type: Number,
        default: 0
      },
      base_path: {
        type: String,
        default: ''
      },
      extensions: {
        type: Array,
        default: () => []
      },
      error_messages: {
        type: Array,
        default: []
      }
    },
  
    data() {
      return {
        showFileMenu: false,
        searchQuery: ''
      }
    },
  
    computed: {
      filteredFiles() {
        if (!this.searchQuery) return this.file_list;
        return this.file_list.filter(file =>
          file.name.toLowerCase().includes(this.searchQuery.toLowerCase())
        );
      },
      parentItem() {
      return this.filteredFiles.length && this.filteredFiles[0].name === '..'
        ? this.filteredFiles[0]
        : null;
    },
    // Remove the parent item from the list of files.
    nonParentFiles() {
      if (this.parentItem) {
        return this.filteredFiles.slice(1);
      }
      return this.filteredFiles;
    },
    getErrorMessages() {
      return this.error_messages;
    },


    },
  
    methods: {
      reloadFiles() {
        this.reload_files += 1;
      },
      getEmptyMsg() {
        return this.extensions.length
          ? `No files with extensions ${this.extensions.join(', ')}`
          : 'No files available';
      },
  
      reset() {
        this.value = '';
        this.error_messages = [];
        this.reset_prop += 1;
      },
  
      onFileSelect(item) {
        if (item.type === 'directory') {
          this.current_folder = item.path;
        } else {
          this.value = this.base_path? this.base_path + "/" + item.path : item.path;
          this.showFileMenu = false;
        }
        // Reset search query when a file or folder is clicked
        this.searchQuery = '';
      },
  
      getFileMetadata(item) {
        const fileMetadata = {
            "": { color: "primary_contrast", icon: "fa-regular fa-folder" },
            ".csv": { color: "secondary_contrast", icon: "fa-solid fa-table" },
            ".txt": { color: "secondary_contrast", icon: "fa-solid fa-table" },
            ".tif": { color: "secondary_contrast", icon: "fa-regular fa-image" },
            ".tiff": { color: "secondary_contrast", icon: "fa-regular fa-image" },
            ".png": { color: "secondary_contrast", icon: "fa-regular fa-image" },
            ".vrt": { color: "secondary_contrast", icon: "fa-regular fa-image" },
            ".shp": { color: "secondary_contrast", icon: "fa-solid fa-vector-square" },
            ".ipynb": { color: "green", icon: "fa-regular fa-file-code" },
            ".py": { color: "secondary_contrast", icon: "fa-regular fa-file-code" },
            ".json": { color: "secondary_contrast", icon: "fa-regular fa-file-code" },
            ".geojson": { color: "secondary_contrast", icon: "fa-solid fa-vector-square" },
            ".gpkg": { color: "secondary_contrast", icon: "fa-solid fa-vector-square" },
            ".pdf": { color: "secondary_contrast", icon: "fa-regular fa-file-pdf" },
            ".zip": { color: "secondary_contrast", icon: "fa-regular fa-file-archive" },
            ".log": { color: "secondary_contrast", icon: "fa-regular fa-file-alt" },
            "DEFAULT": { color: "anchor", icon: "fa-regular fa-file" },
            "PARENT": { color: "anchor", icon: "fa-regular fa-folder-open" }
        };

        if (item.type === 'directory') {
            return item.name === '..' ? fileMetadata["PARENT"] : fileMetadata[""];
        }

        const ext = item.name.slice(item.name.lastIndexOf('.')).toLowerCase();
        return fileMetadata[ext] || fileMetadata["DEFAULT"];
    },

    getIconName(item) {
        return this.getFileMetadata(item).icon;
    },

    getIconColor(item) {
        return this.getFileMetadata(item).color;
    },


  
      getParentName(path) {
        const parts = path.split('/');
        return parts[parts.length - 1] || '';
      },
  
      formatFileSize(bytes) {
        if (!bytes) return '';
        const units = ['B', 'KB', 'MB', 'GB'];
        let size = bytes;
        let unit = 0;
        while (size >= 1024 && unit < units.length - 1) {
          size /= 1024;
          unit++;
        }
        return Math.round(size * 100) / 100 + ' ' + units[unit];
      },
  
      resetScroll() {
        this.$nextTick(() => {
          if (this.$refs.fileList) {
            this.$refs.fileList.$el.scrollTop = 0;
          }
        });
      }
    }
  }
  </script>
  