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
  static async fetchGuacAPI(timeoutMs = 5000) {
    const guacURL = "api/topology_data";
    const controller = new AbortController();
    const { signal } = controller;

    const requestId = setTimeout(() => { controller.abort(); }, timeoutMs);

    const response = await fetch(guacURL, { signal }).catch((error) => {
      clearTimeout(requestId);
      RequestHandler.getError(error, RequestHandler.reqErrorMsg(error));
    });

    const data = await response.json().catch((error) => {
      clearTimeout(requestId);
      RequestHandler.getError(error, RequestHandler.jsonErrorMsg(error));
    });
    clearTimeout(requestId);
    if (!data) {
			throw new TopologyError("DATA_ERROR: The response from the Guacamole API was empty.");
		}
		if (!data.nodes) {
			throw new TopologyError(
				"BAD_DATA_ERROR: The response from the Guacamole API did not return any nodes."
			);
		}
    return data.nodes;
  }

  /**
   * @param {Error} errorObj
   * @param {string} errorMsg
   */
  static getError(errorObj, errorMsg) {
    if (errorObj.name === "AbortError") {
      throw new RequestTimeoutError(
        "The request to the Guacamole API timed out, please try again."
      );
    } else {
      throw new TopologyError(errorMsg);
    }
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
