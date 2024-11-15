
export const intervalTypes = Object.freeze({
  high: 5000, // best for development to see changes & during events  
  medium: 15000, // default 
  low: 30000, // best when changes aren't occuring 
});

export const updateScheduler = {
  updateId: null,
  lastUpdated: null,
  callback: null,
  delay: intervalTypes.medium,
  isRunning: false,
  stringDelay: "medium",
  upTime: Date.now(),
  setCallback(callback) {
    if (typeof callback !== 'function') {
      throw new Error(`Callback must be a function`);
    }
    this.callback = callback;
    if (this.isRunning) {
      this.pause();
      this.start();
    }
    console.log(`[SET] scheduler set to -> ${this.stringDelay}`);
  },
  start() {
    if (this.isRunning) {
      return;
    }
    if (!this.callback) {
      throw new Error(`Callback is required to start the scheduler`);
    }
    console.log(`[START] scheduler set to -> ${this.stringDelay}`);
    this.isRunning = true;
    this.delay = intervalTypes[this.stringDelay];
    this.lastUpdated = Date.now();
    this.updateId = setTimeout(() => this.execute(), this.delay);
  },
  pause() {
    console.log(`[PAUSED] scheduler set to -> ${this.stringDelay}`);
    if (!this.isRunning) {
      console.warn("Cannot pause the scheduler because it is not running");
      return;
    }
    clearTimeout(this.updateId);
    this.updateId = null;
    this.isRunning = false;
  },
  setDelay(newDelay) {
    this.stringDelay = newDelay;
    this.delay = intervalTypes[newDelay];
    console.log(`Delay now set to ${this.delay} (${newDelay})`);
    if (!this.isRunning) {
      return;
    }
    clearTimeout(this.updateId);
    const elapsed = Date.now() - this.lastUpdated;
    console.log(`Scheduler delay changed to ${newDelay}`);
    const nextDelay = Math.max(0, this.delay - elapsed);
    this.updateId = setTimeout(() => this.execute(), nextDelay);
  },
  async execute() {
    if (!this.isRunning || !this.callback) {
      return;
    }
    this.lastUpdated = Date.now();
    try {
      await this.callback();
    } catch (error) {
      console.error(`UpdateError: ${error}`);
    } finally {
      if (this.isRunning) {
        const elapsed = Date.now() - this.lastUpdated;
        const nextDelay = Math.max(0, this.delay - elapsed);  
        this.updateId = setTimeout(() => this.execute(), nextDelay);
      }
    }
  },
};
