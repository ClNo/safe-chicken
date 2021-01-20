
class Connector {
    constructor(topic, topicKeys, inputSelectorList, textSelectorList) {
        this.topic = topic;
        this.topicKeys = topicKeys;
        this.inputSelectorList = inputSelectorList;
        this.textSelectorList = textSelectorList;
    }

    setSenderFunc(senderObj, senderFunc) {
        this.senderObj = senderObj;
        this.senderFunc = senderFunc;
    }

    getTopic() {
        return this.topic;
    }

    getTopicFullStr() {
        if (this.topicKeys) {
          return this.topic + ' keys: ' + this.topicKeys.join(', ');
        }
        return this.topic;
    }

    hasSelector(selector) {
        return (this.inputSelectorList.find(element => element === selector) ||
                this.textSelectorList.find(element => element === selector));
    }

    getSelectors() {
      return this.inputSelectorList.concat(this.textSelectorList);  // returns a new array
    }

    getIndexInInputList(selectorName) {
      let index = 0;
      for (let sel of this.inputSelectorList) {
        if (selectorName && sel.includes(selectorName)) {
          return index;
        }
        ++index;
      }
      return -1;
    }
}

class InputConnector extends Connector {
  constructor(topic, topicKeys, inputSelectorList, textSelectorList) {
      super(topic, topicKeys, inputSelectorList, textSelectorList);
  }

  initWebSide() {
    const thisClass = this;
    // Event listener for Slider value changes.
    for (let inputElem of this.inputSelectorList) {
      $(inputElem).on('input', function() {
        const newValue = $(this).val();

        const key = thisClass.topicKeys[thisClass.getIndexInInputList(this.id)];
        const payload = {}
        payload[key] = newValue;

        thisClass.senderFunc(thisClass.senderObj, thisClass.getTopic(), payload);
      });
      $(inputElem).on('change', function() {
        const newValue = $(this).val();

        const key = thisClass.topicKeys[thisClass.getIndexInInputList(this.id)];
        const payload = {}
        payload[key] = newValue;

        thisClass.senderFunc(thisClass.senderObj, thisClass.getTopic(), payload);
      });
    }
  }

  dataHostConnected(connected) {
    for (let inputElem of this.inputSelectorList) {
      $(inputElem).attr("disabled", connected ? null:true);
    }

    // unclear: also enable text/disable elements?
    for (let textElem of this.textSelectorList) {
      $(textElem).attr("disabled", connected ? null:true);
    }
  }

  valueArrived(data) {
    let index = 0;
    for (let key of this.topicKeys) {
      if(!data[key]) {
        continue;
      }

      const value = data[key];
      console.log('new value for key ', key, ':', value, ' -> ', this.inputSelectorList[index]);

      $(this.inputSelectorList[index]).val(value);
      if(index < this.textSelectorList.length) {
        $(this.textSelectorList[index]).html(value);
      }
      index++;
    }
  };
}


class SelectionConnector extends Connector {
  constructor(topic, topicKey, inputSelector, optionList) {
      super(topic, [topicKey], [inputSelector]);
      self.optionList = optionList;
  }

  initWebSide() {
    const thisClass = this;
    // Event listener for Slider value changes.
    for (let inputElem of this.inputSelectorList) {
      $(inputElem).on('click', function(event) {
        //console.log(event.currentTarget.name, ':', event.currentTarget.value);
        //$('input[name = "' + event.currentTarget.name + '"]').parent().removeClass('active').removeClass('btn-primary').removeClass('btn-secondary');
        //$('#' + event.currentTarget.id).parent().addClass('active').addClass('btn-primary');
        thisClass.updateVisualState(event.currentTarget.value);

        const key = thisClass.topicKeys[0];  // expecting exactly one topic key, more than one is currently not supported
        const payload = {}
        payload[key] = event.currentTarget.value;
        var dt = new Date();
        payload['started_isodt'] = dt.toISOString();
        thisClass.senderFunc(thisClass.senderObj, thisClass.getTopic(), payload);
      });
    }
  }

  updateVisualState(optionValue) {
    // first clear all options
    $(this.getSelectors()[0]).parent().removeClass('active').removeClass('btn-primary').addClass('btn-secondary');
    $(this.getSelectors()[0]).removeAttr('checked');

    // then select the activated option
    if(optionValue) {
      $(this.getSelectors()[0] + '[value = "' + optionValue + '"]').parent().addClass('active').removeClass('btn-secondary').addClass('btn-primary');
      $(this.getSelectors()[0] + '[value = "' + optionValue + '"]').attr('checked', true);
    }
  }

  dataHostConnected(connected) {
//    for (let inputElem of this.inputSelectorList) {
//      $(inputElem).attr("disabled", connected ? null:true);
//    }
//
//    // unclear: also enable text/disable elements?
//    for (let textElem of this.textSelectorList) {
//      $(textElem).attr("disabled", connected ? null:true);
//    }
  }

  valueArrived(data) {
    const key = this.topicKeys[0];  // expecting exactly one topic key, more than one is currently not supported
    const value = data[key];
    this.updateVisualState(value);
  };
}


class TextOutConnector extends Connector {
  constructor(topic, topicKeys, textSelectorList, dataFormatterList) {
      super(topic, topicKeys, [], textSelectorList);
      this.dataFormatterList = dataFormatterList;
  }

  initWebSide() {
    let initData = {};
    if (this.topicKeys) {
      for (let key of this.topicKeys) {
        initData[key] = undefined;
      }
    }
    this.valueArrived(initData);
  }

  dataHostConnected(connected) {
    // unclear: also enable text/disable elements?
    for (let textElem of this.textSelectorList) {
      $(textElem).attr("disabled", connected ? null:true);
    }
  }

  valueArrived(data) {
    if (!data) {
      return; // do nothing for empty data
    }

    // this is for passing just the complete data to the formatter; it can extract whatever it wants
    if(!this.topicKeys && this.dataFormatterList) {
        let dataFormatter = this.dataFormatterList[0];
        dataFormatter(this.textSelectorList[0], data);
        return;
    }

    let index = 0;
    for (let key of this.topicKeys) {
      // allow empty/undefined values
      //if(!data[key]) {
      //  continue;
      //}

      const value = data[key];
      console.log('new value for key ', key, ':', value, ' -> ', this.textSelectorList[index]);
      if(this.dataFormatterList && this.dataFormatterList[index]) {
        let dataFormatter = this.dataFormatterList[index];
        dataFormatter(this.textSelectorList[index], value);
      }
      else {
        $(this.textSelectorList[index]).html(value);
      }
      index++;
    }
  };
}


class TableOutConnector extends Connector {
  constructor(topic, topicKeys, textSelectorList) {
      super(topic, topicKeys, [], textSelectorList);
  }

  initWebSide() {
    $(this.textSelectorList[0]).bootstrapTable();
  }

  dataHostConnected(connected) {
    // unclear: also enable text/disable elements?
    for (let textElem of this.textSelectorList) {
      $(textElem).attr("disabled", connected ? null:true);
    }
  }

  valueArrived(data) {
    const tableData = data;
    console.log('new table data of length ', tableData.length, ' -> ', this.textSelectorList[0]);
    /*
    for (let row of data) {
      const value = data[key]
      console.log('new value for key ', key, ':', value, ' -> ', this.textSelectorList[index]);
      $(this.textSelectorList[index]).html(value);
      index++;
    }
    */
    $(this.textSelectorList[0]).bootstrapTable('load', tableData);
  };
}

export { Connector, InputConnector, SelectionConnector, TextOutConnector, TableOutConnector };
