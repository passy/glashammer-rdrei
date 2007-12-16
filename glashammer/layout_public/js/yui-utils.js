

function create_message(txt, type) {
    var messages = new YAHOO.util.Element("messages");
    var msg = document.createElement("div");
    msg.setAttribute('class', type);
    msg.innerHTML = txt + '<br />' + Date();
    messages.appendChild(msg);
    window.setTimeout(function() {
        YAHOO.widget.Effects.Fade(msg);
        }, 2000);
}


function build_request_handler(form_id, url) {
    function make_request() {
    var formObject = document.getElementById(form_id); 
    YAHOO.util.Connect.setForm(formObject, false);
    function handleSuccess(o) {
        var messages = new YAHOO.util.Element("messages");
        var res = eval("(" + o.responseText + ")");
        if (res.SUCCESS) {
            for (i in formObject.elements) {
                var el = formObject.elements[i];
                if (el.name) {
                    var err = document.getElementById(el.name + "_error");
                    if (err) {
                        err.innerHTML = "";
                    }
                }
            }
            create_message('Ok, saved', 'message');
        }
        else {
            for (field in res.ERRORS) {
                error_msg = document.getElementById(field + "_error");
                error_msg.innerHTML = res.ERRORS[field];
            }
            create_message('Errors, NOT saved', 'error');
        }
    }
    var callback =
    {
        success:handleSuccess,
        failure:handleSuccess
    };
    var request = YAHOO.util.Connect.asyncRequest('POST', url, callback);
    }
    return make_request;
}

function yui_submit_button(id, callback) {
    var _yui_button = new YAHOO.widget.Button(id);
    if (callback) {
        _yui_button.addListener("click", callback);
    }
}

function yui_tab_view(id) {
    var _yui_tabs = new YAHOO.widget.TabView(id);
    return _yui_tabs;
}


function _create_rte_simple_config() {
    return {
        handleSubmit: false,
        height: '300px',
        width: '600px',
        dompath: false, //Turns on the bar at the bottom
        animate: true, //Animates the opening, closing and moving of Editor windows
        toolbar: {
            collapse: false,
            titlebar: '',
            draggable: false,
            buttons: [
                { group: 'textstyle', label: 'Font Style',
                    buttons: [
                        { type: 'push', label: 'Bold CTRL + SHIFT + B', value: 'bold' },
                        { type: 'push', label: 'Italic CTRL + SHIFT + I', value: 'italic' },
                        { type: 'push', label: 'Underline CTRL + SHIFT + U', value: 'underline' },
                        { type: 'separator' },
                        { type: 'push', label: 'Remove Formatting', value: 'removeformat', disabled: true },
                    ]
                },
                { type: 'separator' },
                { group: 'alignment', label: 'Alignment',
                    buttons: [
                        { type: 'push', label: 'Align Left CTRL + SHIFT + [', value: 'justifyleft' },
                        { type: 'push', label: 'Align Center CTRL + SHIFT + |', value: 'justifycenter' },
                        { type: 'push', label: 'Align Right CTRL + SHIFT + ]', value: 'justifyright' },
                        { type: 'push', label: 'Justify', value: 'justifyfull' }
                    ]
                },
                { type: 'separator' },
                { group: 'parastyle', label: 'Paragraph Style',
                    buttons: [
                    { type: 'select', label: 'Normal', value: 'heading', disabled: true,
                        menu: [
                            { text: 'Normal', value: 'none', checked: true },
                            { text: 'Header 1', value: 'h2' },
                            { text: 'Header 2', value: 'h3' },
                            { text: 'Header 3', value: 'h4' },
                        ]
                    }
                    ]
                },
                { type: 'separator' },
                { group: 'indentlist', label: 'Lists',
                    buttons: [
                        { type: 'push', label: 'Create an Unordered List', value: 'insertunorderedlist' },
                        { type: 'push', label: 'Create an Ordered List', value: 'insertorderedlist' }
                    ]
                },
                { type: 'separator' },
                { group: 'insertitem', label: 'Insert Item',
                    buttons: [
                        { type: 'push', label: 'HTML Link CTRL + SHIFT + L', value: 'createlink', disabled: true },
                        { type: 'push', label: 'Insert Image', value: 'insertimage' }
                    ]
                }
            ]
        }
    }
};

function yui_basic_rte(id) {
    var _yui_editor = new YAHOO.widget.Editor(id, _create_rte_simple_config());
    _yui_editor.render();
    return _yui_editor;
}

