
const initTemplate = (templateId) => {
  const template = document.getElementById(templateId);
  const cloned = template.content.cloneNode(true).children[0];
  return $(cloned);
};

const templateManager = {
  toggler: initTemplate("toggler"),
  subOption: initTemplate("sub-option"),
  modalCheckbox: initTemplate("modalCheckbox"),
};

// const selectors = {
//   unchecked: "fa-regular fa-rectangle-xmark icon icon-deselected",
//   checked: "fa-square-check icon-selected",
// }


/* 
<div class="checkbox-item checkbox-option" 
  data-node-id="${connection.identifier}" 
  data-active="${connection.isActive()}"
>
  <i class="fa-regular fa-rectangle-xmark icon icon-deselected"></i>
  <label class="checkbox-label">
    ${connection.name} ${connection.getOsIcon()}
  </label>
</div>
*/




/**
 * toggler options
 * {
    text: "Enable Paragraph",
    icons: {
      onIcon: "fa-solid fa-play",
      offIcon: "fa-solid fa-pause",
    },
    activeClass: "active",
    inactiveClass: "inactive",
  }
 */
export class Toggler {
  constructor(options, flag) {
    this.$tag = templateManager.toggler.clone();
    this.$icon = this.$tag.find(".toggler-icon");
    this.$text = this.$tag.find(".toggler-text");
    this.options = options;
    this.changeText(options.text);
    this.toggle(flag);
  }
  toggle(flag) {
    if (flag) {
      this.enable();
    } else {
      this.disable();
    }
  }
  enable() {
    this.$tag
      .removeClass(this.options.inactiveClass)
      .addClass(this.options.activeClass);
    this.$icon
      .removeClass(this.options.icons.offIcon)
      .addClass(this.options.icons.onIcon);
  }
  disable() {
    this.$tag
      .removeClass(this.options.activeClass)
      .addClass(this.options.inactiveClass);
    this.$icon
      .removeClass(this.options.icons.onIcon)
      .addClass(this.options.icons.offIcon);
  }
  get button() {
    return this.$tag;
  }
  changeText(text) {
    this.$text.text(text);
  }
}
/* 
  checkbox options 
  {
    text: [str],
    valueText: [str],
    dataField: [str], (e.g "speed" would be "data-speed")
    dataValue: [str]
  }
*/
export class Checkbox {
  constructor(options) {
    this.$tag = templateManager.subOption.clone();
    this.$icon = this.$tag.find(".sub-icon");
    this.$text = this.$tag.find(".option-text");
    this.$val = this.$tag.find(".option-val");
    this.id = options.id;
    this.options = options;
    this.init();
  }
  init() {
    const { dataField, dataValue } = this.options;
    this.$tag
      .data(dataField, dataValue)
      .attr("id", this.id);
    this.$text.text(this.options.text);
    this.$val.text(this.options.valueText);
    this.uncheck();
    /*
      
    */
  }
  toggle(flag = null) {
    if (!flag) {
      flag = this.$tag.hasClass("selected");
    }
    if (this.$tag.hasClass("selected")) {
      this.uncheck();
    } else {
      this.check();
    }
  }
  check() {
    this.$tag.addClass("selected");
    this.$icon
      .removeClass("far fa-square")
      .addClass("fas fa-check-square");
  }
  uncheck() {
    this.$tag.removeClass("selected");
    this.$icon
      .removeClass("fas fa-check-square")
      .addClass("far fa-square");
  }
  isChecked() {
    return this.$tag.hasClass("selected");
  }
}


