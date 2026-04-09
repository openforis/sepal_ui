<template>
  <div>
    <!-- Toast Stack: fixed top-right -->
    <div class="toast-stack">
      <v-alert
        v-for="toast in visibleToasts"
        :key="toast.id"
        :type="toast.color"
        dense
        dismissible
        :value="true"
        elevation="6"
        class="toast-alert"
        @input="_dismissToast(toast.id)"
      >
        {{ toast.message }}
        <span v-if="toast.count > 1" class="ml-1">(x{{ toast.count }})</span>
      </v-alert>

      <v-chip v-if="staleErrorCount > 0" color="error" small class="stale-chip">
        {{ staleErrorCount }} more error(s)
      </v-chip>
    </div>

    <!-- Task Progress Pill: positioned relative to right panel -->
    <div
      class="pill-container"
      :class="{ 'pill-hidden': !hasTasks }"
      :style="{ right: pillRight + 'px' }"
    >
      <!-- Collapsed pill -->
      <v-btn
        v-if="!pillExpanded"
        rounded
        color="primary"
        dark
        small
        class="pill-btn"
        @click="pillExpanded = true"
      >
        <v-progress-circular
          v-if="activeCount > 0"
          indeterminate
          :size="16"
          :width="2"
          class="mr-2"
        />
        {{ pillText }}
      </v-btn>

      <!-- Expanded detail panel -->
      <v-card v-else max-width="400" min-width="300" class="pill-card">
        <v-card-title class="py-2">
          <span>Task Progress</span>
          <v-spacer />
          <v-btn icon small @click="pillExpanded = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text style="max-height: 300px; overflow-y: auto">
          <div v-if="displayTasks.length === 0" class="text--secondary">
            No active tasks
          </div>
          <v-card
            v-for="task in displayTasks"
            :key="task.id"
            outlined
            class="mb-2"
          >
            <v-card-title class="py-2" style="font-size: 0.95em">
              {{ task.title }}
              <v-spacer />
              <v-chip x-small :color="task.statusColor">
                {{ task.status }}
              </v-chip>
            </v-card-title>
            <v-card-text class="py-1">
              <div v-if="task.lastStep" style="font-size: 0.85em">
                {{ task.lastStep }}
              </div>
              <v-progress-linear
                v-if="task.progress !== null"
                :value="task.progress * 100"
                :color="task.statusColor"
                height="6"
                rounded
                class="mt-1"
              />
              <div
                v-if="task.totalSteps && task.currentStep"
                style="font-size: 0.75em; color: grey"
              >
                Step {{ task.currentStep }}/{{ task.totalSteps }}
              </div>
              <div
                v-if="task.errorMessage"
                style="color: red; font-size: 0.85em"
              >
                {{ task.errorMessage }}
              </div>

              <!-- Milestone timeline (expandable) -->
              <div v-if="task.milestones && task.milestones.length > 0">
                <v-btn
                  text
                  x-small
                  @click="$set(taskExpanded, task.id, !taskExpanded[task.id])"
                >
                  {{ taskExpanded[task.id] ? "Hide steps" : "Show steps" }}
                </v-btn>
                <v-timeline v-if="taskExpanded[task.id]" dense align-top>
                  <v-timeline-item
                    v-for="(ms, idx) in task.milestones"
                    :key="idx"
                    small
                    color="primary"
                  >
                    {{ ms.message }}
                  </v-timeline-item>
                </v-timeline>
              </div>
            </v-card-text>
          </v-card>
        </v-card-text>
      </v-card>
    </div>
  </div>
</template>

