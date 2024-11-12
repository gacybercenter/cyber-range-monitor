


export const intervalTypes = Object.freeze({
  "high": 5000,
  "medium" : 15000,
  "low" : 30000 
});
export const updateScheduler = {
  updateId: null,
  lastUpdated: null,
  delay: intervalTypes.medium,
  callback: null,
  running: false,
  paused: false,
  setCallback(callback) {
    if(typeof callback !== 'function') {
      throw new Error(`Callback must be a function`);
    }
    this.callback = callback;
  },
  start(delay = intervalTypes.medium) {
    if(this.running) {
      return;
    }
    if(!this.callback) {
      throw new Error(`Callback is required to start the scheduler`);
    }
    this.running = true;
    this.paused = false;
    this.delay = delay;
    this.execute();
  },
  pause() {
    if (this.isPaused) {
      return;
    }
    
    clearTimeout(this.updateId);
    this.updateId = null;

    this.paused = true;
    this.running = false;
  },
  async execute() {
    if(this.paused || !this.callback) {
      return;
    }
    try {
      await this.callback();
    } catch(error) {
      console.error(`UpdateError: ${error}`);
    } finally {
      if(!this.paused) {
        this.lastUpdated = Date.now();
        this.updateId = setTimeout(() => this.execute(), this.delay);
      }
    }
  }
};



