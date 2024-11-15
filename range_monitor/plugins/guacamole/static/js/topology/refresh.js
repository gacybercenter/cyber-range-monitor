
export const intervalTypes = Object.freeze({
  high: 5000,   // best for development to see changes & during events
  medium: 15000, // default
  low: 30000,   // best when changes aren't occurring
});

export const updateScheduler = {
  updateId: null, // id of the timeout / interval
  lastUpdated: null, // last time the scheduler was updated
  callback: null, // the async update func
  delay: intervalTypes.medium, // the delay between updates
  isRunning: false,
  stringDelay: "medium", // used for when user changes delay
  upTime: Date.now(),
  /**
   * NOTE: Simply sets the callback for 
   * scheduler and nothing else 
   * @param {callback} callback 
   */
  setCallback(callback) {
    if (typeof callback !== 'function') {
      throw new Error(`Callback must be a function`);
    }
    this.callback = callback;
    console.log(`[SET] Scheduler set to -> ${this.stringDelay}`);
  },
  start() {
    if (this.isRunning) {
      console.warn(`[NOTE] - Scheduler was attempted to be set while already running`);
      return;
    }
    if (!this.callback) {
      throw new Error(
        `The update callback for the scheduler is not set, set it before calling this method`
      );
    }
    console.log(`[START] Scheduler set to -> ${this.stringDelay}`);
    this.isRunning = true;
    this.delay = intervalTypes[this.stringDelay];
    this.lastUpdated = Date.now();
    this.updateId = setTimeout(() => this.execute(), this.delay);
  },
  pause() {
    if (!this.isRunning) {
      console.warn("[NOTE] - Cannot pause the scheduler because it is not running");
      return;
    }
    console.log(`[PAUSED] Scheduler set to -> ${this.stringDelay}`);
    clearTimeout(this.updateId);
    this.updateId = null;
    this.isRunning = false;
  },
  setDelay(newDelay) {
    if (!intervalTypes.hasOwnProperty(newDelay)) {
      throw new Error(`Invalid delay type: ${newDelay}`);
    }
    this.stringDelay = newDelay;
    this.delay = intervalTypes[newDelay];
    console.log(`Delay now set to ${this.delay}ms (${newDelay})`);
    if (!this.isRunning) {
      return;
    }
    clearTimeout(this.updateId);
    const elapsed = Date.now() - this.lastUpdated;
    const nextDelay = Math.max(0, this.delay - elapsed);
    console.log(`[SET] - Scheduler delay changed to ${newDelay}`);
    this.updateId = setTimeout(() => this.execute(), nextDelay);
  },
  async execute() {
    if (!this.isRunning || !this.callback) {
      return;
    }
    const nextScheduledTime = this.lastUpdated + this.delay;
    this.callback()
      .then(() => {
        console.log(`[SCHEDULER_SUCESS] - Updated at ${new Date(nextScheduledTime).toLocaleTimeString()}`);
      })
      .catch((error) => {
        console.error(`[SCHEDULER_ERROR] - ${error}`);
      })
      .finally(() => {
        if (!this.isRunning) {
          return;
        }
        const now = Date.now();
        const nextDelay = Math.max(0, nextScheduledTime - now);
        this.lastUpdated = nextScheduledTime;
        this.updateId = setTimeout(() => this.execute(), nextDelay);
      });
  },
};

