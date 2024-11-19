


export const initGroupSelect = (tabContent, childConnections, userSelection) => {
  const $panel = createControlPanel(childConnections);
  tabContent.addContent($panel);

  const $checkboxGroup = $("<div>", { class: "checkbox-group" });
  const selectAllBox = `
    <div class="checkbox-item select-all" id="select-all">
      <i class="fa-regular fa-rectangle-xmark icon icon-deselected"></i>
      <label>Select All (<span id="selected-count">0</span>)</label>
    </div>
  `;
  $checkboxGroup.append(selectAllBox);

  createCheckboxes($checkboxGroup, childConnections);

  const childIds = childConnections.map((node) => node.identifier);
  const components = {
    filterBtns: $panel.find(".filter-btn"),
    selectAll: $checkboxGroup.find("#select-all"),
    selectedCount: $checkboxGroup.find("#selected-count"),
    checkboxes: $checkboxGroup.find(".checkbox-option"),
  };

  addCheckBoxEvents(userSelection, components, childIds);
  tabContent.addContent($checkboxGroup);
};

function addCheckBoxEvents(userSelection, components) {
  // cached jQueries of commonly updated components 
  const { filterBtns, selectedCount, selectAll, checkboxes } = components;

  const toggleIcon = ($icon, isSelected) => {
    $icon.stop(true, true).fadeOut(150, function () {
      if (isSelected) {
        $icon
          .removeClass("fa-rectangle-xmark icon-deselected")
          .addClass("fa-square-check icon-selected");
      } else {
        $icon
          .removeClass("fa-square-check icon-selected")
          .addClass("fa-rectangle-xmark icon-deselected");
      }
      $icon.fadeIn(150);
    });
  };

  let currentFilter = null;
  const filterConnections = (filter) => {
    checkboxes.removeClass("hidden");
    if (filter === 'all') {
      currentFilter = null;
      return;
    }
    if (filter === "active") {
      currentFilter = '[data-active="true"]';
    } else {
      currentFilter = '[data-active="false"]';
    }
    checkboxes.not(currentFilter).addClass("hidden");
  };

  const debugInfo = () => {
    console.log("Current Filter: ", currentFilter);
    console.log("Selected IDs: ", userSelection);
  };

  const updateSelectAll = () => {
    const $selectIcon = selectAll.find(".icon");
    const selectAllChecked = selectAll.hasClass("selected");
    const visibleItems = checkboxes.filter(':visible').length;
    const selectedVisible = checkboxes.filter('.selected:visible').length;

    const allSelected = (visibleItems > 0 && 
      selectedVisible === visibleItems
    );

    if (allSelected && !selectAllChecked) {
      selectAll.addClass("selected");
      toggleIcon($selectIcon, true);
    } else if (!allSelected && selectAllChecked) {
      selectAll.removeClass("selected");
      toggleIcon($selectIcon, false);
    }
  };

  const rebuildSelection = () => {
    userSelection.length = 0; // reset array
    checkboxes.filter(".selected").each(function () {
      userSelection.push(`${$(this).data("node-id")}`);
    });
  };

  checkboxes.click(function () {
    const $icon = $(this).find(".icon");
    const wasSelected = $icon.hasClass("icon-selected");
    $(this).toggleClass("selected");
    toggleIcon($icon, !wasSelected);
    rebuildSelection();
    updateSelectAll();
    selectedCount.text(userSelection.length);
    debugInfo();
  });

  selectAll.click(function () {
    const wasSelected = $(this).hasClass("selected");
    $(this).toggleClass("selected");
    toggleIcon($(this).find(".icon"), !wasSelected);
    const selection = checkboxes.filter(':visible');
    if (wasSelected) {
      selection.removeClass("selected");
    } else {
      selection.addClass("selected");
    }
    selection.each(function () {
      const $icon = $(this).find(".icon");
      toggleIcon($icon, !wasSelected);
    });

    rebuildSelection();
    updateSelectAll();
    selectedCount.text(userSelection.length);
    debugInfo();
  });

  filterBtns.click(function () {
    filterBtns.removeClass("active");
    $(this).addClass("active");
    filterConnections($(this).data("filter"));
    updateSelectAll();
  });
}

const createCheckboxes = ($checkboxGroup, childConnections) => {
  childConnections.forEach((connection) => {
    const checkbox = `
      <div class="checkbox-item checkbox-option" 
        data-node-id="${connection.identifier}" 
        data-active="${connection.isActive()}"
      >
        <i class="fa-regular fa-rectangle-xmark icon icon-deselected"></i>
        <label class="checkbox-label">
          ${connection.name} ${connection.getOsIcon()}
        </label>
      </div>
    `;
    $checkboxGroup.append(checkbox);
  });
};

const createControlPanel = (childNodes) => {
  const activeCount = childNodes.filter((node) => node.isActive()).length || 0;
  const inactiveCount = childNodes.length - activeCount;
  const $controlPanel = $("<div>", { class: "control-panel" }).html(`
    <div class="control-panel">
      <div class="counter"></div>
      <div class="filters">
        <button class="filter-btn active" data-filter="all">
          All (${childNodes.length}) <i class="fa-solid fa-users-rectangle"></i>
        </button>
        <button class="filter-btn" data-filter="active">
          Active (${activeCount}) <i class="fa-regular fa-eye"></i>
        </button>
        <button class="filter-btn" data-filter="inactive">
          Inactive (${inactiveCount}) <i class="fa-regular fa-eye-slash"></i>
        </button>
      </div>
      

    </div>
  `);
  return $controlPanel;
};






