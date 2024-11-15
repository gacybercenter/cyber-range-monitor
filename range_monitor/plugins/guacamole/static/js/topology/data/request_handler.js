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
	static reqErrorMsg() {
		return `Request Failed: check your network connection or the may be down.`;
	}
	static jsonErrorMsg() {
		return `Failed to parse API response`;
	}

	/**
	 * fetches the guac data from the API
	 * endpoint, caller must handle exceptions
	 * @param {number} timeoutMs
	 * @returns {object[]}
	 */
	static async fetchGuacAPI(timeoutMs = 10000) {
		const controller = new AbortController();
		const { signal } = controller;
		const requestId = setTimeout(() => {
			controller.abort();
		}, timeoutMs);
		try {
			return await RequestHandler.getData(signal);
		} finally {
			clearTimeout(requestId);
		}
	}

	static async getData(signal) {
		const guacURL = "api/topology_data";
		const resposne = await fetch(guacURL, { signal });
		if (!resposne.ok) {
			return [null, RequestHandler.reqErrorMsg()];
		}
		const json = await resposne.json();
		if (!json || !json.nodes) {
			return [null, RequestHandler.jsonErrorMsg()];
		}
		return [json.nodes, null];
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

