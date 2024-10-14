// static/js/data_source_entries.js

class DataSourceStatus {
  /**
   * @param {jQuery} $row - jQuery object of the row
   * @property {jQuery} $row - jQuery object of the row
   * @property {jQuery} $icon - jQuery object of the icon
   * @property {jQuery} $checkbox - jQuery object of the checkbox
   */
  constructor($row) {
    this.$row = $row;
    this.$icon = $row.find(".icon");
    this.$checkbox = $row.find(".datasource-checkbox");
  }

  toggleStatus() {
    this.$checkbox.prop("checked", !this.getStatus());
  }

  getStatus() { return this.$checkbox.prop("checked"); }

  toggleAppearance() {
    this.toggleStatus();
    if(this.getStatus()) {
      this.$row.removeClass("untoggled");
    }
    this.$icon.toggleClass("fa-check checked fa-times unchecked");
  }
  shake() {
    this.$icon.addClass("shake");
    setTimeout(() => {
      this.$icon.removeClass("shake");
    }, 1000);
  }
}

class DataSourceForm {
  /**
   * @param {jQuery} $row - jQuery object of the row
   * @param {string} sourceId - ID of the data source
   * @property {jQuery} $form - jQuery object of the form
   * @property {string} url - Form submission URL
   */
  constructor($row, sourceId) {
    this.$form = $row.find(`#form${sourceId}`);
    if (this.$form.length === 0) {
      throw new Error("Form not found");
    }
    this.url = this.$form.attr("action");
  }

  submit() {
    const formData = this.$form.serialize();
    return $.ajax({
      type: "POST",
      url: this.url,
      data: formData,
    });
  }
}

class DataSource {
  /**
   * @param {jQuery} $row - jQuery object of the data source row
   * @property {string} id - Data source ID
   * @property {DataSourceStatus} status - Status object
   * @property {DataSourceForm} form - Form object
   */
  constructor($row) {
    if ($row.length === 0) {
      throw new Error("Row not found");
    }
    this.id = $row.data("source");
    this.status = new DataSourceStatus($row);
    this.form = new DataSourceForm($row, this.id);
  }

  /** Toggles the data source status and submits the form */
  toggleDataSource() {
    this.form
      .submit()
      .then(ajaxSuccess.bind(this))
      .catch(ajaxError.bind(this));
  }
}

// Helper functions

/**
 * Initializes DataSource objects for all rows
 * @returns {DataSource[]} Array of initialized DataSource objects
 */
function initializeDataSources() {
  const dataSources = [];
  $(".data-source-entry").each(function () {
    dataSources.push(new DataSource($(this)));
  });
  return dataSources;
}

/**
 * Sets up click event listeners for icons
 * @param {DataSource[]} dataSources - Array of DataSource objects
 */
function setupEventListeners(dataSources) {
  $(".icon").click(function (event) {
    const $row = $(this).closest("tr");
    const dataSource = findDataSource(dataSources, $row);
    if (dataSource) {
      dataSource.toggleDataSource();
    }
  });

  setupCopyOnIconClick();
}

function findDataSource(dataSources, $row) {
  return dataSources.find((ds) => ds.id === $row.data("source"));
}


function resetIcons(dataSources, $toggledIcon) {
  dataSources.forEach((ds) => {
    if (!ds.status.$icon.is($toggledIcon)) {
      ds.status.toggleAppearance();
    }
  });
}

/**
 * Toggles the icon and checkbox state
 * @param {DataSource} dataSource - DataSource object to toggle
 */
function toggleIcon(dataSource) {
  dataSource.status.toggleAppearance();
}

/** Sets up click event listener for copying URL */
function setupCopyOnIconClick() {
  $(".url-icon").on("click", function () {
    navigator.clipboard.writeText($(this).data("url"));
  });
}

function ajaxSuccess(response) {
  if (response.success) {
    resetIcons(window.dataSources, this.status.$icon);
    toggleIcon(this);
  } else {
    console.error("Update failed: ", response.error);
    this.status.shake();
  }
}

function ajaxError() {
  console.error("Error updating");
  this.status.shake();
}

$(function () {
  window.dataSources = initializeDataSources();
  setupEventListeners(window.dataSources);
});
