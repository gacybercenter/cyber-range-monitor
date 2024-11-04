import { Modal, ModalHTML } from "./modal.js";
import {
  SampleData,
  ConnectionNode,
  ContextHandler,
  NodeWeight,
} from "./sample-api.js";

function parseSampleData() {
  const connections = SampleData.nodes;
  const context = ContextHandler.getContext();
  return context;
}

function leafConnectionModal(connection) {
  const generalTabContent = generalTab(connection);
  const controlsTabContent = controlsTab(connection);
  return [generalTabContent, controlsTabContent];
}

function generalTab(connection) {
  const tabContext = {
    tabId: "nodeGeneral",
    title: "General",
    fasIcon: "fa-solid fa-circle-info",
  };
  const tabContent = generalTabContent(connection);
  return { tabContext, tabContent };
}

function initControlsHTML() {
  const makeControlBtn = (label, icon, cssClass) => {
    return $("<button>")
      .addClass("control-btn" + cssClass)
      .attr("aria-label", label).html(`
				<i class="icon fas ${icon}"></i>	
				${label}
			`);
  };
  return {
    connect: makeControlBtn("Connect To", "fa-plug", "btn-connect"),
    kill: makeControlBtn("Kill Connection", "fa-smile", "btn-kill"),
    timeline: makeControlBtn("View Timeline", "fa-chart-line", "btn-timeline"),
  };
}

/**
 * @param {Map<string, ConnectionNode>} nodeMap
 * @param {ConnectionNode} connection
 */

function generalTabContent(connection, nodeMap) {
  const fields = [
    ModalHTML.createField({
      title: "Connection Name",
      value: connection.name,
    }),
    ModalHTML.createField({
      title: "Node Identifier",
      value: connection.identifier,
    }),
  ];
  let parent = nodeMap.get(connection.parentIdentifier);
  if (parent) {
    fields.push(
      ModalHTML.createField({
        title: "Parent Connection",
        value: parent.name,
      }),
      ModalHTML.createField({
        title: "Parent Identifier",
        value: connection.parentIdentifier,
      })
    );
  }
  const activeConnections = connection.dump.activeConnections;
  let status;
  if (!activeConnections || activeConnections < 0) {
    status = "Offline";
  } else {
    status = "Online";
  }
  const getLastActive = () => {
    if (connection.dump.lastActive) {
      const lastActive = new Date(connection.dump.lastActive);
      return lastActive.toUTCString();
    }
    return "Not available";
  };

  const connectionFields = [
    {
      title: "Active Connections",
      value: connection.dump.activeConnections,
    },
    {
      title: "Connection Status",
      value: status,
    },
    {
      title: "Protocol",
      value: connection.dump.protocol,
    },
    {
      title: "Last Active",
      value: getLastActive(),
    },
  ];
  ModalHTML.createCollapsible(connectionFields);
  const connProps = initConnectionProperties(connection);
  const sharingProfile = initSharingProfile(connection, nodeMap);
  fields.push(
    ModalHTML.createCollapsible("Connection Properties", connProps),
    ModalHTML.createCollapsible("Sharing Profile", sharingProfile)
  );
  return fields;
}

const initConnectionProperties = (connection) => {
  const attributes = connection.attributes;
  if (!attributes || attributes.length === 0) {
    return ModalHTML.createField({
      title: "Connection Properties",
      value: "No attributes have been set for this connection",
    });
  }
  return attributes.map((attribute) => {
    return {
      title: attribute.name,
      value: attribute.value ?? "Not set",
    };
  });
};

const initSharingProfile = (connection) => {
  const sharingProfile = connection.sharingProfile;
  if (!sharingProfile || sharingProfile.length === 0) {
    return ModalHTML.createField({
      title: "Sharing Profile",
      value: "No attributes have been set for this connection",
    });
  }
  return sharingProfile.map((attribute) => {
    return {
      title: attribute.name,
      value: attribute.value ?? "Not set",
    };
  });
};
