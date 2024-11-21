

const appIcons = {
  checkbox: {
    on: 'fa-circle-check',
    off: 'fa-circle-xmark'
  },
  selectAll: {
    on: 'fa-hand-pointer',
    off: 'fa-arrow-pointer'
  },
  pagination: {
    left: 'fa-arrow-left',
    right: 'fa-arrow-right'
  },
  osIcons: {
    win: 'fa-brands fa-windows',
    linux: 'fa-brands fa-linux',
  },
  filterIcons: {
    all: 'fa-solid fa-users-rays',
    inactive: 'fa-solid fa-power-off',
    active: "fa-solid fa-signal",
  },
};

const demoSpecific = {
  coinFlip(heads, tails) {
    return Math.random() < 0.5 ? heads : tails;
  },
  createSampleData(amount) {
    const data = [];
    for (let i = 0; i < amount; i++) {
      data.push(
        demoSpecific.nodeFactory(i)
      );
    }
    return data;
  },
  nodeFactory(nodeI) {
    return {
      name: `Node ${nodeI + 1}`,
      active: demoSpecific.coinFlip(true, false),
      id: nodeI,
      os: demoSpecific.coinFlip('win', 'linux'),
      isActive() {
        return  this.active;
      },
      getOsIcon() {
        return appIcons.osIcons[this.os];
      }
    }
  }
};

const component = {
  checkbox: "modalCheckbox",
  filter: "filterTab",
  pager: "checkboxPager",
  container: "groupSelect",
};


const templateManager = {
  assets: {},
  cloneAsset(templateId) {
    if(!this.assets[templateId]) {
      this.registerAsset(templateId);  
    }
    return this.assets[templateId].clone();
  },
  registerAsset(templateId) {
    const template = document.getElementById(templateId);
    if(!template) {
      throw new Error(`Template with id ${templateId} not found`);
    }
    const cloned = template.content.cloneNode(true).children[0];
    this.assets[templateId] = $(cloned);
  }
};

const assetFactory = {
  assignCheckboxProps($checkbox, connection) {
    $checkbox
      .attr('data-node-id', connection.id) // change to identifier later
      .attr('data-active', connection.isActive())
      .find('.checkbox-label')
      .prepend(connection.name)
      .find('.node-os-icon')
      .addClass(connection.getOsIcon());
  },
  createCheckbox(connection) {
    const { name, id } = connection;
    const $checkbox = templateManager.cloneAsset(component.checkbox);
    console.log("checkbox: ",$checkbox )
    assetFactory.assignCheckboxProps($checkbox, connection);
    return $checkbox;
  },
  createFilter(filterConfig) {
    const { text, count, icon, dataFilter } = filterConfig;
    const $filter = templateManager.cloneAsset(component.filter);
    console.log("filter: ", $filter)
    $filter
      .attr('data-filter', dataFilter)
      .find('.filter-label')
      .prepend(`${text} (${count}) `)
      .find('.filter-icon')
      .addClass(icon);
    return $filter;
  },
};

const pageHandler = {
  renderPage($checkboxes, pageIndex, connections) {
    const start = pageIndex * assetManager.itemsPerPage;
    let iter = start;
    $checkboxes.fadeOut(200, function() {
      $checkboxes.each(function() {
        if(iter < connections.length) {
          $(this).empty();
          const connection = connections[iter];
          assetFactory.assignCheckboxProps($(this), connection);
          $(this).fadeIn(200);
        } else {
          $(this).hide();
        }
        iter++;
      });
    });
  }
};



const assetManager = {
  itemsPerPage: 20,
  currentPage: 0,  
  renderCheckboxes(connections, $assetHolder) {
    connections.forEach(connection => {
      const $checkbox = assetFactory.createCheckbox(connection);
      $assetHolder.append($checkbox);
    });
  },
  renderFilters(filterConfigs, $filterHolder) {
    filterConfigs.forEach(filterConfig => {
      const $filter = assetFactory.createFilter(filterConfig);
      if(filterConfig.text === 'All') {
        $filter.addClass('active');
      }
      $filterHolder.append($filter);
    });
  },
  renderAssets({ connections, filters }) {
    const $assetHolder = templateManager.cloneAsset(component.container);
    console.log("assetHolder: ", $assetHolder)
    
    const containers = {
      $filters: $assetHolder.find('.filters'),
      $checkbox: $assetHolder.find('.checkbox-container'),
      $pager: $assetHolder.find('.pagination-container'),
    };

    this.renderFilters(filters, containers.$filters);
    this.renderCheckboxes(connections, containers.$checkbox);
    return $assetHolder;
  }, 
};

