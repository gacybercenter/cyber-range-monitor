// Jobs collapsible button
var isCollapsed = true;
function toggleTable(target) {
  console.log('Toggling table for target:', target);
  var table = document.getElementById('table-' + target);
  var rows = table.querySelectorAll('tr');
  rows.forEach(function(row, index) {
    if (index > 1) {
        if (!isCollapsed) {
          row.style.display = 'none';
        } else {
          row.style.display = 'table-row';
        }
      }
  });
  isCollapsed = !isCollapsed;
}
function toggleCollapse() {
  var tables = document.querySelectorAll('.table');
  tables.forEach(function(table) {
    var rows = table.querySelectorAll('tr');
    rows.forEach(function(row, index) {
      if (index > 1) {
        if (!isCollapsed) {
          row.style.display = 'none';
        } else {
          row.style.display = 'table-row';
        }
      }
    });
  });
  isCollapsed = !isCollapsed;
  document.getElementById('collapse-button').textContent = isCollapsed ? "Expand All" : "Collapse All";
}

// Dropdown button in menu 
function toggleDropdown(button) {
  const dropdown = button.parentElement;
  dropdown.classList.toggle('open');
}
document.addEventListener('click', function (event) {
  const dropdowns = document.querySelectorAll('.dropdown');
  dropdowns.forEach(dropdown => {
      if (!dropdown.contains(event.target)) {
          dropdown.classList.remove('open');
      }
  });
});

