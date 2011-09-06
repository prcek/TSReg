
        function log() {
                var args = (arguments.length > 1) ? Array.prototype.join.call(arguments, " ") : arguments[0];
                try { 
                    console.log(args);
                return true;
                } catch(e) {  
    
                }
                return false;
        }

        function err() {
                var args = (arguments.length > 1) ? Array.prototype.join.call(arguments, " ") : arguments[0];
                try { 
                    console.error(args);
                return true;
                } catch(e) {  
    
                }
                return false;
        }



        TOOLS = {}


        TOOLS.stopEvent = function(e) {
            var e = e || window.event;
            if (e.stopPropagation){
                e.stopPropagation();
            } else { 
                e.cancelBubble = true;
            }
        }


        TOOLS.cancelDef = function(e) {
            var e = e || window.event;
            if(e.preventDefault) {
                e.preventDefault();
            } else {
                e.returnValue = false;
            }
        }


        TOOLS._getMethod = function(obj,func,elm){
            if (typeof(func) == "string") {
                return function(e){return obj[func].apply(obj,[e,elm])};
            } else {
                return function(e){return func.apply(obj,[e,elm])};
            }
        }


        TOOLS._addListener = function (elm,eType,func) {
            if (document.addEventListener) {
                if (window.opera && (elm == window)){
                    elm = document;
                }
                elm.addEventListener(eType,func,false);
            } else if (document.attachEvent) {
                elm.attachEvent('on'+eType,func);
            }
            
        }


        TOOLS.addListener = function(elm, eType, obj, func) {
            if (typeof(obj) == "function"){ 
                log('addListener fce mode');
                TOOLS._addListener(elm,eType,obj)
            } else if (typeof(obj) == "object") {
                log('addListener obj.fce mode');
               
                if (typeof(obj[func]) == "function") {
                    method = TOOLS._getMethod(obj,func,elm);
                    TOOLS._addListener(elm,eType,method);            
                } else {
                    log('addListener obj.fce error'); 
                }
            } else {
                log('addListener error');
            }
        }

        TOOLS.gEl = function(ids){
            if (typeof(ids) == "string") {
                return document.getElementById(ids);
            } else { return ids; }
        }


        TOOLS.getElementsByClass = function (searchClass,node,tag) {
            var classElements = [];
            var node = node || document;
            var tag = tag || "*";

            var els = node.getElementsByTagName(tag);
            var elsLen = els.length;
        
            var pattern = new RegExp("(^|\\s)"+searchClass+"(\\s|$)");
            for (var i = 0, j = 0; i < elsLen; i++) {
                    if (pattern.test(els[i].className)) {
                            classElements[j] = els[i];
                            j++;
                    }
            }
            return classElements;
        }
        TOOLS.setupConfirm = function (confirmClass, confirmFce) {
            var hrefs = TOOLS.getElementsByClass(confirmClass,null);
            for(var i = 0; i < hrefs.length; i++) {
                TOOLS.addListener(hrefs[i],"click",confirmFce);
            } 
        }
       
        TOOLS.confirmDel = function (e, elm) {
            if (!confirm("Opravdu smazat?")) {
               TOOLS.cancelDef(e);
               TOOLS.stopEvent(e);
            }
        }
        TOOLS.confirmKick = function (e, elm) {
            if (!confirm("Opravdu vyřadit/odmítnout?")) {
               TOOLS.cancelDef(e);
               TOOLS.stopEvent(e);
            }
        }
/*
        TOOLS.selectAll = function (e, elm) {
            var selects = TOOLS.getElementsByClass('check-action', null, 'input'); 
            var me = TOOLS.gEl('select-all')
            checked = me.checked;

            for(var i = 0; i < selects.length; i++) {
                if (selects[i].disabled == false) {
                    selects[i].checked = checked;
                }
            }
            
        }
*/

        TOOLS.selector = function(mark,slave) {
            log('new selector for mark =', mark)
            this.mark = mark;
            this.slave = slave;

            if (TOOLS.gEl(mark)) {
                TOOLS.addListener(TOOLS.gEl(mark), 'click', this, '_select');
            } else {
                err('mark not found!');
            }
        }


        TOOLS.selector.prototype._select = function() {
            log('selector._select function - mark ', this.mark);
            log('selector._select function - slave ', this.slave);

            var me = TOOLS.gEl(this.mark);
            checked = me.checked; 
            log('me.checked = ',checked)

            var selects = TOOLS.getElementsByClass('check-action', null, 'input'); 
             for(var i = 0; i < selects.length; i++) {
                log('select ', selects[i], ' ' , selects[i].id);
                if ((selects[i].disabled == false) && (selects[i].id == this.slave)) {
                    selects[i].checked = checked;
                    log('ap');
                } 
            }
            
        }

        TOOLS.bindSelect = function (mark, slave) {
            s1  = new TOOLS.selector(mark,slave);
        }