<script>
export default {
  name: "NotificationUI",
  props: {
    toasts: { type: Array, default: () => [] },
    tasks: { type: Array, default: () => [] },
  },
  data() {
    return {
      pillExpanded: false,
      taskExpanded: {},
      dismissTimers: {},
      dismissedIds: new Set(),
      pillRight: 16,
    };
  },
  computed: {
    visibleToasts() {
      // Filter out locally dismissed toasts first
      const active = this.toasts.filter((t) => !this.dismissedIds.has(t.id));

      const now = Date.now() / 1000;
      const staleThreshold = 30;

      const fresh = [];
      const staleErrors = [];

      for (const t of active) {
        if (t.color === "error" && now - t.created_at > staleThreshold) {
          staleErrors.push(t);
        } else {
          fresh.push(t);
        }
      }

      fresh.sort((a, b) => b.created_at - a.created_at);
      const visible = fresh.slice(0, 3);

      const remaining = 3 - visible.length;
      if (remaining > 0 && staleErrors.length > 0) {
        staleErrors.sort((a, b) => b.created_at - a.created_at);
        visible.push(...staleErrors.slice(0, remaining));
      }

      return visible.slice(0, 3);
    },
    staleErrorCount() {
      const visibleIds = new Set(this.visibleToasts.map((t) => t.id));
      return this.toasts.filter(
        (t) => t.color === "error" && !visibleIds.has(t.id)
      ).length;
    },
    activeCount() {
      return this.tasks.filter(
        (t) => t.status === "running" || t.status === "pending"
      ).length;
    },
    displayTasks() {
      return this.tasks.filter((t) => t.status !== "pending");
    },
    hasTasks() {
      return this.displayTasks.length > 0 || this.activeCount > 0;
    },
    pillText() {
      if (this.activeCount > 0) {
        const running = this.tasks.filter((t) => t.status === "running");
        if (running.length > 0) {
          const current = running[running.length - 1];
          let label = current.title;
          if (current.lastStep) {
            label += " — " + current.lastStep;
          } else {
            label += "...";
          }
          if (this.activeCount > 1) {
            label += ` (+${this.activeCount - 1} more)`;
          }
          return label;
        }
        return this.activeCount === 1
          ? "1 task running"
          : `${this.activeCount} tasks running`;
      }

      // Show last finished
      const finished = this.tasks.filter(
        (t) => t.status === "completed" || t.status === "failed"
      );
      if (finished.length > 0) {
        const last = finished[finished.length - 1];
        const status = last.status === "completed" ? "Done" : "Failed";
        return `${last.title} — ${status}`;
      }
      return "";
    },
  },
  watch: {
    toasts: {
      immediate: true,
      handler(newToasts) {
        // Set up auto-dismiss timers for new toasts with timeouts
        for (const toast of newToasts) {
          if (toast.timeout && !this.dismissTimers[toast.id]) {
            this.dismissTimers[toast.id] = setTimeout(() => {
              this._dismissToast(toast.id);
              delete this.dismissTimers[toast.id];
            }, toast.timeout * 1000);
          }
        }

        // Clean up timers and dismissed IDs for removed toasts
        const currentIds = new Set(newToasts.map((t) => t.id));
        for (const id of Object.keys(this.dismissTimers)) {
          if (!currentIds.has(id)) {
            clearTimeout(this.dismissTimers[id]);
            delete this.dismissTimers[id];
          }
        }
        // Prune stale dismissed IDs
        for (const id of this.dismissedIds) {
          if (!currentIds.has(id)) {
            this.dismissedIds.delete(id);
          }
        }
      },
    },
  },
  mounted() {
    this._updatePillPosition();
    // Watch the right-panel drawer for open/close (class and style changes)
    this._pollInterval = setInterval(() => this._updatePillPosition(), 50);
  },
  beforeDestroy() {
    for (const id of Object.keys(this.dismissTimers)) {
      clearTimeout(this.dismissTimers[id]);
    }
    if (this._pollInterval) {
      clearInterval(this._pollInterval);
    }
  },
  methods: {
    _dismissToast(id) {
      // Instantly hide in Vue, then notify Python to clean up bus state
      this.dismissedIds.add(id);
      this.dismissedIds = new Set(this.dismissedIds); // trigger reactivity
      this.dismiss_toast(id);
    },
    _updatePillPosition() {
      // Find the right panel drawer by its class
      const panel = document.querySelector(".right-panel.v-navigation-drawer");
      if (!panel) {
        this.pillRight = 16;
        return;
      }
      // Vuetify keeps offsetWidth even when closed (uses transform to hide).
      // Check for the --open class to know if it's actually visible.
      const isOpen = panel.classList.contains("v-navigation-drawer--open");
      this.pillRight = isOpen ? panel.offsetWidth + 16 : 16;
    },
  },
};
</script>

<style scoped>
.toast-stack {
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: 1000;
  width: 350px;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.toast-alert {
  pointer-events: auto;
  opacity: 0.88;
  margin-bottom: 0 !important;
}

.stale-chip {
  pointer-events: auto;
}

.pill-container {
  position: fixed;
  bottom: 16px;
  z-index: 1000;
  max-width: 500px;
  transition: right 0.3s ease, opacity 0.3s ease;
  opacity: 0.92;
}

.pill-hidden {
  pointer-events: none;
  opacity: 0;
}

.pill-btn {
  text-transform: none;
  letter-spacing: normal;
}

.pill-card {
  max-height: 400px;
  overflow-y: auto;
}
</style>
