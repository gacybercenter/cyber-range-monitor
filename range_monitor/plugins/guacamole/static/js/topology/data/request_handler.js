// topology/data/request_handler.js
export { RequestHandler };

/**
 * @class RequestHandler
 * @description
 * responsible for getting fetching / parsing
 * data from the guac API endpoint and also
 * providing detailed errors
 */
class RequestHandler {
	static reqErrorMsg(error) {
		return `Request Failed: check your network connection or the may be down. (${error.message})`;
	}
	static jsonErrorMsg(error) {
		return `Failed to parse API response: ${error.message}`;
	}

	/**
	 * fetches the guac data from the API
	 * endpoint, caller must handle exceptions
	 * @param {number} timeoutMs
	 * @returns {object[]}
	 */
	static async fetchGuacAPI(timeoutMs = 10000) {
		const guacURL = "api/topology_data";
		const controller = new AbortController();
		const { signal } = controller;

		const requestId = setTimeout(() => {
			controller.abort();
		}, timeoutMs);

		let result;
		try {
			const data = await fetch(guacURL, { signal });
			clearTimeout(requestId);
			result = [await data.json(), null];
		} catch (error) {
			error.message = RequestHandler.getError(error);
			result = [null, error];
		} finally {
			clearTimeout(requestId);
		}
		return result;
	}

	/**
	 * @param {Error} errorObj
	 * @param {string} errorMsg
	 */
	static getError(errorObj) {
		if (errorObj.name === "AbortError") {
			return "The request to the Guacamole API timed out, please try again.";
		}
		return errorObj.message;
	}
}

class TopologyError extends Error {
	constructor(message) {
		super(
			`TopologyError: something went wrong in the topology.\n[INFO] - ${message}`
		);
		this.name = "TopologyError";
	}
}

class RequestTimeoutError extends Error {
	constructor() {
		super(
			"RequestTimeoutError: the request took too long to complete due to connection or accessibility isssues."
		);
		this.name = "RequestTimeoutError";
	}
}