const assetEvents = {
  checkboxClick($checkbox, selectedIds) {
    const nodeId = $checkbox.attr('data-node-id');
    const index = selectedIds.indexOf(nodeId);
    const wasSelected = index > -1;
    if(wasSelected) {
      selectedIds.splice(index, 1);
    } else {
      selectedIds.push(nodeId);
    }
    $checkbox
      .toggleClass("active", !wasSelected)
      .find('.checkbox-icon')
      .toggleClass(`${appIcons.checkbox.off} ${appIcons.checkbox.on}`);
    console.log("Selected IDs: ", selectedIds);
  },
  enableCheckbox($checkbox) {
    $checkbox
      .addClass('active')
      .find('.checkbox-icon')
      .removeClass(appIcons.checkbox.off)
      .addClass(appIcons.checkbox.on);
  },
  disableCheckbox($checkbox) {
    $checkbox
      .removeClass('active')
      .find('.checkbox-icon')
      .removeClass(appIcons.checkbox.on)
      .addClass(appIcons.checkbox.off);
  },
  filterClick($filter, $checkboxes) {
    const nodeFilter = $filter.attr('data-filter');
    $filter.addClass('active').siblings().removeClass('active');
    if(nodeFilter === 'all') {
      $checkboxes.fadeIn(300);
      return;
    }
    const selector = assetEvents.getFilterSelector(nodeFilter);
    if(!selector) {
      return;
    }
    $checkboxes.not(selector).fadeOut(200, function() {
      $checkboxes.filter(selector).fadeIn(200);
    });
  },

  getFilterSelector(nodeFilter) {
    switch(nodeFilter) {
      case 'active':
        return '[data-active="true"]';
      case 'inactive':
        return '[data-active="false"]';
      default: 
      case 'all':
        return null;
    }
  },
  updateCounter(selectedCount, nodes) {
    $('#selectedCounter').text(selectedCount);
    const $all = $('.select-all');
    let add, remove;
    if(selectedCount === nodes.length) {
      $all.addClass('active');
      remove = appIcons.selectAll.off;
      add = appIcons.selectAll.on;
    } else if ($all.hasClass('active')) {
      $all.removeClass('active');
      remove = appIcons.selectAll.on;
      add = appIcons.selectAll.off;
    } 
    if(add && remove) {
      $all
        .find('.select-all-icon')
        .removeClass(remove)
        .addClass(add);
    }
  },
  selectAllClick(selectedIds, $checkboxes, $selectAll) {
    const deselectAll = $selectAll.hasClass('active');
    if(deselectAll) {
      $checkboxes.each(function() {
        assetEvents.disableCheckbox($(this));
      });
      selectedIds.length = 0;
    } else {
      $checkboxes.each(function() {
        const nodeId = $(this).attr('data-node-id');
        if(!selectedIds.includes(nodeId)) {
          assetEvents.enableCheckbox($(this));
          selectedIds.push(nodeId);
        }
      });
    }
  },
};

const setupGroupSelect = (selectedIds, nodes) => {
  const selectedIds = [];
  // const nodes = demoSpecific.createSampleData(15);
  const activeCount = nodes.filter(n => n.isActive()).length || 0;
  const filterConfigs = [
    {
      text: "All",
      count: nodes.length,
      icon: appIcons.filterIcons.all,
      dataFilter: "all"
    },
    {
      text: "Inactive",
      count: nodes.length - activeCount,
      icon: appIcons.filterIcons.inactive,
      dataFilter: "inactive"
    },
    {
      text: "Active",
      count: activeCount,
      icon: appIcons.filterIcons.active,
      dataFilter: "active"
    }
  ];

  const $assetHolder = assetManager.renderAssets(
    { connections: nodes, filters: filterConfigs }
  );
  
  const shouldPage = connections.length > assetManager.itemsPerPage;
  if(shouldPage) {
    const $pager = templateManager.cloneAsset(component.pager);
    containers.$pager.append($pager);
  }

  $('body').append($assetHolder);
  const uiComps = {
    $checkboxes: $assetHolder.find('.checkbox'),
    $filters: $assetHolder.find('.filter-button'),
    $pager: $('.pagination'),
    $selectAll: $('.select-all'),
  };
  uiComps.$checkboxes.on('click', function() {
    assetEvents.checkboxClick($(this), selectedIds);
    assetEvents.updateCounter(selectedIds.length, nodes);
  });
  uiComps.$filters.on('click', function() {
    assetEvents.filterClick($(this), uiComps.$checkboxes);
  });
  uiComps.$selectAll.on('click', function() {
    assetEvents.selectAllClick(selectedIds, uiComps.$checkboxes, $(this));
    assetEvents.updateCounter(selectedIds.length, nodes);
  });
  // uiComps.$pager.find('.pager-icon').on("click", function() {
  //   const action = $(this).attr('data-action');
  //   if(action === 'left') {

  //   }


  // });
});