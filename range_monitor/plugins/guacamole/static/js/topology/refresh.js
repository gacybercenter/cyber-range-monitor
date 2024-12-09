export const intervalTypes = Object.freeze({
  high: 5000,   // best for development to see changes & during events
  medium: 15000, // default
  low: 30000,   // best when changes aren't occurring
});

class AsyncScheduler {
  constructor(callback, delay) {
    this.callback = callback;
    this.delay = delay;
    this.controller = null;
    this.isRunning = false;
    this.lastExecuted = null;
    this._error = null;
  }

  async _wait(ms) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(resolve, ms);
      this.controller.signal.addEventListener('abort', () => {
        clearTimeout(timer);
        reject(new Error('Scheduler aborted'));
      });
    });
  }

  async _executeLoop() {
    while (this.isRunning) {
      try {
        const startTime = Date.now();
        await this.callback();
        this.lastExecuted = startTime;

        const executionDuration = Date.now() - startTime;
        const remainingTime = Math.max(0, this.delay - executionDuration);

        if (remainingTime > 0) {
          await this._wait(remainingTime);
        }
      } catch (error) {
        if (error.name === 'AbortError') break;
        this._error = error;
        this.stop();
        throw new Error(`Scheduler error: ${error.message}`);
      }
    }
  }

  start() {
    if (this.isRunning) {
      throw new Error('Scheduler is already running');
    }
    
    if (this._error) {
      throw new Error(`Cannot restart failed scheduler: ${this._error.message}`);
    }

    this.controller = new AbortController();
    this.isRunning = true;
    this._executeLoop().catch(error => {
      console.error('Scheduler failed:', error);
      this.cleanup();
    });
  }

  stop() {
    if (!this.isRunning) return;
    this.cleanup();
  }

  cleanup() {
    this.isRunning = false;
    if (this.controller) {
      this.controller.abort();
      this.controller = null;
    }
  }

  setDelay(newDelay) {
    this.delay = newDelay;
    if (this.isRunning) {
      this.stop();
      this.start();
    }
  }
}

export const updateScheduler = {
  scheduler: null,
  lastUpdated: null,
  callback: null,
  delay: intervalTypes.medium,
  isRunning: false,
  stringDelay: "medium",
  upTime: Date.now(),

  setCallback(callback) {
    if (typeof callback !== 'function') {
      throw new Error('Callback must be a function');
    }
    this.callback = callback;
    this.scheduler = new AsyncScheduler(callback, this.delay);
    console.log(`[SET] Scheduler set to -> ${this.stringDelay}`);
  },

  start() {
    if (!this.callback || !this.scheduler) {
      throw new Error('Scheduler not initialized. Call setCallback first.');
    }
    if (this.isRunning) {
      return;
    }
    
    try {
      this.isRunning = true;
      this.lastUpdated = Date.now();
      this.scheduler.start();
      console.log(`[START] Scheduler set to -> ${this.stringDelay}`);
    } catch (error) {
      this.isRunning = false;
      console.error('Failed to start scheduler:', error);
    }
  },

  pause() {
    if (!this.isRunning) {
      return;
    }
    this.isRunning = false;
    this.scheduler.stop();
    console.log(`[PAUSED] Scheduler set to -> ${this.stringDelay}`);
  },

  setDelay(newDelay) {
    if (!intervalTypes.hasOwnProperty(newDelay)) {
      throw new Error(`Invalid delay type: ${newDelay}`);
    }
    
    this.stringDelay = newDelay;
    this.delay = intervalTypes[newDelay];
    
    if (this.scheduler) {
      this.scheduler.setDelay(this.delay);
    }
    console.log(`Delay now set to ${this.delay}ms (${newDelay})`);
  }
};

