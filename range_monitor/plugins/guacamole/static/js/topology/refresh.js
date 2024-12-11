export const intervalTypes = Object.freeze({
	high: 5000, // best for development to see changes & during events
	medium: 15000, // default
	low: 30000, // best when changes aren't occurring
});

class AsyncScheduler {
	constructor(callback, delay) {
		this.callback = callback;
		this.delay = delay;
		this.controller = null;
		this.isRunning = false;
		this.stopOn = null;
	}

	async _wait(ms) {
		return new Promise((resolve) => {
			const timer = setTimeout(() => resolve(true), ms);
			this.controller.signal.addEventListener("abort", () => {
				clearTimeout(timer);
				resolve(false);
			});
		});
	}

	async _executeLoop() {
    let shouldContinue = true;
    while (shouldContinue) {
			shouldContinue = await this._runInterval()
        .catch((error) => {
			  	if (this.errorHandler) {
						this.errorHandler(error, this);
					} else {
						this.stop();
					}
			  });
		}
	}
	async _runInterval() {
		if (this.stopOn && this.stopOn()) {
			this.stop();
			return false;
		}
		let shouldContinue = true;
		const startTime = Date.now();
		await this.callback();
		const executionDuration = Date.now() - startTime;
		const remainingTime = Math.max(0, this.delay - executionDuration);
		if (remainingTime > 0) {
			shouldContinue = await this._wait(remainingTime);
		}
		return shouldContinue;
	}
	start(stopOn = null, errorHandler = null) {
		this.stopOn = stopOn;
		this.errorHandler = errorHandler;
		this.controller = new AbortController();
		this._executeLoop();
	}

	stop() {
		if(this.controller === null) {
			return;
		}
    this.controller.abort();
		this.controller = null;
	}

	setDelay(newDelay, shouldContinue  = false) {
		this.stop();
		this.delay = newDelay;
		if (shouldContinue) {
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
		this.callback = callback;
		this.scheduler = new AsyncScheduler(callback, this.delay);
		console.log(`[SET] Scheduler set to -> ${this.stringDelay}`);
	},

	start(onStop = null, onError = null) {
		if (!this.callback || !this.scheduler) {
			throw new Error("Scheduler not initialized. Call setCallback first.");
		}
		if (this.isRunning) {
			return;
		}
		this.scheduler.start(onStop, onError);

		try {
			this.isRunning = true;
			this.lastUpdated = Date.now();
			console.log(`[START] Scheduler set to -> ${this.stringDelay}`);
		} catch (error) {
			this.isRunning = false;
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
	},
};
